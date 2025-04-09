"""
Service de chaîne d'auto-amélioration pour les descriptions de produits.
Utilise LangChain pour créer une série de prompts qui permettent à l'IA de s'auto-évaluer et d'améliorer ses générations.
"""
import logging
import os
import traceback
import json
from typing import Dict, Any, List, Optional

from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.chains.transform import TransformChain
from langchain_openai import ChatOpenAI
from langchain.output_parsers import ResponseSchema
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from .prompt_manager import PromptManager

# Configuration du logging
logger = logging.getLogger(__name__)

class EvaluationOutput(BaseModel):
    """Modèle pour la sortie de l'évaluation."""
    technical_accuracy: int = Field(description="Note de précision technique sur 10")
    tone_style: int = Field(description="Note de ton et style sur 10")
    seo_optimization: int = Field(description="Note d'optimisation SEO sur 10")
    structure: int = Field(description="Note de structure sur 10")
    persuasion: int = Field(description="Note de persuasion sur 10")
    differentiation: int = Field(description="Note de différenciation sur 10")
    technical_accuracy_justification: str = Field(description="Justification de la note de précision technique")
    tone_style_justification: str = Field(description="Justification de la note de ton et style")
    seo_optimization_justification: str = Field(description="Justification de la note d'optimisation SEO")
    structure_justification: str = Field(description="Justification de la note de structure")
    persuasion_justification: str = Field(description="Justification de la note de persuasion")
    differentiation_justification: str = Field(description="Justification de la note de différenciation")
    improvement_points: List[str] = Field(description="Points à améliorer par ordre de priorité")

