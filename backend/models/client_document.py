from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class ClientDocument(BaseModel):
    """
    Modèle représentant un document client pour le RAG.
    """
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    title: str
    content: str
    source_type: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le document en dictionnaire.
        """
        return {
            "document_id": self.document_id,
            "client_id": self.client_id,
            "title": self.title,
            "content": self.content,
            "source_type": self.source_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientDocument":
        """
        Crée un document à partir d'un dictionnaire.
        """
        # Convertir les chaînes de date en objets datetime
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str) and data["updated_at"]:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        return cls(**data)
