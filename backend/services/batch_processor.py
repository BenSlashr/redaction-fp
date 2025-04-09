"""
Service de traitement par lot pour générer plusieurs descriptions de produits en parallèle.
"""
import asyncio
import logging
import traceback
import os
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from .langchain_service import ProductDescriptionGenerator
from .self_improving_chain import SelfImprovingChain

# Configuration du logging
logger = logging.getLogger(__name__)

class BatchProcessor:
    """
    Traite plusieurs produits en parallèle pour générer des descriptions.
    """
    
    def __init__(
        self, 
        product_generator: ProductDescriptionGenerator,
        self_improving_chain: Optional[SelfImprovingChain] = None,
        thot_api_key: Optional[str] = None,
        valueserp_api_key: Optional[str] = None,
        max_workers: int = 3  # Limiter le nombre de traitements parallèles pour éviter de surcharger l'API
    ):
        """
        Initialise le processeur par lot.
        
        Args:
            product_generator: Générateur de descriptions de produits
            self_improving_chain: Chaîne d'auto-amélioration (optionnel)
            thot_api_key: Clé API THOT pour les fonctionnalités SEO (optionnel)
            valueserp_api_key: Clé API ValueSerp pour l'analyse concurrentielle (optionnel)
            max_workers: Nombre maximum de traitements parallèles
        """
        self.product_generator = product_generator
        self.self_improving_chain = self_improving_chain
        self.thot_api_key = thot_api_key
        self.valueserp_api_key = valueserp_api_key
        self.max_workers = max_workers
        
    async def process_batch(
        self, 
        products: List[Dict[str, Any]], 
        tone_style: Dict[str, Any],
        seo_optimization: bool = True,
        use_auto_improvement: bool = False,
        competitor_analysis: bool = False,
        use_seo_guide: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Traite un lot de produits pour générer des descriptions.
        
        Args:
            products: Liste des informations de produits
            tone_style: Style et ton à utiliser
            seo_optimization: Activer l'optimisation SEO
            use_auto_improvement: Utiliser la chaîne d'auto-amélioration
            competitor_analysis: Activer l'analyse des concurrents
            use_seo_guide: Utiliser le guide SEO
            
        Returns:
            Liste des résultats de génération
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Créer les tâches pour chaque produit
            loop = asyncio.get_event_loop()
            futures = []
            
            for product in products:
                if use_auto_improvement and self.self_improving_chain:
                    # Utiliser la chaîne d'auto-amélioration
                    future = loop.run_in_executor(
                        executor,
                        self._process_with_improvement,
                        product,
                        tone_style,
                        seo_optimization,
                        competitor_analysis,
                        use_seo_guide
                    )
                else:
                    # Utiliser le générateur standard
                    future = loop.run_in_executor(
                        executor,
                        self._process_product,
                        product,
                        tone_style,
                        seo_optimization,
                        competitor_analysis,
                        use_seo_guide
                    )
                
                futures.append(future)
            
            # Attendre que toutes les tâches soient terminées
            for future in asyncio.as_completed(futures):
                try:
                    result = await future
                    results.append(result)
                except Exception as e:
                    logger.error(f"Erreur lors du traitement d'un produit: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Ajouter un résultat d'erreur
                    results.append({
                        "status": "error",
                        "error": str(e)
                    })
        
        return results
    
    def _process_product(
        self,
        product: Dict[str, Any],
        tone_style: Dict[str, Any],
        seo_optimization: bool,
        competitor_analysis: bool,
        use_seo_guide: bool
    ) -> Dict[str, Any]:
        """
        Traite un produit et génère une description.
        
        Args:
            product: Informations du produit
            tone_style: Style et ton à utiliser
            seo_optimization: Activer l'optimisation SEO
            competitor_analysis: Activer l'analyse des concurrents
            use_seo_guide: Utiliser le guide SEO
            
        Returns:
            Résultat de la génération
        """
        try:
            # Préparer les données pour le générateur
            request_data = {
                "product_info": product,
                "tone_style": tone_style,
                "seo_optimization": seo_optimization,
                "competitor_analysis": competitor_analysis,
                "use_seo_guide": use_seo_guide
            }
            
            # Récupérer les insights du guide SEO si nécessaire
            if use_seo_guide and self.thot_api_key and "keywords" in product:
                from services.thot_seo_service import ThotSeoService
                
                logger.info(f"Récupération du guide SEO pour {product.get('name', '')}")
                thot_service = ThotSeoService()
                
                # Temporairement définir la clé API dans l'environnement
                original_api_key = os.environ.get("THOT_API_KEY")
                os.environ["THOT_API_KEY"] = self.thot_api_key
                
                # Récupération du guide SEO
                keywords_str = ", ".join(product.get("keywords", [])) if isinstance(product.get("keywords", []), list) else product.get("keywords", "")
                raw_data = thot_service.get_seo_guide(
                    keywords=keywords_str,
                    debug_mode=True
                )
                
                if raw_data:
                    # Extraction des insights SEO
                    seo_insights = thot_service.extract_seo_insights(raw_data)
                    # Ajout des insights SEO à la requête
                    request_data["seo_guide_insights"] = seo_insights
                    logger.info(f"Guide SEO récupéré avec succès pour {product.get('name', '')}")
                else:
                    logger.warning(f"Impossible de récupérer le guide SEO pour {product.get('name', '')}")
                
                # Restaurer la clé API originale
                if original_api_key:
                    os.environ["THOT_API_KEY"] = original_api_key
                else:
                    os.environ.pop("THOT_API_KEY", None)
            
            # Récupérer les insights concurrentiels si nécessaire
            if competitor_analysis and self.valueserp_api_key and "keywords" in product:
                from services.competitor_analyzer import CompetitorAnalyzer
                
                logger.info(f"Récupération des insights concurrentiels pour {product.get('name', '')}")
                competitor_analyzer = CompetitorAnalyzer(
                    valueserp_api_key=self.valueserp_api_key,
                    openai_api_key=self.self_improving_chain.openai_api_key if self.self_improving_chain else None
                )
                
                # Récupération des insights concurrentiels
                search_query = None
                if "keywords" in product and product["keywords"]:
                    search_query = product.get("name", "") + " " + " ".join(product["keywords"][:3])
                
                competitor_insights = competitor_analyzer.analyze_competitors(
                    product_name=product.get("name", ""),
                    product_category=product.get("category", ""),
                    search_query=search_query
                )
                
                if competitor_insights:
                    # Ajout des insights concurrentiels à la requête
                    request_data["competitor_insights"] = competitor_insights
                    logger.info(f"Insights concurrentiels récupérés avec succès pour {product.get('name', '')}")
                else:
                    logger.warning(f"Impossible de récupérer les insights concurrentiels pour {product.get('name', '')}")
            
            # Ajouter la clé THOT si disponible et nécessaire pour le guide SEO
            if use_seo_guide and self.thot_api_key:
                request_data["thot_api_key"] = self.thot_api_key
                
            # Ajouter la clé ValueSerp si disponible et nécessaire pour l'analyse concurrentielle
            if competitor_analysis and self.valueserp_api_key:
                request_data["valueserp_api_key"] = self.valueserp_api_key
            
            # Générer la description
            description = self.product_generator.generate_product_description(request_data)
            
            # Préparer le résultat
            return {
                "product_name": product.get("name", ""),
                "status": "success",
                "product_description": description,
                "seo_suggestions": description.get("seo_suggestions", []),
                "competitor_insights": description.get("competitor_insights", [])
            }
        except Exception as e:
            logger.error(f"Erreur lors de la génération pour {product.get('name', '')}: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "product_name": product.get("name", ""),
                "status": "error",
                "error": str(e)
            }
    
    def _process_with_improvement(
        self,
        product: Dict[str, Any],
        tone_style: Dict[str, Any],
        seo_optimization: bool,
        competitor_analysis: bool,
        use_seo_guide: bool
    ) -> Dict[str, Any]:
        """
        Traite un produit avec la chaîne d'auto-amélioration.
        
        Args:
            product: Informations du produit
            tone_style: Style et ton à utiliser
            seo_optimization: Activer l'optimisation SEO
            competitor_analysis: Activer l'analyse des concurrents
            use_seo_guide: Utiliser le guide SEO
            
        Returns:
            Résultat de la génération améliorée
        """
        if not self.self_improving_chain:
            raise ValueError("La chaîne d'auto-amélioration n'est pas disponible")
        
        try:
            # Préparer les données pour le générateur
            request_data = {
                "product_info": product,
                "tone_style": tone_style,
                "seo_optimization": seo_optimization,
                "competitor_analysis": competitor_analysis,
                "use_seo_guide": use_seo_guide
            }
            
            # Récupérer les insights du guide SEO si nécessaire
            if use_seo_guide and self.thot_api_key and "keywords" in product:
                from services.thot_seo_service import ThotSeoService
                
                logger.info(f"Récupération du guide SEO pour {product.get('name', '')} (amélioration)")
                thot_service = ThotSeoService()
                
                # Temporairement définir la clé API dans l'environnement
                original_api_key = os.environ.get("THOT_API_KEY")
                os.environ["THOT_API_KEY"] = self.thot_api_key
                
                # Récupération du guide SEO
                keywords_str = ", ".join(product.get("keywords", [])) if isinstance(product.get("keywords", []), list) else product.get("keywords", "")
                raw_data = thot_service.get_seo_guide(
                    keywords=keywords_str,
                    debug_mode=True
                )
                
                if raw_data:
                    # Extraction des insights SEO
                    seo_insights = thot_service.extract_seo_insights(raw_data)
                    # Ajout des insights SEO à la requête
                    request_data["seo_guide_insights"] = seo_insights
                    logger.info(f"Guide SEO récupéré avec succès pour {product.get('name', '')} (amélioration)")
                else:
                    logger.warning(f"Impossible de récupérer le guide SEO pour {product.get('name', '')} (amélioration)")
                
                # Restaurer la clé API originale
                if original_api_key:
                    os.environ["THOT_API_KEY"] = original_api_key
                else:
                    os.environ.pop("THOT_API_KEY", None)
            
            # Récupérer les insights concurrentiels si nécessaire
            if competitor_analysis and self.valueserp_api_key and "keywords" in product:
                from services.competitor_analyzer import CompetitorAnalyzer
                
                logger.info(f"Récupération des insights concurrentiels pour {product.get('name', '')} (amélioration)")
                competitor_analyzer = CompetitorAnalyzer(
                    valueserp_api_key=self.valueserp_api_key,
                    openai_api_key=self.self_improving_chain.openai_api_key
                )
                
                # Récupération des insights concurrentiels
                search_query = None
                if "keywords" in product and product["keywords"]:
                    search_query = product.get("name", "") + " " + " ".join(product["keywords"][:3])
                
                competitor_insights = competitor_analyzer.analyze_competitors(
                    product_name=product.get("name", ""),
                    product_category=product.get("category", ""),
                    search_query=search_query
                )
                
                if competitor_insights:
                    # Ajout des insights concurrentiels à la requête
                    request_data["competitor_insights"] = competitor_insights
                    logger.info(f"Insights concurrentiels récupérés avec succès pour {product.get('name', '')} (amélioration)")
                else:
                    logger.warning(f"Impossible de récupérer les insights concurrentiels pour {product.get('name', '')} (amélioration)")
            
            # Ajouter la clé THOT si disponible et nécessaire pour le guide SEO
            if use_seo_guide and self.thot_api_key:
                request_data["thot_api_key"] = self.thot_api_key
                
            # Ajouter la clé ValueSerp si disponible et nécessaire pour l'analyse concurrentielle
            if competitor_analysis and self.valueserp_api_key:
                request_data["valueserp_api_key"] = self.valueserp_api_key
            
            # Générer la description améliorée
            result = self.self_improving_chain.generate_improved_description(request_data)
            
            # Préparer le résultat
            return {
                "product_name": product.get("name", ""),
                "status": "success",
                "improved_description": result.get("improved_description", ""),
                "original_description": result.get("original_description", ""),
                "evaluation": result.get("evaluation", {})
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'amélioration pour {product.get('name', '')}: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "product_name": product.get("name", ""),
                "status": "error",
                "error": str(e)
            }
