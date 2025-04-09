"""
Service d'analyse et d'extraction du ton éditorial à partir d'exemples de texte.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# Configuration du logging
logger = logging.getLogger(__name__)

class ToneAnalyzer:
    """
    Classe pour analyser et extraire le ton éditorial à partir d'exemples de texte.
    Utilise LangChain et OpenAI pour analyser le style d'écriture.
    """
    
    def __init__(self, openai_api_key):
        """
        Initialise l'analyseur de ton avec la clé API OpenAI.
        
        Args:
            openai_api_key (str): Clé API OpenAI
        """
        logger.debug("Initialisation du ToneAnalyzer")
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.3,  # Température plus basse pour des résultats plus cohérents
            openai_api_key=openai_api_key
        )
        
        # Schéma de sortie pour le parsing structuré
        self.response_schemas = [
            ResponseSchema(name="tone_description", 
                          description="Description détaillée du ton et du style d'écriture"),
            ResponseSchema(name="tone_characteristics", 
                          description="Liste des caractéristiques principales du ton"),
            ResponseSchema(name="writing_style", 
                          description="Description du style d'écriture (formel, informel, technique, etc.)"),
            ResponseSchema(name="vocabulary_level", 
                          description="Niveau de vocabulaire utilisé (simple, technique, spécialisé, etc.)"),
            ResponseSchema(name="sentence_structure", 
                          description="Structure des phrases (courtes, longues, complexes, etc.)")
        ]
        
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()
        
        # Template de prompt pour l'analyse du ton
        self.tone_template = """
        Tu es un expert en analyse stylistique et linguistique. Analyse le texte suivant pour en extraire le ton éditorial et le style d'écriture.
        
        TEXTE À ANALYSER:
        ```
        {text_example}
        ```
        
        INSTRUCTIONS:
        1. Analyse le ton, le style et le registre de langage utilisés dans ce texte.
        2. Identifie les caractéristiques distinctives du style d'écriture.
        3. Détermine si le style est formel, informel, technique, conversationnel, etc.
        4. Analyse le niveau de vocabulaire et la complexité des phrases.
        5. Fournis une description détaillée que l'on pourrait utiliser pour reproduire ce style.
        
        {format_instructions}
        """
        
        self.prompt = PromptTemplate(
            template=self.tone_template,
            input_variables=["text_example"],
            partial_variables={"format_instructions": self.format_instructions}
        )
        
        # Chaîne de traitement
        self.chain = self.prompt | self.llm | self.output_parser
        logger.debug("ToneAnalyzer initialisé avec succès")
    
    def analyze_tone(self, text_example):
        """
        Analyse le ton éditorial d'un exemple de texte.
        
        Args:
            text_example (str): Exemple de texte à analyser
            
        Returns:
            dict: Résultats de l'analyse du ton
        """
        logger.info("Début de l'analyse du ton")
        logger.debug(f"Texte à analyser (premiers 100 caractères): {text_example[:100]}...")
        
        try:
            # Préparation des inputs
            inputs = {
                "text_example": text_example
            }
            
            # Appel à l'API OpenAI via la chaîne de traitement
            logger.info("Appel de l'API OpenAI pour l'analyse du ton")
            result = self.chain.invoke(inputs)
            logger.debug(f"Résultat de l'analyse: {result}")
            
            # Construction de la réponse
            tone_analysis = {
                "tone_description": result.get("tone_description", ""),
                "tone_characteristics": self._ensure_list(result.get("tone_characteristics", [])),
                "writing_style": result.get("writing_style", ""),
                "vocabulary_level": result.get("vocabulary_level", ""),
                "sentence_structure": result.get("sentence_structure", "")
            }
            
            logger.info("Analyse du ton terminée avec succès")
            return tone_analysis
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du ton: {str(e)}")
            return {
                "tone_description": f"Erreur lors de l'analyse: {str(e)}",
                "tone_characteristics": [],
                "writing_style": "",
                "vocabulary_level": "",
                "sentence_structure": ""
            }
    
    def _ensure_list(self, value):
        """
        S'assure que la valeur est une liste.
        
        Args:
            value: Valeur à convertir en liste si nécessaire
            
        Returns:
            list: Valeur convertie en liste
        """
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            # Si c'est une chaîne avec des tirets, on la divise en liste
            if value.strip().startswith('-'):
                items = [item.strip() for item in value.split('\n') if item.strip()]
                # Supprime le tiret au début de chaque élément
                return [item[1:].strip() if item.startswith('-') else item for item in items]
            else:
                # Si c'est une chaîne simple, on la retourne comme un élément unique
                return [value]
        else:
            return []


class ToneLibrary:
    """
    Bibliothèque de tons éditoriaux prédéfinis.
    """
    
    def __init__(self):
        """
        Initialise la bibliothèque de tons avec des exemples prédéfinis.
        """
        self.predefined_tones = {
            "professionnel": {
                "name": "Professionnel",
                "description": "Ton formel et technique, adapté aux communications B2B et aux documents officiels.",
                "characteristics": [
                    "Vocabulaire précis et technique",
                    "Phrases bien structurées",
                    "Approche factuelle",
                    "Peu d'expressions familières"
                ],
                "example": """Notre solution d'entreprise offre une intégration complète des processus métier, permettant une optimisation significative de la productivité. Les fonctionnalités avancées comprennent l'analyse en temps réel des données opérationnelles et la génération de rapports personnalisés selon vos besoins spécifiques."""
            },
            "conversationnel": {
                "name": "Conversationnel",
                "description": "Ton décontracté et accessible, comme une conversation avec un ami.",
                "characteristics": [
                    "Langage simple et direct",
                    "Utilisation de la première et deuxième personne",
                    "Questions rhétoriques",
                    "Expressions familières"
                ],
                "example": """Vous en avez assez des produits compliqués ? On vous comprend ! C'est pourquoi nous avons créé cette solution super simple à utiliser. Essayez-la, vous verrez, c'est vraiment un jeu d'enfant. Et si vous avez des questions, n'hésitez pas à nous contacter, on est là pour vous aider !"""
            },
            "persuasif": {
                "name": "Persuasif",
                "description": "Ton convaincant et orienté vers l'action, idéal pour le marketing.",
                "characteristics": [
                    "Utilisation d'arguments forts",
                    "Appels à l'action",
                    "Mise en avant des bénéfices",
                    "Création d'un sentiment d'urgence"
                ],
                "example": """Découvrez dès maintenant notre produit révolutionnaire qui transformera votre quotidien. Grâce à ses fonctionnalités uniques, vous économiserez temps et argent. Ne manquez pas cette opportunité exceptionnelle - les stocks sont limités ! Commandez aujourd'hui et bénéficiez de 20% de réduction."""
            },
            "technique": {
                "name": "Technique",
                "description": "Ton détaillé et précis, adapté aux descriptions techniques et scientifiques.",
                "characteristics": [
                    "Vocabulaire spécialisé",
                    "Données précises et mesurables",
                    "Structure logique",
                    "Références techniques"
                ],
                "example": """Le système utilise un processeur quadricœur cadencé à 2,4 GHz avec 8 Go de mémoire vive DDR4. La transmission des données s'effectue via un protocole sécurisé TLS 1.3 avec chiffrement AES-256. Les performances observées indiquent un temps de réponse moyen de 12 ms sous charge normale et une capacité de traitement de 1000 transactions par seconde."""
            },
            "luxe": {
                "name": "Luxe et Prestige",
                "description": "Ton élégant et raffiné, mettant en valeur l'exclusivité et la qualité.",
                "characteristics": [
                    "Vocabulaire riche et recherché",
                    "Évocation de sensations et d'émotions",
                    "Références à l'artisanat et à l'excellence",
                    "Mise en avant de l'exclusivité"
                ],
                "example": """Fruit d'un savoir-faire d'exception, cette création d'une élégance intemporelle incarne l'alliance parfaite entre tradition et innovation. Chaque détail, minutieusement pensé et exécuté par nos maîtres artisans, témoigne d'une quête incessante de perfection. Une expérience sensorielle unique, réservée aux connaisseurs les plus exigeants."""
            }
        }
    
    def get_tone(self, tone_id):
        """
        Récupère un ton prédéfini par son identifiant.
        
        Args:
            tone_id (str): Identifiant du ton
            
        Returns:
            dict: Informations sur le ton ou None si non trouvé
        """
        return self.predefined_tones.get(tone_id)
    
    def get_all_tones(self):
        """
        Récupère tous les tons prédéfinis.
        
        Returns:
            dict: Tous les tons prédéfinis
        """
        return self.predefined_tones
