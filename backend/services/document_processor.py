"""
Service de traitement des documents pour le système RAG.
Responsable de l'ingestion, du chunking et du traitement des documents client.
"""
import os
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
import re

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangChainDocument

from models.rag_models import ClientDocument, DocumentChunk

# Configuration du logging
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Service de traitement des documents pour le système RAG.
    Responsable de l'ingestion, du chunking et du traitement des documents client.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialise le processeur de documents.
        
        Args:
            chunk_size: Taille des chunks en caractères
            chunk_overlap: Chevauchement entre les chunks en caractères
        """
        logger.debug("Initialisation du DocumentProcessor")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialisation du text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )
        
        logger.debug(f"DocumentProcessor initialisé avec chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    
    def process_document(self, document: ClientDocument) -> List[DocumentChunk]:
        """
        Traite un document client et le découpe en chunks.
        
        Args:
            document: Document client à traiter
            
        Returns:
            Liste des chunks de document
        """
        logger.debug(f"Traitement du document {document.document_id}")
        
        try:
            # Création d'un document LangChain
            langchain_doc = LangChainDocument(
                page_content=document.content,
                metadata={
                    "document_id": document.document_id,
                    "client_id": document.client_id,
                    "title": document.title,
                    "source_type": document.source_type
                }
            )
            
            # Si des métadonnées supplémentaires sont fournies, les ajouter
            if document.metadata:
                langchain_doc.metadata.update(document.metadata)
            
            # Découpage du document en chunks
            chunks = self.text_splitter.split_documents([langchain_doc])
            
            # Conversion des chunks LangChain en DocumentChunk
            document_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document.document_id}_{i}"
                document_chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document.document_id,
                        content=chunk.page_content,
                        metadata=chunk.metadata
                    )
                )
            
            logger.debug(f"Document {document.document_id} traité avec succès, {len(document_chunks)} chunks créés")
            return document_chunks
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du document {document.document_id}: {str(e)}")
            raise
    
    def extract_metadata_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extrait des métadonnées à partir du texte du document.
        Utile pour enrichir les métadonnées des documents sans structure.
        
        Args:
            text: Texte du document
            
        Returns:
            Dictionnaire de métadonnées extraites
        """
        metadata = {}
        
        # Extraction de potentielles références de produits
        product_refs = re.findall(r'[A-Z0-9]{5,10}', text)
        if product_refs:
            metadata["product_references"] = product_refs
        
        # Extraction de potentielles catégories de produits
        categories = []
        common_categories = ["électroménager", "informatique", "meuble", "décoration", 
                            "jardin", "bricolage", "cuisine", "salle de bain"]
        
        for category in common_categories:
            if category.lower() in text.lower():
                categories.append(category)
        
        if categories:
            metadata["categories"] = categories
        
        return metadata
    
    def clean_text(self, text: str) -> str:
        """
        Nettoie le texte avant chunking pour améliorer la qualité.
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        # Suppression des espaces multiples
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Suppression des caractères non imprimables
        cleaned = re.sub(r'[\x00-\x1F\x7F]', '', cleaned)
        
        # Normalisation des sauts de ligne
        cleaned = re.sub(r'\n+', '\n', cleaned)
        
        return cleaned.strip()
    
    def get_document_summary(self, document: ClientDocument) -> str:
        """
        Génère un résumé du document pour l'affichage dans l'interface.
        
        Args:
            document: Document à résumer
            
        Returns:
            Résumé du document
        """
        content = document.content
        
        # Limiter la longueur du contenu pour le résumé
        if len(content) > 500:
            content = content[:497] + "..."
        
        return {
            "document_id": document.document_id,
            "title": document.title,
            "content_preview": content,
            "source_type": document.source_type,
            "client_id": document.client_id
        }
    
    def create_document_from_text(self, 
                                 text: str, 
                                 client_id: str, 
                                 title: str = None, 
                                 source_type: str = "text", 
                                 metadata: Dict[str, Any] = None) -> ClientDocument:
        """
        Crée un document client à partir d'un texte brut.
        
        Args:
            text: Texte du document
            client_id: ID du client
            title: Titre du document (généré si non fourni)
            source_type: Type de source
            metadata: Métadonnées additionnelles
            
        Returns:
            Document client créé
        """
        # Nettoyage du texte
        cleaned_text = self.clean_text(text)
        
        # Génération d'un titre si non fourni
        if not title:
            # Utiliser les premiers mots comme titre
            title_words = cleaned_text.split()[:5]
            title = " ".join(title_words) + "..."
        
        # Génération d'un ID unique
        document_id = str(uuid.uuid4())
        
        # Extraction de métadonnées supplémentaires
        extracted_metadata = self.extract_metadata_from_text(cleaned_text)
        
        # Fusion des métadonnées
        combined_metadata = extracted_metadata
        if metadata:
            combined_metadata.update(metadata)
        
        # Création du document
        return ClientDocument(
            document_id=document_id,
            client_id=client_id,
            title=title,
            content=cleaned_text,
            source_type=source_type,
            metadata=combined_metadata
        )
