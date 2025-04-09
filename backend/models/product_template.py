"""
Modèles pour les templates de fiches produit.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ProductSectionTemplate(BaseModel):
    """Modèle pour une section de fiche produit."""
    id: str = Field(..., description="Identifiant unique de la section")
    name: str = Field(..., description="Nom de la section")
    description: str = Field(..., description="Description de la section")
    required: bool = Field(False, description="Indique si la section est obligatoire")
    default_enabled: bool = Field(True, description="Indique si la section est activée par défaut")
    order: int = Field(..., description="Ordre d'affichage de la section")
    rag_query_template: str = Field(
        "", 
        description="Template de requête RAG spécifique à cette section"
    )
    prompt_template: str = Field(
        "", 
        description="Template de prompt spécifique à cette section"
    )


class ProductTemplate(BaseModel):
    """Modèle pour un template de fiche produit."""
    id: str = Field(..., description="Identifiant unique du template")
    name: str = Field(..., description="Nom du template")
    description: str = Field(..., description="Description du template")
    sections: List[ProductSectionTemplate] = Field(
        ..., 
        description="Liste des sections du template"
    )
    is_default: bool = Field(False, description="Indique si c'est le template par défaut")


# Templates prédéfinis
DEFAULT_PRODUCT_SECTIONS = [
    ProductSectionTemplate(
        id="introduction",
        name="Introduction",
        description="Présentation générale du produit",
        required=True,
        default_enabled=True,
        order=1,
        rag_query_template="présentation générale et contexte d'utilisation de {product_name} dans la catégorie {product_category}",
        prompt_template="""
Rédige une introduction captivante pour {product_name} qui présente le produit 
et son utilité principale. Mentionne la marque et le positionnement du produit.
Longueur: 2-3 phrases.
"""
    ),
    ProductSectionTemplate(
        id="benefits",
        name="Avantages et bénéfices",
        description="Principaux avantages et bénéfices du produit",
        required=True,
        default_enabled=True,
        order=2,
        rag_query_template="avantages, bénéfices et points forts de {product_name} par rapport à la concurrence",
        prompt_template="""
Présente les 3-5 principaux avantages et bénéfices de {product_name}.
Mets en avant ce qui le distingue de la concurrence et ses points forts.
Format: liste à puces avec titre pour chaque avantage.
"""
    ),
    ProductSectionTemplate(
        id="technical_specs",
        name="Caractéristiques techniques",
        description="Spécifications techniques détaillées",
        required=True,
        default_enabled=True,
        order=3,
        rag_query_template="spécifications techniques détaillées de {product_name} incluant dimensions, matériaux, capacités",
        prompt_template="""
Détaille les caractéristiques techniques de {product_name} de façon précise et structurée.
Utilise les informations techniques suivantes: {technical_specs}
Format: liste à puces organisée par catégories.
"""
    ),
    ProductSectionTemplate(
        id="use_cases",
        name="Cas d'utilisation",
        description="Exemples concrets d'utilisation",
        required=False,
        default_enabled=True,
        order=4,
        rag_query_template="exemples concrets et cas d'utilisation de {product_name} dans différents contextes",
        prompt_template="""
Présente 2-3 cas d'utilisation concrets pour {product_name}.
Montre comment le produit résout des problèmes spécifiques pour les utilisateurs.
"""
    ),
    ProductSectionTemplate(
        id="installation",
        name="Installation et mise en service",
        description="Instructions d'installation et de mise en service",
        required=False,
        default_enabled=False,
        order=5,
        rag_query_template="instructions d'installation et de mise en service de {product_name}, prérequis et étapes",
        prompt_template="""
Résume les principales étapes d'installation et de mise en service de {product_name}.
Mentionne les prérequis et les points d'attention importants.
"""
    ),
    ProductSectionTemplate(
        id="maintenance",
        name="Entretien et maintenance",
        description="Conseils d'entretien et de maintenance",
        required=False,
        default_enabled=False,
        order=6,
        rag_query_template="conseils d'entretien et de maintenance pour {product_name}, fréquence et méthodes",
        prompt_template="""
Donne des conseils pratiques pour l'entretien et la maintenance de {product_name}.
Précise la fréquence recommandée et les méthodes à utiliser.
"""
    ),
    ProductSectionTemplate(
        id="warranty",
        name="Garantie et SAV",
        description="Informations sur la garantie et le service après-vente",
        required=False,
        default_enabled=True,
        order=7,
        rag_query_template="informations sur la garantie, le SAV et le support pour {product_name}",
        prompt_template="""
Présente les informations de garantie et de service après-vente pour {product_name}.
Inclus la durée de garantie, ce qu'elle couvre et comment contacter le support.
"""
    ),
    ProductSectionTemplate(
        id="customer_reviews",
        name="Avis clients",
        description="Synthèse des avis clients",
        required=False,
        default_enabled=True,
        order=8,
        rag_query_template="avis clients et témoignages sur {product_name}, points forts et points faibles mentionnés",
        prompt_template="""
Synthétise les avis clients sur {product_name}.
Mentionne les points forts récurrents et éventuellement quelques points d'amélioration.
Ne pas inventer d'avis spécifiques mais rester factuel sur les tendances.
"""
    ),
    ProductSectionTemplate(
        id="comparison",
        name="Comparaison avec la concurrence",
        description="Comparaison avec des produits concurrents",
        required=False,
        default_enabled=False,
        order=9,
        rag_query_template="comparaison de {product_name} avec les produits concurrents, avantages et inconvénients",
        prompt_template="""
Compare objectivement {product_name} avec les principaux produits concurrents.
Mets en avant les points forts sans dénigrer la concurrence.
Utilise ces insights concurrentiels si disponibles: {competitor_insights}
"""
    ),
    ProductSectionTemplate(
        id="conclusion",
        name="Conclusion",
        description="Conclusion et appel à l'action",
        required=True,
        default_enabled=True,
        order=10,
        rag_query_template="conclusion et synthèse des points forts de {product_name}, public cible idéal",
        prompt_template="""
Rédige une conclusion persuasive qui résume les principaux atouts de {product_name}.
Termine par un appel à l'action adapté au produit.
Longueur: 2-3 phrases.
"""
    ),
]

# Templates prédéfinis
DEFAULT_PRODUCT_TEMPLATES = [
    ProductTemplate(
        id="standard",
        name="Fiche produit standard",
        description="Template standard pour tous types de produits",
        sections=[
            section for section in DEFAULT_PRODUCT_SECTIONS 
            if section.default_enabled or section.required
        ],
        is_default=True
    ),
    ProductTemplate(
        id="technical",
        name="Fiche produit technique",
        description="Template orienté spécifications techniques",
        sections=[
            section for section in DEFAULT_PRODUCT_SECTIONS
            if section.id in ["introduction", "technical_specs", "installation", 
                             "maintenance", "use_cases", "warranty", "conclusion"]
        ],
        is_default=False
    ),
    ProductTemplate(
        id="commercial",
        name="Fiche produit commerciale",
        description="Template orienté vente et bénéfices",
        sections=[
            section for section in DEFAULT_PRODUCT_SECTIONS
            if section.id in ["introduction", "benefits", "customer_reviews", 
                             "comparison", "warranty", "conclusion"]
        ],
        is_default=False
    ),
]
