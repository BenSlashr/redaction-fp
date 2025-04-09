"""
Routes pour la gestion des templates de fiches produit.
"""
import logging
import traceback
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from services.product_description_service import ProductDescriptionService
from models.template_models import (
    TemplatesResponse, 
    SectionedProductRequest, 
    SectionedProductResponse
)

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router
router = APIRouter(prefix="/templates", tags=["Templates"])

# Dépendance pour obtenir le service de génération de fiches produit
def get_product_description_service(
    provider_type: str = "openai", 
    model_name: str = None
) -> ProductDescriptionService:
    """
    Retourne une instance du service de génération de fiches produit.
    
    Args:
        provider_type: Type de fournisseur d'IA ('openai' ou 'gemini')
        model_name: Nom du modèle à utiliser
        
    Returns:
        ProductDescriptionService: Service de génération de fiches produit
    """
    try:
        return ProductDescriptionService(
            provider_type=provider_type,
            model_name=model_name
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du service de génération: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'initialisation du service de génération: {str(e)}"
        )

@router.get("/", response_model=TemplatesResponse)
async def get_templates(
    service: ProductDescriptionService = Depends(get_product_description_service)
) -> TemplatesResponse:
    """
    Récupère la liste des templates disponibles.
    
    Returns:
        TemplatesResponse: Liste des templates disponibles
    """
    try:
        templates = service.get_available_templates()
        return TemplatesResponse(templates=templates)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des templates: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des templates: {str(e)}"
        )

@router.post("/generate", response_model=SectionedProductResponse)
async def generate_sectioned_product(
    request: SectionedProductRequest,
    service: ProductDescriptionService = Depends(get_product_description_service)
) -> SectionedProductResponse:
    """
    Génère une fiche produit par sections.
    
    Args:
        request: Informations sur le produit et options de génération
        
    Returns:
        SectionedProductResponse: Fiche produit générée par sections
    """
    try:
        logger.info("Demande de génération de fiche produit par sections")
        
        # Si un fournisseur d'IA spécifique est demandé, l'utiliser
        if request.ai_provider:
            provider_type = request.ai_provider.get("provider_type")
            model_name = request.ai_provider.get("model_name")
            
            if provider_type:
                service = get_product_description_service(
                    provider_type=provider_type,
                    model_name=model_name
                )
        
        # Génération de la fiche produit
        result = service.generate_product_description(request.dict())
        
        logger.info("Génération de fiche produit par sections terminée avec succès")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la génération de fiche produit par sections: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de fiche produit par sections: {str(e)}"
        )
