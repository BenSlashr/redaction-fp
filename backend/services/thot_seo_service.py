"""
Service d'analyse SEO via l'API THOT SEO.
"""
import logging
import requests
import os
from typing import Dict, Any, Optional, List
import urllib.parse

logger = logging.getLogger(__name__)

class ThotSeoService:
    """
    Service pour obtenir des recommandations SEO via l'API THOT SEO.
    """
    
    def __init__(self):
        self.api_key = os.environ.get("THOT_API_KEY")
        if not self.api_key:
            logger.warning("THOT_API_KEY n'est pas défini dans les variables d'environnement")
        self.base_url = "https://api.thot-seo.fr/commande-api"
    
    def get_seo_guide(self, keywords: str, debug_mode: bool = False) -> Optional[Dict[str, Any]]:
        """
        Obtient un guide SEO pour les mots-clés spécifiés.
        
        Args:
            keywords: Les mots-clés pour lesquels obtenir des recommandations SEO
            debug_mode: Si True, affiche des informations de débogage supplémentaires
            
        Returns:
            Un dictionnaire contenant les recommandations SEO ou None en cas d'erreur
        """
        if not self.api_key:
            logger.error("Impossible d'obtenir des recommandations SEO: THOT_API_KEY manquante")
            return None
            
        # Encoder les mots-clés pour l'URL
        encoded_keywords = urllib.parse.quote(keywords)
        
        # Construire l'URL complète
        url = f"{self.base_url}?keywords={encoded_keywords}&apikey={self.api_key}"
        
        if debug_mode:
            logger.info(f"Requête THOT SEO pour les mots-clés: {keywords}")
            
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if debug_mode:
                logger.info(f"Réponse THOT SEO reçue: {data}")
                
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête à l'API THOT SEO: {e}")
            return None
        except ValueError as e:
            logger.error(f"Erreur lors du parsing de la réponse de l'API THOT SEO: {e}")
            return None
            
    def extract_seo_insights(self, seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les informations SEO les plus pertinentes à partir des données brutes.
        
        Args:
            seo_data: Les données brutes de l'API THOT SEO
            
        Returns:
            Un dictionnaire contenant les informations SEO formatées
        """
        insights = {}
        
        if not seo_data:
            return insights
            
        # Mots-clés obligatoires
        if "KW_obligatoires" in seo_data:
            insights["required_keywords"] = [
                {"keyword": kw[0], "min_occurrences": kw[1], "score": kw[2]} 
                for kw in seo_data.get("KW_obligatoires", [])[:15]  # Limiter aux 15 premiers
            ]
            
        # Mots-clés complémentaires
        if "KW_complementaires" in seo_data:
            insights["complementary_keywords"] = [
                {"keyword": kw[0], "min_occurrences": kw[1], "score": kw[2]} 
                for kw in seo_data.get("KW_complementaires", [])[:10]  # Limiter aux 10 premiers
            ]
            
        # N-grams (expressions)
        if "ngrams" in seo_data:
            insights["expressions"] = seo_data.get("ngrams", "").split(";")[:15]  # Limiter aux 15 premiers
            
        # Questions
        if "questions" in seo_data:
            insights["questions"] = seo_data.get("questions", "").split(";")[:10]  # Limiter aux 10 premières
            
        # Informations générales
        insights["word_count"] = seo_data.get("mots_requis", 0)
        insights["target_score"] = seo_data.get("score_target", 0)
        insights["max_overoptimization"] = seo_data.get("max_suroptimisation", 5)
        
        # Analyse de la concurrence
        if "concurrence" in seo_data:
            competition = []
            for comp in seo_data.get("concurrence", [])[:3]:  # Limiter aux 3 premiers concurrents
                competition.append({
                    "title": comp.get("title", ""),
                    "h1": comp.get("h1", ""),
                    "h2": comp.get("h2", ""),
                    "score": comp.get("score", 0),
                    "word_count": comp.get("words", 0),
                    "url": comp.get("url", ""),
                })
            insights["competition"] = competition
            
        return insights