class SelfImprovingChain:
    """
    Chaîne d'auto-amélioration pour les descriptions de produits.
    Utilise une série de prompts pour générer, évaluer et améliorer les descriptions.
    """
    
    def __init__(self, openai_api_key: str):
        """
        Initialise la chaîne d'auto-amélioration.
        
        Args:
            openai_api_key: Clé API OpenAI
        """
        logger.debug("Initialisation de SelfImprovingChain")
        
        self.openai_api_key = openai_api_key
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            openai_api_key=self.openai_api_key
        )
        
        # Initialisation du gestionnaire de prompts
        self.prompt_manager = PromptManager()
        
        # Initialisation des parsers
        self.str_parser = StrOutputParser()
        self.evaluation_parser = PydanticOutputParser(pydantic_object=EvaluationOutput)
        
        # Récupération des prompts personnalisés
        self._initialize_prompts()
        
        # Création des chaînes individuelles
        self._create_chains()
        
        # Création de la chaîne séquentielle complète
        self._create_sequential_chain()
        
        logger.debug("SelfImprovingChain initialisé avec succès")
    
    def _initialize_prompts(self):
        """
        Initialise les prompts pour chaque étape de la chaîne.
        """
        # Prompt de génération
        generation_prompt_data = self.prompt_manager.get_prompt("self_improvement_generation")
        if generation_prompt_data:
            self.generation_template = generation_prompt_data["template"]
        else:
            logger.warning("Prompt de génération non trouvé, utilisation du prompt par défaut")
            self.generation_template = """
            Tu es un expert en rédaction de fiches produit optimisées pour le marketing et le SEO.
            
            TÂCHE:
            Génère une description de produit professionnelle pour {product_name} basée sur les informations suivantes.
            
            INFORMATIONS PRODUIT:
            - Description: {product_description}
            - Catégorie: {product_category}
            - Mots-clés: {product_keywords}
            
            SPÉCIFICATIONS TECHNIQUES:
            {technical_specs}
            
            TON ÉDITORIAL:
            {tone_instructions}
            
            PERSONA CIBLE:
            {persona_instructions}
            
            OPTIMISATION SEO:
            - Optimisation demandée: {seo_optimization}
            - Mots-clés à intégrer: {seo_keywords}
            
            INFORMATIONS CONCURRENTIELLES:
            {competitor_insights}
            
            GUIDE SEO:
            {seo_guide_info}
            
            INSTRUCTIONS SUPPLÉMENTAIRES:
            - Crée une description complète et persuasive
            - Mets en avant les avantages et caractéristiques clés
            - Utilise des sous-titres pour structurer le contenu
            - Intègre naturellement les mots-clés SEO
            - Adapte le ton à la marque et au public cible
            
            DESCRIPTION DE PRODUIT:
            """
        
        # Prompt d'évaluation
        evaluation_prompt_data = self.prompt_manager.get_prompt("self_improvement_evaluation")
        if evaluation_prompt_data:
            self.evaluation_template = evaluation_prompt_data["template"]
        else:
            logger.warning("Prompt d'évaluation non trouvé, utilisation du prompt par défaut")
            self.evaluation_template = """
            Tu es un expert en marketing, copywriting et SEO. Évalue la description de produit suivante selon des critères précis.
            
            DESCRIPTION DE PRODUIT À ÉVALUER:
            {generated_description}
            
            INFORMATIONS CONTEXTUELLES:
            - Nom du produit: {product_name}
            - Catégorie: {product_category}
            - Ton souhaité: {tone_summary}
            - Mots-clés SEO à intégrer: {seo_keywords}
            
            CRITÈRES D'ÉVALUATION:
            Évalue la description sur une échelle de 1 à 10 pour chacun des critères suivants:
            
            1. Précision technique: Les caractéristiques sont-elles correctement présentées?
            2. Ton et style: Le texte respecte-t-il le ton demandé?
            3. Optimisation SEO: Les mots-clés sont-ils intégrés naturellement?
            4. Structure: La structure est-elle claire et efficace?
            5. Persuasion: Le texte est-il convaincant pour l'acheteur potentiel?
            6. Différenciation: Le produit se distingue-t-il de la concurrence?
            
            Pour chaque critère, donne une note et une justification détaillée.
            Identifie également les 3 principaux points à améliorer, classés par ordre de priorité.
            
            {format_instructions}
            """
        
        # Prompt d'amélioration
        improvement_prompt_data = self.prompt_manager.get_prompt("self_improvement_improvement")
        if improvement_prompt_data:
            self.improvement_template = improvement_prompt_data["template"]
        else:
            logger.warning("Prompt d'amélioration non trouvé, utilisation du prompt par défaut")
            self.improvement_template = """
            Tu es un rédacteur expert en marketing et SEO. Améliore la description de produit suivante en te basant sur l'évaluation fournie.
            
            DESCRIPTION ORIGINALE:
            {generated_description}
            
            ÉVALUATION DÉTAILLÉE:
            {evaluation_summary}
            
            POINTS À AMÉLIORER (par ordre de priorité):
            {improvement_points}
            
            CONTEXTE PRODUIT:
            - Nom du produit: {product_name}
            - Catégorie: {product_category}
            - Ton souhaité: {tone_summary}
            - Mots-clés SEO à intégrer: {seo_keywords}
            
            CONSIGNES:
            1. Génère une nouvelle version améliorée qui corrige les faiblesses identifiées
            2. Conserve les points forts de la version originale
            3. Concentre-toi particulièrement sur les critères ayant reçu les notes les plus basses
            4. Assure-toi que tous les mots-clés SEO sont intégrés naturellement
            5. Respecte le ton et le style demandés
            
            DESCRIPTION AMÉLIORÉE:
            """
        
        # Prompt de vérification
        verification_prompt_data = self.prompt_manager.get_prompt("self_improvement_verification")
        if verification_prompt_data:
            self.verification_template = verification_prompt_data["template"]
        else:
            logger.warning("Prompt de vérification non trouvé, utilisation du prompt par défaut")
            self.verification_template = """
            Compare les deux versions de la description de produit et vérifie que les améliorations ont bien été apportées.
            
            VERSION ORIGINALE:
            {generated_description}
            
            VERSION AMÉLIORÉE:
            {improved_description}
            
            POINTS À AMÉLIORER IDENTIFIÉS:
            {improvement_points}
            
            VÉRIFICATION:
            1. Tous les points à améliorer ont-ils été traités? Explique comment.
            2. Y a-t-il des informations importantes qui ont été perdues? Si oui, lesquelles?
            3. Le ton et le style sont-ils cohérents avec la demande initiale?
            4. Les mots-clés SEO sont-ils toujours présents et bien intégrés?
            5. La version améliorée est-elle globalement meilleure que l'originale? Pourquoi?
            
            Si des problèmes persistent, identifie-les précisément.
            
            RÉSUMÉ DES AMÉLIORATIONS:
            """
        
        # Création des prompts
        self.generation_prompt = ChatPromptTemplate.from_template(self.generation_template)
        
        format_instructions = self.evaluation_parser.get_format_instructions()
        self.evaluation_prompt = ChatPromptTemplate.from_template(
            self.evaluation_template
        ).partial(format_instructions=format_instructions)
        
        self.improvement_prompt = ChatPromptTemplate.from_template(self.improvement_template)
        self.verification_prompt = ChatPromptTemplate.from_template(self.verification_template)
        
    def _create_chains(self):
        """Crée les chaînes individuelles pour chaque étape."""
        logger.debug("Création des chaînes individuelles")
        
        # Chaîne de génération
        self.generation_chain = LLMChain(
            llm=self.llm,
            prompt=self.generation_prompt,
            output_key="generated_description"
        )
        
        # Chaîne d'évaluation
        self.evaluation_chain = LLMChain(
            llm=self.llm,
            prompt=self.evaluation_prompt,
            output_key="evaluation_result"
        )
        
        # Fonction de transformation pour extraire les points d'amélioration
        def extract_evaluation_data(inputs: Dict[str, Any]) -> Dict[str, Any]:
            try:
                evaluation_result = inputs["evaluation_result"]
                
                # Parsing du résultat de l'évaluation
                parsed_evaluation = self.evaluation_parser.parse(evaluation_result)
                
                # Extraction des notes et justifications
                evaluation_summary = "ÉVALUATION:\n"
                for criterion in ["technical_accuracy", "tone_style", "seo_optimization", 
                                 "structure", "persuasion", "differentiation"]:
                    if criterion in parsed_evaluation:
                        evaluation_summary += f"- {criterion.replace('_', ' ').title()}: {parsed_evaluation[criterion]}/10\n"
                
                if "justifications" in parsed_evaluation:
                    evaluation_summary += "\nJUSTIFICATIONS:\n"
                    evaluation_summary += parsed_evaluation["justifications"]
                
                # Extraction des points d'amélioration
                improvement_points = ""
                if "improvement_points" in parsed_evaluation:
                    improvement_points = parsed_evaluation["improvement_points"]
                
                return {
                    "evaluation_summary": evaluation_summary,
                    "improvement_points": improvement_points
                }
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction des données d'évaluation: {str(e)}")
                logger.error(traceback.format_exc())
                return {
                    "evaluation_summary": "Erreur lors de l'analyse de l'évaluation.",
                    "improvement_points": "1. Améliorer la structure\n2. Intégrer plus de mots-clés\n3. Renforcer l'argumentation"
                }
        
        self.extraction_chain = TransformChain(
            transform=extract_evaluation_data,
            input_variables=["evaluation_result"],
            output_variables=["evaluation_summary", "improvement_points"]
        )
        
        # Chaîne d'amélioration
        self.improvement_chain = LLMChain(
            llm=self.llm,
            prompt=self.improvement_prompt,
            output_key="improved_description"
        )
        
        # Chaîne de vérification
        self.verification_chain = LLMChain(
            llm=self.llm,
            prompt=self.verification_prompt,
            output_key="verification_result"
        )
        
        logger.debug("Chaînes individuelles créées avec succès")
    
    def _create_sequential_chain(self):
        """Crée la chaîne séquentielle complète."""
        logger.debug("Création de la chaîne séquentielle")
        
        self.chain = SequentialChain(
            chains=[
                self.generation_chain,
                self.evaluation_chain,
                self.extraction_chain,
                self.improvement_chain,
                self.verification_chain
            ],
            input_variables=[
                "product_name", 
                "product_description", 
                "product_category",
                "product_keywords",
                "technical_specs", 
                "tone_instructions", 
                "persona_instructions",
                "tone_summary",
                "seo_optimization",
                "seo_keywords",
                "competitor_insights",
                "seo_guide_info",
                "format_instructions"
            ],
            output_variables=[
                "generated_description", 
                "evaluation_result", 
                "evaluation_summary", 
                "improvement_points", 
                "improved_description", 
                "verification_result"
            ]
        )
        
        logger.debug("Chaîne séquentielle créée avec succès")
    
    def _format_technical_specs(self, technical_specs: Dict[str, Any]) -> str:
        """
        Formate les spécifications techniques pour le prompt.
        
        Args:
            technical_specs: Spécifications techniques du produit
            
        Returns:
            str: Spécifications techniques formatées
        """
        if not technical_specs:
            return "Aucune spécification technique fournie."
        
        formatted_specs = []
        for key, value in technical_specs.items():
            formatted_specs.append(f"- {key}: {value}")
        
        return "\n".join(formatted_specs)
    
    def _format_competitor_insights(self, competitor_insights: Dict[str, Any]) -> str:
        """
        Formate les insights concurrentiels pour le prompt.
        
        Args:
            competitor_insights: Insights concurrentiels
            
        Returns:
            str: Insights concurrentiels formatés
        """
        if not competitor_insights:
            return "Aucune information concurrentielle disponible."
        
        formatted_insights = []
        
        if "key_features" in competitor_insights:
            formatted_insights.append("CARACTÉRISTIQUES CLÉS MENTIONNÉES PAR LES CONCURRENTS:")
            for feature in competitor_insights["key_features"]:
                formatted_insights.append(f"- {feature}")
            formatted_insights.append("")
        
        if "unique_selling_points" in competitor_insights:
            formatted_insights.append("ARGUMENTS DE VENTE UNIQUES DES CONCURRENTS:")
            for usp in competitor_insights["unique_selling_points"]:
                formatted_insights.append(f"- {usp}")
            formatted_insights.append("")
        
        if "common_technical_specs" in competitor_insights:
            formatted_insights.append("SPÉCIFICATIONS TECHNIQUES COMMUNES:")
            for spec in competitor_insights["common_technical_specs"]:
                formatted_insights.append(f"- {spec}")
            formatted_insights.append("")
        
        if "content_structure" in competitor_insights:
            formatted_insights.append("STRUCTURE DE CONTENU EFFICACE:")
            formatted_insights.append(competitor_insights["content_structure"])
            formatted_insights.append("")
        
        if "seo_keywords" in competitor_insights:
            formatted_insights.append("MOTS-CLÉS SEO IDENTIFIÉS:")
            for keyword in competitor_insights["seo_keywords"]:
                formatted_insights.append(f"- {keyword}")
        
        return "\n".join(formatted_insights)
    
    def _format_seo_guide_insights(self, seo_guide: Dict[str, Any]) -> str:
        """
        Formate les insights du guide SEO pour le prompt.
        
        Args:
            seo_guide: Guide SEO
            
        Returns:
            str: Insights du guide SEO formatés
        """
        if not seo_guide:
            return "Aucun guide SEO disponible."
        
        formatted_insights = []
        
        if "required_keywords" in seo_guide:
            formatted_insights.append("MOTS-CLÉS OBLIGATOIRES À INCLURE:")
            for keyword in seo_guide["required_keywords"]:
                formatted_insights.append(f"- {keyword}")
            formatted_insights.append("")
        
        if "recommended_phrases" in seo_guide:
            formatted_insights.append("EXPRESSIONS RECOMMANDÉES:")
            for phrase in seo_guide["recommended_phrases"]:
                formatted_insights.append(f"- {phrase}")
            formatted_insights.append("")
        
        if "questions_to_answer" in seo_guide:
            formatted_insights.append("QUESTIONS À ABORDER:")
            for question in seo_guide["questions_to_answer"]:
                formatted_insights.append(f"- {question}")
            formatted_insights.append("")
        
        if "content_recommendations" in seo_guide:
            formatted_insights.append("RECOMMANDATIONS DE CONTENU:")
            for rec in seo_guide["content_recommendations"]:
                formatted_insights.append(f"- {rec}")
        
        return "\n".join(formatted_insights)
    
    def _format_tone_instructions(self, tone_style: Dict[str, Any]) -> str:
        """
        Formate les instructions de ton pour le prompt de génération.
        
        Args:
            tone_style: Dictionnaire contenant les informations de ton
            
        Returns:
            str: Instructions de ton formatées
        """
        # Si tone_style est une chaîne, utiliser directement
        if isinstance(tone_style, str):
            tone = tone_style
        # Sinon, extraire la description du ton du dictionnaire
        else:
            # Utiliser tone_description ou brand_name comme indicateur de ton
            tone = tone_style.get("tone_description", "")
            if not tone and "brand_name" in tone_style:
                return f"Adapte le ton à la marque {tone_style['brand_name']} et à la nature du produit."
        
        # Mapping des tons
        tone_mapping = {
            "professional": "Utilise un ton professionnel et formel. Évite le jargon excessif mais reste technique et précis.",
            "casual": "Utilise un ton décontracté et conversationnel. Sois amical et accessible, comme si tu parlais à un ami.",
            "enthusiastic": "Utilise un ton enthousiaste et énergique. Montre de l'excitation pour le produit avec un langage dynamique.",
            "luxury": "Utilise un ton luxueux et exclusif. Mets l'accent sur la qualité, l'artisanat et le prestige.",
            "technical": "Utilise un ton technique et détaillé. Concentre-toi sur les spécifications et les fonctionnalités avancées.",
            "educational": "Utilise un ton éducatif et informatif. Explique clairement les concepts et les avantages."
        }
        
        # Rechercher le ton dans le mapping ou utiliser la description complète
        for key, value in tone_mapping.items():
            if key in tone.lower():
                return value
        
        # Si aucun ton spécifique n'est trouvé, utiliser la description complète ou une valeur par défaut
        if tone:
            return f"Utilise le ton suivant: {tone}"
        else:
            return "Adapte le ton au public cible et à la nature du produit."
    
    def _format_persona_instructions(self, tone_style: Dict[str, Any]) -> str:
        """
        Formate les instructions de persona cible pour le prompt de génération.
        
        Args:
            tone_style: Dictionnaire contenant les informations de ton et de persona
            
        Returns:
            str: Instructions de persona cible formatées
        """
        persona = tone_style.get("persona_target", "")
        
        if not persona:
            return ""
        
        # Mapping des personas courants
        persona_mapping = {
            "professionnel": "Adapte le contenu pour des professionnels du secteur qui recherchent des informations techniques précises et des avantages concrets.",
            "débutant": "Adapte le contenu pour des débutants qui ont besoin d'explications claires, simples et pédagogiques sans jargon technique excessif.",
            "expert": "Adapte le contenu pour des experts qui apprécient les détails techniques avancés et les spécifications précises.",
            "entreprise": "Adapte le contenu pour des décideurs d'entreprise qui s'intéressent au ROI, à la productivité et aux avantages stratégiques.",
            "particulier": "Adapte le contenu pour des particuliers qui recherchent des solutions pratiques et faciles à comprendre pour leur usage personnel."
        }
        
        # Rechercher le persona dans le mapping ou utiliser la description complète
        for key, value in persona_mapping.items():
            if key in persona.lower():
                return value
        
        # Si aucun persona spécifique n'est trouvé, utiliser la description complète
        return f"Le public cible est: {persona}. Adapte le langage, le ton et les arguments pour ce public spécifique."
    
    def _format_evaluation_summary(self, evaluation: EvaluationOutput) -> str:
        """
        Formate le résumé de l'évaluation pour le prompt d'amélioration.
        
        Args:
            evaluation: Résultat de l'évaluation
            
        Returns:
            str: Résumé de l'évaluation formaté
        """
        summary = []
        
        summary.append("NOTES D'ÉVALUATION:")
        summary.append(f"- Précision technique: {evaluation.technical_accuracy}/10")
        summary.append(f"- Ton et style: {evaluation.tone_style}/10")
        summary.append(f"- Optimisation SEO: {evaluation.seo_optimization}/10")
        summary.append(f"- Structure: {evaluation.structure}/10")
        summary.append(f"- Persuasion: {evaluation.persuasion}/10")
        summary.append(f"- Différenciation: {evaluation.differentiation}/10")
        summary.append("")
        
        summary.append("JUSTIFICATIONS:")
        summary.append(f"1. Précision technique: {evaluation.technical_accuracy_justification}")
        summary.append(f"2. Ton et style: {evaluation.tone_style_justification}")
        summary.append(f"3. Optimisation SEO: {evaluation.seo_optimization_justification}")
        summary.append(f"4. Structure: {evaluation.structure_justification}")
        summary.append(f"5. Persuasion: {evaluation.persuasion_justification}")
        summary.append(f"6. Différenciation: {evaluation.differentiation_justification}")
        
        return "\n".join(summary)
    
    def _format_improvement_points(self, evaluation: EvaluationOutput) -> str:
        """
        Formate les points d'amélioration pour le prompt d'amélioration.
        
        Args:
            evaluation: Résultat de l'évaluation
            
        Returns:
            str: Points d'amélioration formatés
        """
        points = []
        
        for i, point in enumerate(evaluation.improvement_points, 1):
            points.append(f"{i}. {point}")
        
        return "\n".join(points)
    
    def generate_improved_description(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une description améliorée en utilisant une chaîne d'auto-amélioration.
        
        Args:
            data: Données du produit et options
            
        Returns:
            Dict[str, Any]: Résultat de la génération améliorée
        """
        try:
            # Extraction des données
            product_info = data.get("product_info", {})
            tone_style = data.get("tone_style", {})
            seo_optimization = data.get("seo_optimization", True)
            competitor_insights = data.get("competitor_insights", {})
            seo_guide_insights = data.get("seo_guide_insights", {})
            
            logger.info(f"Génération d'une description améliorée pour: {product_info.get('name', '')}")
            
            # Préparation des inputs pour la chaîne
            inputs = {
                "product_name": product_info.get("name", ""),
                "product_description": product_info.get("description", ""),
                "product_category": product_info.get("category", ""),
                "product_keywords": ", ".join(product_info.get("keywords", [])),
                "technical_specs": self._format_technical_specs(product_info.get("technical_specs", {})),
                "tone_instructions": self._format_tone_instructions(tone_style),
                "persona_instructions": self._format_persona_instructions(tone_style),
                "tone_summary": tone_style.get("tone_description", "Professionnel et informatif"),
                "seo_optimization": "Oui" if seo_optimization else "Non",
                "seo_keywords": ", ".join(product_info.get("keywords", [])),
                "competitor_insights": self._format_competitor_insights(competitor_insights),
                "seo_guide_info": self._format_seo_guide_insights(seo_guide_insights),
                "format_instructions": self.evaluation_parser.get_format_instructions()
            }
            
            # Exécution de la chaîne
            logger.info("Exécution de la chaîne d'auto-amélioration")
            result = self.chain(inputs)
            logger.info("Chaîne d'auto-amélioration exécutée avec succès")
            
            # Construction de la réponse
            response = {
                "original_description": result["generated_description"],
                "evaluation": {
                    "detailed": result["evaluation_result"],
                    "summary": result["evaluation_summary"],
                    "improvement_points": result["improvement_points"]
                },
                "improved_description": result["improved_description"],
                "verification": result["verification_result"]
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la description améliorée: {str(e)}")
            logger.error(traceback.format_exc())
            raise
