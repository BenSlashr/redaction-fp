"""
Modèles Pydantic pour le système RAG (Retrieval-Augmented Generation).
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ClientDocument(BaseModel):
    """Modèle pour un document client à ingérer dans le vector store."""
    document_id: str = Field(description="Identifiant unique du document")
    client_id: str = Field(description="Identifiant du client propriétaire du document")
    title: str = Field(description="Titre du document")
    content: str = Field(description="Contenu textuel du document")
    source_type: str = Field(description="Type de source (catalogue, fiche technique, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Métadonnées additionnelles")


class DocumentChunk(BaseModel):
    """Modèle pour un chunk de document après traitement."""
    chunk_id: str = Field(description="Identifiant unique du chunk")
    document_id: str = Field(description="Identifiant du document parent")
    content: str = Field(description="Contenu textuel du chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées incluant source, client_id, etc.")


class RAGQuery(BaseModel):
    """Modèle pour une requête au système RAG."""
    query_text: str = Field(description="Requête textuelle")
    enriched_query: Optional[str] = Field(default=None, description="Requête enrichie avec des informations supplémentaires")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Filtres à appliquer à la recherche")
    top_k: int = Field(default=5, description="Nombre de résultats à retourner")


class RAGResult(BaseModel):
    """Modèle pour les résultats d'une requête RAG."""
    query: RAGQuery = Field(description="Requête originale")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="Chunks de documents pertinents")
    total_chunks: int = Field(default=0, description="Nombre total de chunks trouvés")
    sources: Optional[List[str]] = Field(default_factory=list, description="Sources des documents")


class RAGGenerationRequest(BaseModel):
    """Modèle pour une demande de génération avec RAG."""
    product_name: str = Field(description="Nom du produit")
    product_description: str = Field(description="Description courte du produit")
    product_category: str = Field(description="Catégorie du produit")
    technical_specs: Dict[str, str] = Field(description="Spécifications techniques")
    tone_description: Optional[str] = Field(default=None, description="Description du ton éditorial")
    predefined_tone_id: Optional[str] = Field(default=None, description="ID du ton prédéfini")
    seo_optimization: Optional[str] = Field(default=None, description="Niveau d'optimisation SEO")
    seo_keywords: Optional[List[str]] = Field(default=None, description="Mots-clés SEO")
    competitor_insights: Optional[str] = Field(default=None, description="Insights concurrentiels")
    seo_guide_info: Optional[str] = Field(default=None, description="Guide SEO")
    brand_name: Optional[str] = Field(default=None, description="Nom de la marque")
    persona_target: Optional[str] = Field(default=None, description="Persona cible")
    use_rag: bool = Field(default=False, description="Utiliser le RAG pour enrichir la génération")
    client_id: Optional[str] = Field(default=None, description="ID du client pour le RAG")
    client_data_ids: Optional[List[str]] = Field(default=None, description="IDs des documents client à utiliser")


class ClientDocumentUpload(BaseModel):
    """Modèle pour l'upload d'un document client."""
    client_id: str = Field(description="Identifiant du client")
    title: str = Field(description="Titre du document")
    content: str = Field(description="Contenu textuel du document")
    source_type: str = Field(description="Type de source (catalogue, fiche technique, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Métadonnées additionnelles")


class ClientDocumentResponse(BaseModel):
    """Modèle pour la réponse après l'upload d'un document client."""
    document_id: str = Field(description="Identifiant unique du document")
    client_id: str = Field(description="Identifiant du client")
    title: str = Field(description="Titre du document")
    source_type: str = Field(description="Type de source")
    chunk_count: int = Field(description="Nombre de chunks créés")
    status: str = Field(description="Statut de l'indexation")


class ClientDataSummaryResponse(BaseModel):
    """Modèle pour le résumé des données client disponibles."""
    client_id: str = Field(description="Identifiant du client")
    document_count: int = Field(description="Nombre total de documents")
    document_types: Dict[str, int] = Field(default_factory=dict, description="Nombre de documents par type")
    documents: List[Dict[str, Any]] = Field(default_factory=list, description="Liste des documents avec métadonnées de base")
