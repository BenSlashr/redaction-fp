"""
Service de gestion des templates de fiches produit.
"""
import logging
from typing import List, Dict, Any, Optional
from models.product_template import ProductTemplate, ProductSectionTemplate, DEFAULT_PRODUCT_TEMPLATES

logger = logging.getLogger(__name__)

class TemplateService:
    """
    Service de gestion des templates de fiches produit.
    """
    
    def __init__(self):
        """
        Initialise le service de templates.
        """
        self.templates = DEFAULT_PRODUCT_TEMPLATES
        logger.debug(f"Service de templates initialisé avec {len(self.templates)} templates")
    
    def get_all_templates(self) -> List[ProductTemplate]:
        """
        Récupère tous les templates disponibles.
        
        Returns:
            List[ProductTemplate]: Liste des templates
        """
        return self.templates
    
    def get_template_by_id(self, template_id: str) -> Optional[ProductTemplate]:
        """
        Récupère un template par son ID.
        
        Args:
            template_id: ID du template à récupérer
            
        Returns:
            Optional[ProductTemplate]: Template trouvé ou None
        """
        for template in self.templates:
            if template.id == template_id:
                return template
        return None
    
    def get_default_template(self) -> ProductTemplate:
        """
        Récupère le template par défaut.
        
        Returns:
            ProductTemplate: Template par défaut
        """
        for template in self.templates:
            if template.is_default:
                return template
        
        # Si aucun template n'est marqué comme défaut, retourner le premier
        if self.templates:
            return self.templates[0]
        
        # Cas improbable: aucun template disponible
        raise ValueError("Aucun template disponible")
    
    def customize_template(self, base_template_id: str, section_ids: List[str]) -> ProductTemplate:
        """
        Crée un template personnalisé basé sur un template existant.
        
        Args:
            base_template_id: ID du template de base
            section_ids: Liste des IDs de sections à inclure
            
        Returns:
            ProductTemplate: Template personnalisé
        """
        base_template = self.get_template_by_id(base_template_id)
        if not base_template:
            base_template = self.get_default_template()
        
        # Filtrer les sections selon la liste fournie
        custom_sections = []
        for section in base_template.sections:
            if section.id in section_ids or section.required:
                custom_sections.append(section)
        
        # Trier les sections selon leur ordre d'origine
        custom_sections.sort(key=lambda x: x.order)
        
        # Créer le template personnalisé
        custom_template = ProductTemplate(
            id="custom",
            name="Template personnalisé",
            description=f"Template personnalisé basé sur {base_template.name}",
            sections=custom_sections,
            is_default=False
        )
        
        return custom_template
