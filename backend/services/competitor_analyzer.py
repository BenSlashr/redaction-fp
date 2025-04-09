"""
Service d'analyse des concurrents via ValueSERP et extraction de contenu web.
"""
import logging
import requests
import os
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# Configuration du logging
logger = logging.getLogger(__name__)

class CompetitorAnalyzer:
    """
    Classe pour analyser les concurrents via ValueSERP et extraire des informations pertinentes.
    """
    
    def __init__(self, valueserp_api_key: str, openai_api_key: str):
        """
        Initialise l'analyseur de concurrents avec les clés API nécessaires.
        
        Args:
            valueserp_api_key (str): Clé API ValueSERP
            openai_api_key (str): Clé API OpenAI
        """
        logger.debug("Initialisation du CompetitorAnalyzer")
        self.valueserp_api_key = valueserp_api_key
        
        # Initialisation du modèle OpenAI
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,  # Température basse pour des résultats plus factuels
            openai_api_key=openai_api_key
        )
        
        # Schéma de sortie pour le parsing structuré
        self.response_schemas = [
            ResponseSchema(name="key_features", 
                          description="Liste des caractéristiques clés mentionnées par les concurrents"),
            ResponseSchema(name="unique_selling_points", 
                          description="Liste des arguments de vente uniques utilisés par les concurrents"),
            ResponseSchema(name="common_specifications", 
                          description="Liste des spécifications techniques fréquemment mentionnées"),
            ResponseSchema(name="content_structure", 
                          description="Structure de contenu efficace observée chez les concurrents"),
            ResponseSchema(name="seo_keywords", 
                          description="Mots-clés SEO fréquemment utilisés par les concurrents")
        ]
        
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()
        
        # Template de prompt pour l'analyse des concurrents
        self.analysis_template = """
        Tu es un expert en analyse de contenu et en marketing digital. Analyse le contenu des pages concurrentes suivantes pour en extraire des informations pertinentes pour notre propre fiche produit.

        CONTEXTE:
        Nous créons une fiche produit pour: {product_name}
        Catégorie de produit: {product_category}
        
        CONTENU DES PAGES CONCURRENTES:
        {competitor_content}
        
        INSTRUCTIONS:
        1. Identifie les caractéristiques clés du produit mentionnées par les concurrents.
        2. Repère les arguments de vente uniques utilisés.
        3. Note les spécifications techniques fréquemment mentionnées.
        4. Analyse la structure de contenu efficace utilisée par les concurrents.
        5. Identifie les mots-clés SEO fréquemment utilisés.
        
        Concentre-toi uniquement sur les informations pertinentes pour notre produit et ignore le contenu non lié.
        
        {format_instructions}
        """
        
        self.prompt = PromptTemplate(
            template=self.analysis_template,
            input_variables=["product_name", "product_category", "competitor_content"],
            partial_variables={"format_instructions": self.format_instructions}
        )
        
        # Chaîne de traitement
        self.chain = self.prompt | self.llm | self.output_parser
        logger.debug("CompetitorAnalyzer initialisé avec succès")
    
    def search_competitors(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """
        Recherche les concurrents via ValueSERP.
        
        Args:
            query (str): Requête de recherche (nom du produit + code produit)
            num_results (int): Nombre de résultats à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des résultats de recherche
        """
        logger.info(f"Recherche de concurrents pour: {query}")
        
        try:
            # Paramètres de l'API ValueSERP
            params = {
                "api_key": self.valueserp_api_key,
                "q": query,
                "location": "France",
                "google_domain": "google.fr",
                "gl": "fr",
                "hl": "fr",
                "num": num_results + 2  # On demande plus de résultats pour compenser les résultats non pertinents
            }
            
            # Appel à l'API ValueSERP
            logger.info(f"Appel à l'API ValueSERP avec la requête: {query}")
            response = requests.get("https://api.valueserp.com/search", params=params)
            response.raise_for_status()
            
            # Traitement de la réponse
            search_results = response.json()
            organic_results = search_results.get("organic_results", [])
            logger.info(f"Nombre total de résultats organiques: {len(organic_results)}")
            
            # Filtrage des résultats (on exclut les marketplaces génériques)
            filtered_results = []
            excluded_domains = ["amazon.fr", "ebay.fr", "leboncoin.fr", "rakuten.fr"]
            
            for result in organic_results:
                domain = self._extract_domain(result.get("link", ""))
                if domain not in excluded_domains:
                    filtered_results.append(result)
                    logger.info(f"Site concurrent retenu: {result.get('title', 'Sans titre')} - {result.get('link', 'Sans lien')} (domaine: {domain})")
                    if len(filtered_results) >= num_results:
                        break
                else:
                    logger.info(f"Site exclu (marketplace): {result.get('title', 'Sans titre')} - {domain}")
            
            logger.info(f"Récupération de {len(filtered_results)} résultats pertinents")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche ValueSERP: {str(e)}")
            return []
    
    def extract_content(self, url: str) -> str:
        """
        Extrait le contenu pertinent d'une page web.
        
        Args:
            url (str): URL de la page à extraire
            
        Returns:
            str: Contenu extrait
        """
        logger.info(f"Extraction du contenu de: {url}")
        
        try:
            # Récupération du contenu de la page
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parsing du contenu avec BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Suppression des éléments non pertinents
            for element in soup.find_all(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Extraction du contenu principal
            main_content = ""
            
            # Tentative d'extraction du contenu principal via les balises sémantiques
            content_tags = soup.find_all(["main", "article", "section", "div.product-description", "div.product-details"])
            
            if content_tags:
                logger.debug(f"Balises de contenu trouvées: {len(content_tags)}")
                for tag in content_tags:
                    # Vérification que le contenu est suffisamment pertinent (contient du texte)
                    content_text = tag.get_text(strip=True)
                    if len(content_text) > 200:
                        main_content += content_text + "\n\n"
                        logger.debug(f"Contenu extrait d'une balise ({len(content_text)} caractères)")
            
            # Si aucun contenu pertinent n'a été trouvé, on prend tout le texte
            if not main_content:
                logger.debug("Aucune balise de contenu pertinente trouvée, extraction du texte complet")
                main_content = soup.get_text(strip=True)
            
            # Limitation de la taille du contenu (pour éviter de dépasser les limites d'OpenAI)
            max_chars = 10000
            if len(main_content) > max_chars:
                logger.debug(f"Contenu tronqué de {len(main_content)} à {max_chars} caractères")
                main_content = main_content[:max_chars] + "...[contenu tronqué]"
            
            logger.info(f"Extraction réussie: {len(main_content)} caractères")
            return main_content
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du contenu: {str(e)}")
            return f"Erreur d'extraction: {str(e)}"
    
    def analyze_competitors(self, product_name: str, product_category: str, search_query: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyse complète des concurrents pour un produit donné.
        
        Args:
            product_name (str): Nom du produit
            product_category (str): Catégorie du produit
            search_query (Optional[str]): Requête de recherche personnalisée (si None, utilise le nom du produit)
            
        Returns:
            Dict[str, Any]: Résultats de l'analyse
        """
        logger.info(f"Début de l'analyse des concurrents pour: {product_name}")
        
        try:
            # Préparation de la requête de recherche
            if not search_query:
                search_query = f"{product_name} fiche technique caractéristiques"
            
            # Recherche des concurrents
            competitors = self.search_competitors(search_query)
            
            if not competitors:
                logger.warning("Aucun concurrent trouvé")
                return {
                    "key_features": [],
                    "unique_selling_points": [],
                    "common_specifications": [],
                    "content_structure": "",
                    "seo_keywords": []
                }
            
            # Extraction du contenu des pages concurrentes
            all_content = ""
            for i, competitor in enumerate(competitors):
                url = competitor.get("link")
                title = competitor.get("title", "")
                
                logger.info(f"Traitement du concurrent {i+1}/{len(competitors)}: {title}")
                
                content = self.extract_content(url)
                content_preview = content[:200].replace("\n", " ") + "..." if len(content) > 200 else content
                logger.debug(f"Aperçu du contenu extrait: {content_preview}")
                
                all_content += f"--- CONCURRENT {i+1}: {title} ---\n{content}\n\n"
            
            # Analyse du contenu avec OpenAI
            logger.info(f"Analyse du contenu avec OpenAI ({len(all_content)} caractères au total)")
            
            inputs = {
                "product_name": product_name,
                "product_category": product_category,
                "competitor_content": all_content
            }
            
            # Log du prompt complet (en mode debug uniquement)
            prompt_preview = self.prompt.format(**inputs)
            if len(prompt_preview) > 500:
                prompt_preview = prompt_preview[:500] + "..."
            logger.debug(f"Aperçu du prompt envoyé à OpenAI: {prompt_preview}")
            
            result = self.chain.invoke(inputs)
            logger.debug(f"Résultat de l'analyse: {result}")
            
            # Construction de la réponse
            analysis_result = {
                "key_features": self._ensure_list(result.get("key_features", [])),
                "unique_selling_points": self._ensure_list(result.get("unique_selling_points", [])),
                "common_specifications": self._ensure_list(result.get("common_specifications", [])),
                "content_structure": result.get("content_structure", ""),
                "seo_keywords": self._ensure_list(result.get("seo_keywords", []))
            }
            
            # Log des résultats
            logger.info(f"Analyse des concurrents terminée avec succès")
            logger.info(f"Caractéristiques clés identifiées: {len(analysis_result['key_features'])}")
            logger.info(f"Arguments de vente identifiés: {len(analysis_result['unique_selling_points'])}")
            logger.info(f"Spécifications communes identifiées: {len(analysis_result['common_specifications'])}")
            logger.info(f"Mots-clés SEO identifiés: {len(analysis_result['seo_keywords'])}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des concurrents: {str(e)}")
            return {
                "key_features": [],
                "unique_selling_points": [],
                "common_specifications": [],
                "content_structure": f"Erreur lors de l'analyse: {str(e)}",
                "seo_keywords": []
            }
    
    def _extract_domain(self, url: str) -> str:
        """
        Extrait le domaine d'une URL.
        
        Args:
            url (str): URL complète
            
        Returns:
            str: Domaine extrait
        """
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except:
            return url
    
    def _ensure_list(self, value: Any) -> List[str]:
        """
        S'assure que la valeur est une liste.
        
        Args:
            value: Valeur à convertir en liste si nécessaire
            
        Returns:
            List[str]: Valeur convertie en liste
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
