"""
Service de génération de fiches produit par sections avec RAG spécifique.
"""
import logging
import traceback
from typing import Dict, Any, List, Optional
import json
import os
from dotenv import load_dotenv

from services.section_generator import SectionGenerator
from services.template_service import TemplateService
from models.product_template import ProductTemplate, ProductSectionTemplate

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

class ProductDescriptionService:
    """
    Service de génération de fiches produit par sections avec RAG spécifique.
    """
    
    def __init__(self, openai_api_key: str = None, provider_type: str = "openai", model_name: str = None):
        """
        Initialise le service de génération de fiches produit.
        
        Args:
            openai_api_key: Clé API OpenAI
            provider_type: Type de fournisseur d'IA ('openai' ou 'gemini')
            model_name: Nom du modèle à utiliser
        """
        try:
            logger.debug("Initialisation du service de génération de fiches produit")
            
            # Initialisation du générateur de sections
            self.section_generator = SectionGenerator(
                openai_api_key=openai_api_key,
                provider_type=provider_type,
                model_name=model_name
            )
            
            # Initialisation du service de templates
            self.template_service = TemplateService()
            
            logger.debug("Service de génération de fiches produit initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service de génération: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des templates disponibles.
        
        Returns:
            List[Dict[str, Any]]: Liste des templates
        """
        templates = self.template_service.get_all_templates()
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "is_default": template.is_default,
                "sections": [
                    {
                        "id": section.id,
                        "name": section.name,
                        "description": section.description,
                        "required": section.required,
                        "default_enabled": section.default_enabled,
                        "order": section.order
                    }
                    for section in template.sections
                ]
            }
            for template in templates
        ]
    
    def generate_product_description(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une fiche produit complète par sections.
        
        Args:
            product_data: Données du produit et options de génération
            
        Returns:
            Dict[str, Any]: Fiche produit générée
        """
        try:
            logger.debug("Début de la génération de fiche produit par sections")
            logger.debug(f"Données reçues: {json.dumps(product_data, ensure_ascii=False)[:500]}...")
            
            # Extraction des données du produit
            product_info = product_data.get("product_info", {})
            tone_style = product_data.get("tone_style", {})
            
            # Options supplémentaires
            competitor_analysis = product_data.get("competitor_analysis", False)
            competitor_insights = product_data.get("competitor_insights", {}) if competitor_analysis else {}
            
            use_seo_guide = product_data.get("use_seo_guide", False)
            seo_guide_insights = product_data.get("seo_guide_insights", {}) if use_seo_guide else {}
            
            # Options pour le RAG
            use_rag = product_data.get("use_rag", False)
            client_id = product_data.get("client_id") if use_rag else None
            
            # Récupération du template
            template_id = product_data.get("template_id", "standard")
            selected_sections = product_data.get("sections", [])
            
            # Si des sections sont spécifiées, créer un template personnalisé
            if selected_sections:
                template = self.template_service.customize_template(template_id, selected_sections)
            else:
                template = self.template_service.get_template_by_id(template_id)
                if not template:
                    template = self.template_service.get_default_template()
            
            logger.debug(f"Template sélectionné: {template.name} avec {len(template.sections)} sections")
            
            # Génération de chaque section
            generated_sections = []
            for section in template.sections:
                logger.debug(f"Génération de la section '{section.name}'")
                
                # Génération du contenu de la section
                section_content = self.section_generator.generate_section(
                    section=section,
                    product_info=product_info,
                    tone_style=tone_style,
                    client_id=client_id,
                    competitor_insights=competitor_insights,
                    seo_guide_insights=seo_guide_insights
                )
                
                # Ajout de la section générée
                generated_sections.append({
                    "id": section.id,
                    "name": section.name,
                    "content": section_content
                })
                
                logger.debug(f"Section '{section.name}' générée: {len(section_content)} caractères")
            
            # Construction de la réponse
            response = {
                "product_description": {
                    "template": {
                        "id": template.id,
                        "name": template.name
                    },
                    "sections": generated_sections
                },
                "metadata": {
                    "product_name": product_info.get("name", ""),
                    "product_category": product_info.get("category", ""),
                    "rag_used": use_rag,
                    "client_id": client_id,
                    "ai_provider": {
                        "provider": self.section_generator.ai_provider.get_name(),
                        "model": self.section_generator.ai_provider.get_model_name()
                    }
                }
            }
            
            logger.info("Génération de fiche produit terminée avec succès")
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de fiche produit: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Retourner une réponse d'erreur
            return {
                "error": True,
                "message": f"Erreur lors de la génération: {str(e)}",
                "product_description": {
                    "sections": [
                        {
                            "id": "error",
                            "name": "Erreur",
                            "content": f"Une erreur est survenue lors de la génération de la fiche produit: {str(e)}"
                        }
                    ]
                }
            }
