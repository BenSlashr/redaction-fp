"""
Service pour gérer les différents fournisseurs d'IA (OpenAI, Google Gemini, etc.)
"""
import os
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Importation conditionnelle de Gemini
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Module langchain_google_genai non disponible. Le fournisseur Gemini ne sera pas disponible.")
    GEMINI_AVAILABLE = False

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

class AIProvider(ABC):
    """
    Classe abstraite pour les différents fournisseurs d'IA
    """
    
    @abstractmethod
    def initialize_model(self, **kwargs):
        """
        Initialise le modèle d'IA
        """
        pass
    
    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        """
        Génère du contenu à partir d'un prompt
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Retourne le nom du fournisseur d'IA
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Retourne le nom du modèle utilisé
        """
        pass
    
    @abstractmethod
    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de tarification du modèle
        """
        pass


class OpenAIProvider(AIProvider):
    """
    Fournisseur d'IA OpenAI (GPT-4o, etc.)
    """
    
    def __init__(self, model_name="gpt-4o", temperature=0.7, api_key=None):
        """
        Initialise le fournisseur OpenAI
        
        Args:
            model_name: Nom du modèle OpenAI à utiliser
            temperature: Température pour la génération
            api_key: Clé API OpenAI (facultatif, utilise la variable d'environnement par défaut)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.llm = None
        self.initialize_model()
    
    def initialize_model(self, **kwargs):
        """
        Initialise le modèle OpenAI
        """
        try:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                openai_api_key=self.api_key
            )
            logger.debug(f"Modèle OpenAI {self.model_name} initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du modèle OpenAI: {str(e)}")
            raise
    
    def generate_content(self, prompt: str) -> str:
        """
        Génère du contenu à partir d'un prompt
        
        Args:
            prompt: Prompt à envoyer au modèle
            
        Returns:
            str: Contenu généré
        """
        if not self.llm:
            self.initialize_model()
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def get_name(self) -> str:
        """
        Retourne le nom du fournisseur d'IA
        """
        return "OpenAI"
    
    def get_model_name(self) -> str:
        """
        Retourne le nom du modèle utilisé
        """
        return self.model_name
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de tarification du modèle
        """
        pricing = {
            "input": 0.0,
            "output": 0.0,
            "currency": "USD",
            "unit": "1K tokens"
        }
        
        if self.model_name == "gpt-4o":
            pricing["input"] = 0.01
            pricing["output"] = 0.03
        elif self.model_name == "gpt-4":
            pricing["input"] = 0.03
            pricing["output"] = 0.06
        elif self.model_name == "gpt-3.5-turbo":
            pricing["input"] = 0.0015
            pricing["output"] = 0.002
        
        return pricing


class GeminiProvider(AIProvider):
    """
    Fournisseur d'IA Google Gemini (Gemini Pro, etc.)
    """
    
    def __init__(self, model_name="gemini-2.5-pro-exp-03-25", temperature=0.7, api_key=None):
        """
        Initialise le fournisseur Google Gemini
        
        Args:
            model_name: Nom du modèle Gemini à utiliser
            temperature: Température pour la génération
            api_key: Clé API Google (facultatif, utilise la variable d'environnement par défaut)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.llm = None
        self.initialize_model()
    
    def initialize_model(self, **kwargs):
        """
        Initialise le modèle Google Gemini
        """
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                google_api_key=self.api_key,
                convert_system_message_to_human=True  # Important pour Gemini
            )
            logger.debug(f"Modèle Google Gemini {self.model_name} initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du modèle Google Gemini: {str(e)}")
            raise
    
    def generate_content(self, prompt: str) -> str:
        """
        Génère du contenu à partir d'un prompt
        
        Args:
            prompt: Prompt à envoyer au modèle
            
        Returns:
            str: Contenu généré
        """
        if not self.llm:
            self.initialize_model()
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def get_name(self) -> str:
        """
        Retourne le nom du fournisseur d'IA
        """
        return "Google Gemini"
    
    def get_model_name(self) -> str:
        """
        Retourne le nom du modèle utilisé
        """
        return self.model_name
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de tarification du modèle
        """
        pricing = {
            "input": 0.0,
            "output": 0.0,
            "currency": "USD",
            "unit": "1K tokens"
        }
        
        if "gemini-2.5-pro" in self.model_name:
            pricing["input"] = 0.0035
            pricing["output"] = 0.0035
        elif "gemini-1.5-pro" in self.model_name:
            pricing["input"] = 0.0025
            pricing["output"] = 0.0025
        elif "gemini-1.0-pro" in self.model_name:
            pricing["input"] = 0.0010
            pricing["output"] = 0.0010
        
        return pricing


class AIProviderFactory:
    """
    Factory pour créer des instances de fournisseurs d'IA
    """
    
    @staticmethod
    def get_provider(provider_type: str, model_name: str = None, temperature: float = 0.7, api_key: str = None) -> AIProvider:
        """
        Retourne une instance du fournisseur d'IA spécifié
        
        Args:
            provider_type: Type de fournisseur ('openai' ou 'gemini')
            model_name: Nom du modèle à utiliser (facultatif)
            temperature: Température pour la génération (facultatif)
            api_key: Clé API (facultatif)
            
        Returns:
            AIProvider: Instance du fournisseur d'IA
        """
        if provider_type.lower() == "openai":
            model = model_name or "gpt-4o"
            return OpenAIProvider(model_name=model, temperature=temperature, api_key=api_key)
        elif provider_type.lower() == "gemini":
            if not GEMINI_AVAILABLE:
                logger.warning("Le fournisseur Gemini a été demandé mais n'est pas disponible. Utilisation d'OpenAI à la place.")
                model = model_name or "gpt-4o"
                return OpenAIProvider(model_name=model, temperature=temperature, api_key=api_key)
            model = model_name or "gemini-2.5-pro-exp-03-25"
            return GeminiProvider(model_name=model, temperature=temperature, api_key=api_key)
        else:
            raise ValueError(f"Fournisseur d'IA non pris en charge: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> List[Dict[str, Any]]:
        """
        Retourne la liste des fournisseurs d'IA disponibles
        
        Returns:
            List[Dict[str, Any]]: Liste des fournisseurs d'IA disponibles
        """
        providers = [
            {
                "name": "OpenAI",
                "models": [
                    {"id": "gpt-4o", "name": "GPT-4o", "description": "Le modèle le plus récent et le plus performant d'OpenAI"},
                    {"id": "gpt-4", "name": "GPT-4", "description": "Modèle avancé avec d'excellentes capacités de raisonnement"},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Modèle rapide et économique"}
                ]
            }
        ]
        
        # Ajouter Gemini seulement s'il est disponible
        if GEMINI_AVAILABLE:
            providers.append({
                "name": "Google Gemini",
                "models": [
                    {"id": "gemini-2.5-pro-exp-03-25", "name": "Gemini 2.5 Pro", "description": "Le modèle le plus récent et le plus performant de Google"},
                    {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Modèle avancé avec d'excellentes capacités multimodales"},
                    {"id": "gemini-1.0-pro", "name": "Gemini 1.0 Pro", "description": "Modèle rapide et économique"}
                ]
            })
        
        return providers
