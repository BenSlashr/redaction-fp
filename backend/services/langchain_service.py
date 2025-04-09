from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List, Optional
import logging
import os
import traceback
from dotenv import load_dotenv
import json
from .prompt_manager import PromptManager
from .ai_provider_service import AIProviderFactory, AIProvider
from .vector_store_service import VectorStoreService

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Récupération de la clé API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logger.debug(f"Clé API OpenAI configurée: {'Oui' if OPENAI_API_KEY else 'Non'}")
logger.debug(f"Longueur de la clé API OpenAI: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0}")

class ProductDescriptionGenerator:
    """
    Générateur de descriptions de produits utilisant LangChain.
    """
    
    def __init__(self, openai_api_key: str = None, provider_type: str = "openai", model_name: str = None):
        """
        Initialise le générateur de descriptions de produits.
        
        Args:
            openai_api_key: Clé API OpenAI (pour compatibilité avec le code existant)
            provider_type: Type de fournisseur d'IA ('openai' ou 'gemini')
            model_name: Nom du modèle à utiliser
        """
        try:
            logger.debug("Initialisation du générateur de descriptions de produits")
            
            # Initialisation du modèle LLM via le factory
            logger.debug(f"Initialisation du modèle via {provider_type}")
            self.provider_type = provider_type
            self.model_name = model_name
            
            # Déterminer la clé API à utiliser
            api_key = None
            if provider_type.lower() == "openai":
                api_key = openai_api_key or OPENAI_API_KEY
            elif provider_type.lower() == "gemini":
                api_key = os.getenv("GOOGLE_API_KEY")
            
            # Création du fournisseur d'IA
            self.ai_provider = AIProviderFactory.get_provider(
                provider_type=provider_type,
                model_name=model_name,
                temperature=0.7,
                api_key=api_key
            )
            
            logger.debug(f"Modèle {self.ai_provider.get_name()} {self.ai_provider.get_model_name()} initialisé avec succès")
            
            # Pour la compatibilité avec le code existant (certaines parties peuvent encore utiliser self.llm)
            if provider_type.lower() == "openai":
                self.llm = ChatOpenAI(
                    model=model_name or "gpt-4o",
                    temperature=0.7,
                    openai_api_key=openai_api_key or OPENAI_API_KEY
                )
            
            # Initialisation du gestionnaire de prompts
            self.prompt_manager = PromptManager()
            
            # Initialisation du service Vector Store (RAG) avec None par défaut
            # Il sera initialisé à la demande pour éviter de charger inutilement les embeddings
            self.vector_store_service = None
            
            # Schéma de sortie pour le parsing structuré
            logger.debug("Configuration du schéma de sortie")
            self.response_schemas = [
                ResponseSchema(name="product_description", 
                              description="Description complète et détaillée du produit"),
                ResponseSchema(name="seo_suggestions", 
                              description="Liste de suggestions pour optimiser le référencement"),
                ResponseSchema(name="competitor_insights", 
                              description="Insights basés sur l'analyse des concurrents")
            ]
            
            self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
            self.format_instructions = self.output_parser.get_format_instructions()
            logger.debug("Parser de sortie configuré avec succès")
            
            # Récupération du prompt de génération de descriptions
            prompt_data = self.prompt_manager.get_prompt("product_description")
            if prompt_data:
                self.product_template = prompt_data["template"]
                logger.debug("Prompt personnalisé chargé avec succès")
                
                # Vérifier que le template contient la variable client_data_context
                if "{client_data_context}" not in self.product_template:
                    logger.warning("Le prompt personnalisé ne contient pas la variable client_data_context, ajout automatique")
                    # Ajouter la variable avant les instructions
                    if "INSTRUCTIONS:" in self.product_template:
                        self.product_template = self.product_template.replace(
                            "INSTRUCTIONS:", 
                            "{client_data_context}\n\nINSTRUCTIONS:"
                        )
                    else:
                        # Si pas de section INSTRUCTIONS, ajouter avant le format_instructions
                        self.product_template = self.product_template.replace(
                            "{format_instructions}", 
                            "{client_data_context}\n\n{format_instructions}"
                        )
            else:
                # Fallback sur le prompt par défaut si non trouvé
                logger.warning("Prompt de génération de descriptions non trouvé, utilisation du prompt par défaut")
                self.product_template = """
                Tu es un expert en rédaction de fiches produit optimisées pour le e-commerce et le SEO.

                INFORMATIONS SUR LE PRODUIT:
                - Nom: {product_name}
                - Description: {product_description}
                - Catégorie: {product_category}
                - Mots-clés: {keywords}
                - Spécifications techniques: {technical_specs}

                INFORMATIONS CONCURRENTIELLES:
                {competitor_insights}

                GUIDE SEO:
                {seo_guide_info}

                TON ÉDITORIAL:
                {tone_instructions}

                PERSONA CIBLE:
                {persona_instructions}

                {client_data_context}

                INSTRUCTIONS:
                1. Génère une fiche produit complète et détaillée qui met en valeur les caractéristiques et avantages du produit.
                2. Structure le contenu avec des sections logiques (introduction, caractéristiques principales, spécifications techniques, etc.)
                3. Utilise un langage persuasif qui incite à l'achat tout en restant informatif.
                4. {seo_optimization}
                5. Adapte le ton et le style selon les instructions fournies.

                {format_instructions}
                """
            
            self.prompt = PromptTemplate(
                template=self.product_template,
                input_variables=[
                    "product_name", 
                    "product_description", 
                    "product_category", 
                    "keywords", 
                    "technical_specs", 
                    "competitor_insights", 
                    "seo_guide_info", 
                    "tone_instructions", 
                    "persona_instructions", 
                    "seo_optimization",
                    "client_data_context"
                ],
                partial_variables={"format_instructions": self.format_instructions}
            )
            logger.debug("Template de prompt configuré avec succès")
            
            # Nous n'utilisons plus la chaîne de traitement car nous utilisons directement le fournisseur d'IA
            
            logger.info("Générateur de descriptions de produits initialisé avec succès")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du générateur de descriptions: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _format_technical_specs(self, specs_dict):
        """Formate les spécifications techniques pour le prompt"""
        logger.debug(f"Formatage des spécifications techniques: {specs_dict}")
        if not specs_dict:
            logger.debug("Aucune spécification technique fournie")
            return "Aucune spécification technique fournie."
        
        formatted_specs = []
        for key, value in specs_dict.items():
            formatted_specs.append(f"- {key}: {value}")
        
        result = "\n".join(formatted_specs)
        logger.debug(f"Spécifications techniques formatées: {result}")
        return result
    
    def _format_tone_instructions(self, tone_data):
        """Formate les instructions de ton éditorial"""
        logger.debug(f"Formatage des instructions de ton: {tone_data}")
        if not tone_data or (not tone_data.get("brand_name") and not tone_data.get("tone_description") and not tone_data.get("tone_example")):
            logger.debug("Aucune instruction de ton fournie, utilisation du ton standard")
            return "Utilise un ton professionnel et informatif standard pour la fiche produit."
        
        instructions = ["Adapte le ton éditorial selon ces directives:"]
        
        if tone_data.get("brand_name"):
            instructions.append(f"- Marque: {tone_data['brand_name']}")
        
        if tone_data.get("tone_description"):
            instructions.append(f"- Style souhaité: {tone_data['tone_description']}")
        
        if tone_data.get("tone_example"):
            instructions.append(f"- Exemple de référence: \"{tone_data['tone_example']}\"")
        
        result = "\n".join(instructions)
        logger.debug(f"Instructions de ton formatées: {result}")
        return result
    
    def _format_competitor_insights(self, competitor_insights):
        """
        Formate les informations concurrentielles pour le prompt.
        
        Args:
            competitor_insights (dict): Informations sur les concurrents
            
        Returns:
            str: Instructions formatées sur les concurrents
        """
        if not competitor_insights:
            return ""
        
        formatted_insights = "INFORMATIONS CONCURRENTIELLES:\n"
        
        # Caractéristiques clés
        if "key_features" in competitor_insights and competitor_insights["key_features"]:
            formatted_insights += "Caractéristiques clés mentionnées par les concurrents:\n"
            for feature in competitor_insights["key_features"]:
                formatted_insights += f"- {feature}\n"
            formatted_insights += "\n"
        
        # Arguments de vente uniques
        if "unique_selling_points" in competitor_insights and competitor_insights["unique_selling_points"]:
            formatted_insights += "Arguments de vente utilisés par les concurrents:\n"
            for point in competitor_insights["unique_selling_points"]:
                formatted_insights += f"- {point}\n"
            formatted_insights += "\n"
        
        # Spécifications techniques communes
        if "common_specifications" in competitor_insights and competitor_insights["common_specifications"]:
            formatted_insights += "Spécifications techniques fréquemment mentionnées:\n"
            for spec in competitor_insights["common_specifications"]:
                formatted_insights += f"- {spec}\n"
            formatted_insights += "\n"
        
        # Structure de contenu
        if "content_structure" in competitor_insights and competitor_insights["content_structure"]:
            formatted_insights += f"Structure de contenu efficace observée:\n{competitor_insights['content_structure']}\n\n"
        
        # Mots-clés SEO
        if "seo_keywords" in competitor_insights and competitor_insights["seo_keywords"]:
            formatted_insights += "Mots-clés SEO fréquemment utilisés:\n"
            for keyword in competitor_insights["seo_keywords"]:
                formatted_insights += f"- {keyword}\n"
            formatted_insights += "\n"
        
        return formatted_insights
    
    def _format_seo_guide_insights(self, seo_guide_insights):
        """
        Formate les insights du guide SEO pour le prompt.
        
        Args:
            seo_guide_insights (dict): Insights du guide SEO
            
        Returns:
            str: Instructions formatées sur le guide SEO
        """
        if not seo_guide_insights:
            return ""
        
        formatted_insights = "GUIDE SEO:\n"
        
        # Mots-clés obligatoires
        if "required_keywords" in seo_guide_insights and seo_guide_insights["required_keywords"]:
            formatted_insights += "Mots-clés obligatoires à inclure (avec nombre d'occurrences minimum):\n"
            for kw in seo_guide_insights["required_keywords"]:
                formatted_insights += f"- {kw['keyword']} ({kw['min_occurrences']} fois, score: {kw['score']})\n"
            formatted_insights += "\n"
        
        # Mots-clés complémentaires
        if "complementary_keywords" in seo_guide_insights and seo_guide_insights["complementary_keywords"]:
            formatted_insights += "Mots-clés complémentaires recommandés:\n"
            for kw in seo_guide_insights["complementary_keywords"]:
                formatted_insights += f"- {kw['keyword']} ({kw['min_occurrences']} fois, score: {kw['score']})\n"
            formatted_insights += "\n"
        
        # Expressions (n-grams)
        if "expressions" in seo_guide_insights and seo_guide_insights["expressions"]:
            formatted_insights += "Expressions à inclure dans le contenu:\n"
            for expr in seo_guide_insights["expressions"]:
                if expr.strip():  # Vérifier que l'expression n'est pas vide
                    formatted_insights += f"- {expr}\n"
            formatted_insights += "\n"
        
        # Questions
        if "questions" in seo_guide_insights and seo_guide_insights["questions"]:
            formatted_insights += "Questions fréquentes à aborder dans le contenu:\n"
            for question in seo_guide_insights["questions"][:5]:  # Limiter à 5 questions
                if question.strip():  # Vérifier que la question n'est pas vide
                    formatted_insights += f"- {question}\n"
            formatted_insights += "\n"
        
        # Informations générales
        if "word_count" in seo_guide_insights:
            formatted_insights += f"Nombre de mots recommandé: {seo_guide_insights['word_count']}\n"
        
        if "target_score" in seo_guide_insights:
            formatted_insights += f"Score SEO cible: {seo_guide_insights['target_score']}\n"
        
        # Analyse de la concurrence
        if "competition" in seo_guide_insights and seo_guide_insights["competition"]:
            formatted_insights += "Analyse des titres et H1 concurrents:\n"
            for comp in seo_guide_insights["competition"]:
                if comp.get("title") and comp.get("title").strip():
                    formatted_insights += f"- Titre: {comp['title']}\n"
                if comp.get("h1") and comp.get("h1").strip():
                    formatted_insights += f"  H1: {comp['h1']}\n"
                if comp.get("word_count"):
                    formatted_insights += f"  Nombre de mots: {comp['word_count']}\n"
                formatted_insights += "\n"
        
        return formatted_insights
    
    def _process_list_field(self, field_value):
        """
        Traite un champ qui devrait être une liste.
        Si c'est une chaîne de caractères, la convertit en liste en la divisant par les tirets.
        """
        logger.debug(f"Traitement du champ liste: {field_value} (type: {type(field_value)})")
        
        if isinstance(field_value, list):
            return field_value
        
        if isinstance(field_value, str):
            # Si c'est une chaîne avec des tirets, on la divise en liste
            if field_value.strip().startswith('-'):
                items = [item.strip() for item in field_value.split('\n') if item.strip()]
                # Supprime le tiret au début de chaque élément
                items = [item[1:].strip() if item.startswith('-') else item for item in items]
                logger.debug(f"Chaîne convertie en liste: {items}")
                return items
            else:
                # Si c'est une chaîne simple, on la retourne comme un élément unique
                logger.debug(f"Chaîne convertie en liste à un élément")
                return [field_value]
        
        # Si c'est None ou un autre type, on retourne une liste vide
        logger.debug(f"Valeur non reconnue, retourne liste vide")
        return []
    
    def _initialize_vector_store_service(self):
        """
        Initialise le service Vector Store (RAG) si ce n'est pas déjà fait.
        """
        if self.vector_store_service is None:
            logger.debug("Initialisation du service Vector Store (RAG)")
            try:
                # Déterminer la clé API à utiliser pour les embeddings
                api_key = None
                if self.provider_type.lower() == "openai":
                    api_key = OPENAI_API_KEY
                
                # Création du service Vector Store
                self.vector_store_service = VectorStoreService(
                    embedding_service="openai" if api_key else "local",
                    openai_api_key=api_key
                )
                logger.debug("Service Vector Store (RAG) initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du service Vector Store: {str(e)}")
                logger.error(traceback.format_exc())
                # Ne pas lever d'exception pour ne pas bloquer le reste du processus
                # Le service continuera sans RAG
                self.vector_store_service = None
    
    def _get_client_data_context(self, product_info, client_id=None, use_rag=False):
        """
        Récupère le contexte des données client via RAG.
        
        Args:
            product_info: Informations sur le produit
            client_id: ID du client
            use_rag: Utiliser le RAG pour enrichir la génération
            
        Returns:
            str: Contexte formaté pour le prompt
        """
        if not use_rag or not client_id:
            logger.warning(" RAG_DEBUG: RAG désactivé ou client_id manquant")
            return ""
            
        try:
            # Initialiser le service Vector Store si nécessaire
            self._initialize_vector_store_service()
            
            # Construire une requête à partir des informations produit
            query = ""
            if isinstance(product_info, dict):
                product_name = product_info.get("name", "")
                product_category = product_info.get("category", "")
                product_description = product_info.get("description", "")
                
                # Construction d'une requête plus spécifique et ciblée
                query = f"caractéristiques techniques détaillées de {product_name}"
                
                # Ajouter des éléments spécifiques à rechercher en fonction de la catégorie
                if "cuve" in product_name.lower() or (product_category and "cuve" in product_category.lower()):
                    query += " incluant capacité, matériaux, dimensions, équipements, prix, garantie et avis clients"
                elif "pompe" in product_name.lower() or (product_category and "pompe" in product_category.lower()):
                    query += " incluant débit, puissance, pression, applications, prix et garantie"
                else:
                    query += " incluant spécifications, prix, garantie, avantages et avis clients"
                
                # Ajouter des mots-clés si disponibles
                keywords = product_info.get("keywords", [])
                if keywords and len(keywords) > 0:
                    query += f" concernant {', '.join(keywords[:3])}"  # Limiter à 3 mots-clés pour éviter les requêtes trop longues
                
                # Ajouter la description si elle est substantielle
                if product_description and len(product_description) > 10:
                    query += f" {product_description[:100]}"  # Limiter à 100 caractères
            else:
                query = str(product_info)
            
            logger.info(f" RAG_DEBUG: Requête RAG construite: '{query}'")
            logger.info(f" RAG_DEBUG: Recherche pour client_id: {client_id}")
            
            # Rechercher le contexte pertinent
            rag_result = self.vector_store_service.query_relevant_context(
                query=query,
                product_info=product_info,
                client_id=client_id,
                top_k=5
            )
            
            # Log détaillé du résultat RAG
            if rag_result and rag_result.chunks:
                logger.info(f" RAG_DEBUG: {len(rag_result.chunks)} chunks trouvés")
                for i, chunk in enumerate(rag_result.chunks):
                    # Vérifier si l'attribut score existe avant d'y accéder
                    score = getattr(chunk, 'score', 0.0)
                    title = chunk.metadata.get('title', 'Sans titre') if hasattr(chunk, 'metadata') else 'Sans titre'
                    logger.info(f" RAG_DEBUG: Chunk {i+1} - Document: {title}")
                    logger.info(f" RAG_DEBUG: Extrait: {chunk.content[:100]}...")
            else:
                logger.warning(" RAG_DEBUG: Aucun chunk pertinent trouvé")
            
            # Formater le contexte pour le prompt
            if rag_result and rag_result.chunks and len(rag_result.chunks) > 0:
                context = self._format_context_for_prompt(rag_result)
                logger.info(f" RAG_DEBUG: Contexte formaté généré ({len(context)} caractères)")
                return context
            else:
                logger.warning(" RAG_DEBUG: Aucune donnée client pertinente trouvée.")
                return "Aucune donnée client pertinente trouvée."
                
        except Exception as e:
            logger.error(f" RAG_DEBUG: Erreur lors de la récupération du contexte client: {str(e)}")
            logger.error(traceback.format_exc())
            return "Erreur lors de la récupération des données client."
    
    def _format_context_for_prompt(self, rag_result):
        """
        Formate le contexte RAG pour le prompt.
        
        Args:
            rag_result: Résultat RAG avec les chunks pertinents
            
        Returns:
            str: Contexte formaté pour le prompt
        """
        if not rag_result or not rag_result.chunks:
            return "Aucune donnée client pertinente trouvée."
            
        context_parts = ["CONTEXTE CLIENT PERTINENT:"]
        
        for i, chunk in enumerate(rag_result.chunks):
            try:
                # Extraire les métadonnées importantes avec gestion des erreurs
                metadata = getattr(chunk, 'metadata', {}) if hasattr(chunk, 'metadata') else {}
                if isinstance(metadata, dict):
                    title = metadata.get("title", "Document sans titre")
                    source_type = metadata.get("source_type", "source inconnue")
                else:
                    title = "Document sans titre"
                    source_type = "source inconnue"
                
                # Ajouter l'en-tête du chunk
                context_parts.append(f"Document {i+1}: {title} (Type: {source_type})")
                
                # Ajouter le contenu du chunk (limité à 500 caractères pour éviter les prompts trop longs)
                content = getattr(chunk, 'content', '') if hasattr(chunk, 'content') else ''
                if content and len(content) > 500:
                    content = content[:497] + "..."
                context_parts.append(content)
                context_parts.append("---")
            except Exception as e:
                logger.error(f" RAG_DEBUG: Erreur lors du formatage du chunk {i}: {str(e)}")
                context_parts.append(f"Document {i+1}: [Erreur de formatage]")
                context_parts.append("---")
        
        formatted_context = "\n".join(context_parts)
        logger.info(f" RAG_DEBUG: Contexte formaté: {formatted_context[:200]}...")
        return formatted_context
    
    def generate_product_description(self, product_data):
        """
        Génère une description de produit enrichie à partir des données fournies.
        
        Args:
            product_data (dict): Données du produit et options de génération
            
        Returns:
            dict: Description générée et suggestions SEO
        """
        try:
            logger.debug("Début de la génération de description produit")
            logger.debug(f"Données reçues: {json.dumps(product_data, ensure_ascii=False)[:500]}...")
            
            # Extraction des données du produit
            product_info = product_data.get("product_info", {})
            tone_style = product_data.get("tone_style", {})
            seo_optimization = product_data.get("seo_optimization", False)
            competitor_analysis = product_data.get("competitor_analysis", False)
            competitor_insights = product_data.get("competitor_insights", {})
            use_seo_guide = product_data.get("use_seo_guide", False)
            seo_guide_insights = product_data.get("seo_guide_insights", {})
            
            # Nouvelles options pour le RAG
            use_rag = product_data.get("use_rag", False)
            client_id = product_data.get("client_id")
            
            logger.info(f" RAG_DEBUG: RAG activé: {use_rag}, Client ID: {client_id}")
            
            # Récupérer les informations du modèle d'IA si spécifiées
            provider_type = product_data.get("ai_provider", {}).get("provider_type", self.provider_type)
            model_name = product_data.get("ai_provider", {}).get("model_name", self.model_name)
            
            # Si le fournisseur ou le modèle a changé, réinitialiser le fournisseur d'IA
            if (provider_type != self.provider_type) or (model_name != self.model_name):
                logger.debug(f"Changement de fournisseur d'IA: {provider_type} {model_name}")
                
                # Déterminer la clé API à utiliser
                api_key = None
                if provider_type.lower() == "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
                elif provider_type.lower() == "gemini":
                    api_key = os.getenv("GOOGLE_API_KEY")
                
                # Création du nouveau fournisseur d'IA
                self.ai_provider = AIProviderFactory.get_provider(
                    provider_type=provider_type,
                    model_name=model_name,
                    temperature=0.7,
                    api_key=api_key
                )
                
                self.provider_type = provider_type
                self.model_name = model_name
                logger.debug(f"Nouveau fournisseur d'IA initialisé: {self.ai_provider.get_name()} {self.ai_provider.get_model_name()}")
            
            # Formatage des spécifications techniques
            tech_specs_formatted = self._format_technical_specs(product_info.get("technical_specs", {}))
            
            # Formatage des instructions de ton
            tone_instructions = self._format_tone_instructions(tone_style)
            
            # Formatage des insights concurrentiels si disponibles
            competitor_info = ""
            if competitor_analysis and competitor_insights:
                competitor_info = self._format_competitor_insights(competitor_insights)
                logger.debug("Insights concurrentiels formatés pour le prompt")
            
            # Formatage des insights du guide SEO si disponibles
            seo_guide_info = ""
            if use_seo_guide and seo_guide_insights:
                seo_guide_info = self._format_seo_guide_insights(seo_guide_insights)
                logger.debug("Guide SEO formaté pour le prompt")
            
            # Formatage des instructions de persona cible
            persona_instructions = ""
            if "persona_target" in tone_style and tone_style["persona_target"]:
                persona_instructions = f"Le public cible est: {tone_style['persona_target']}. Adapte le langage, le ton et les arguments pour ce public spécifique."
            
            # Récupération du contexte des données client via RAG
            client_data_context = ""
            if use_rag:
                client_data_context = self._get_client_data_context(
                    product_info=product_info,
                    client_id=client_id,
                    use_rag=use_rag
                )
                logger.info(f" RAG_DEBUG: Contexte RAG récupéré: {len(client_data_context)} caractères")
                if client_data_context:
                    logger.info(f" RAG_DEBUG: Aperçu du contexte RAG: {client_data_context[:200]}...")
            
            # Construction du prompt complet avec toutes les variables
            prompt_vars = {
                "product_name": product_info.get("name", ""),
                "product_description": product_info.get("description", ""),
                "product_category": product_info.get("category", ""),
                "keywords": ", ".join(product_info.get("keywords", [])),
                "technical_specs": tech_specs_formatted,
                "tone_instructions": tone_instructions,
                "persona_instructions": persona_instructions,
                "seo_optimization": "Optimise le contenu pour le référencement en utilisant les mots-clés de manière naturelle" if seo_optimization else "Ne te préoccupe pas de l'optimisation SEO",
                "competitor_insights": competitor_info,
                "seo_guide_info": seo_guide_info,
                "client_data_context": client_data_context,
                "format_instructions": self.format_instructions
            }
            
            # Vérifier que client_data_context est bien inclus dans le prompt
            logger.info(f" RAG_DEBUG: Inclusion du contexte client dans le prompt: {'client_data_context' in prompt_vars}")
            
            # Formatage du prompt avec toutes les variables
            prompt_template = self.product_template.format(**prompt_vars)
            
            # Log du prompt complet pour débogage
            logger.info(f" RAG_DEBUG: PROMPT COMPLET ENVOYÉ À L'IA:")
            # Découper le prompt en sections pour faciliter la lecture dans les logs
            prompt_lines = prompt_template.split('\n')
            current_section = ""
            for line in prompt_lines:
                if line.strip() and (line.isupper() or line.endswith(':') or "CONTEXTE CLIENT PERTINENT" in line):
                    if current_section:
                        logger.info(f" RAG_DEBUG: Section précédente: {current_section}")
                    current_section = line
                elif line.strip():
                    current_section += " " + line.strip()
            
            # Log de la dernière section
            if current_section:
                logger.info(f" RAG_DEBUG: Dernière section: {current_section}")
            
            # Log du prompt complet pour vérification
            logger.info(f" RAG_DEBUG: VÉRIFICATION DU PROMPT COMPLET:")
            logger.info(prompt_template)
            
            # Création du message pour le modèle
            messages = [
                {"role": "user", "content": prompt_template}
            ]
            
            # Appel au modèle via le fournisseur d'IA
            logger.info(f" RAG_DEBUG: Envoi du prompt au modèle {self.ai_provider.get_name()} {self.ai_provider.get_model_name()}")
            
            # Génération du contenu
            response_content = self.ai_provider.generate_content(messages)
            logger.debug(f"Réponse brute reçue: {response_content[:500]}...")
            
            # Parsing de la réponse
            logger.debug("Parsing de la réponse")
            try:
                parsed_response = self.output_parser.parse(response_content)
                logger.debug(f"Réponse parsée: {json.dumps(parsed_response, ensure_ascii=False)[:500]}...")
            except Exception as parse_error:
                logger.error(f"Erreur lors du parsing de la réponse: {str(parse_error)}")
                # En cas d'erreur de parsing, essayer de récupérer au moins la description
                parsed_response = {
                    "product_description": response_content,
                    "seo_suggestions": [],
                    "competitor_insights": []
                }
            
            # Traitement des champs de type liste
            if "seo_suggestions" in parsed_response:
                parsed_response["seo_suggestions"] = self._process_list_field(parsed_response["seo_suggestions"])
            
            if "competitor_insights" in parsed_response:
                parsed_response["competitor_insights"] = self._process_list_field(parsed_response["competitor_insights"])
            
            # Ajouter les informations sur le modèle utilisé
            parsed_response["ai_provider"] = {
                "provider": self.ai_provider.get_name(),
                "model": self.ai_provider.get_model_name(),
                "pricing": self.ai_provider.get_pricing_info()
            }
            
            # Ajouter des informations sur le RAG si utilisé
            if use_rag:
                parsed_response["rag_info"] = {
                    "used": True,
                    "client_id": client_id,
                    "context_size": len(client_data_context) if client_data_context else 0
                }
            
            logger.info("Génération de description produit terminée avec succès")
            return parsed_response
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération de description produit: {str(e)}")
            logger.error(traceback.format_exc())
            raise
