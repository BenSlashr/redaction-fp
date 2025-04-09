"""
Service de gestion des prompts personnalisés.
"""
import logging
import json
import os
from typing import Dict, Any, List, Optional

# Configuration du logging
logger = logging.getLogger(__name__)

class PromptManager:
    """
    Gestionnaire de prompts personnalisés.
    Permet de sauvegarder, charger et mettre à jour les prompts utilisés par l'application.
    """
    
    def __init__(self, prompts_file_path: str = None):
        """
        Initialise le gestionnaire de prompts.
        
        Args:
            prompts_file_path: Chemin vers le fichier de prompts personnalisés
        """
        logger.debug("Initialisation du PromptManager")
        
        # Chemin par défaut pour le fichier de prompts
        self.prompts_file_path = prompts_file_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "custom_prompts.json"
        )
        
        # Création du dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(self.prompts_file_path), exist_ok=True)
        
        # Prompts par défaut
        self.default_prompts = {
            "product_description": {
                "name": "Génération de description de produit",
                "template": """
                Tu es un expert en rédaction de fiches produit optimisées pour le marketing et le SEO.
                
                TÂCHE:
                Génère une description de produit professionnelle pour {product_name} basée sur les informations suivantes.
                
                INFORMATIONS PRODUIT:
                - Description: {product_description}
                - Catégorie: {product_category}
                - Mots-clés: {keywords}
                
                SPÉCIFICATIONS TECHNIQUES:
                {technical_specs}
                
                INFORMATIONS CONCURRENTIELLES:
                {competitor_insights}
                
                GUIDE SEO:
                {seo_guide_info}
                
                TON ÉDITORIAL:
                {tone_instructions}
                
                {client_data_context}
                
                OPTIMISATION SEO:
                - Optimisation demandée: {seo_optimization}
                
                INSTRUCTIONS:
                - Crée une description complète et persuasive
                - Mets en avant les avantages et caractéristiques clés
                - Utilise des sous-titres pour structurer le contenu
                - Intègre naturellement les mots-clés SEO
                - Adapte le ton à la marque et au public cible
                
                {format_instructions}
                """
            },
            "competitor_analysis": {
                "name": "Analyse des concurrents",
                "template": """
                Tu es un expert en analyse concurrentielle et marketing. Analyse le contenu extrait des sites concurrents pour un produit.
                
                PRODUIT À ANALYSER:
                {product_name} - {product_category}
                
                CONTENU DES SITES CONCURRENTS:
                {competitor_content}
                
                TÂCHE:
                Analyse ce contenu et identifie les éléments suivants:
                
                1. CARACTÉRISTIQUES CLÉS: Quelles sont les principales caractéristiques mentionnées par les concurrents pour ce type de produit?
                
                2. ARGUMENTS DE VENTE UNIQUES: Quels sont les principaux arguments de vente utilisés par les concurrents?
                
                3. SPÉCIFICATIONS TECHNIQUES COMMUNES: Quelles spécifications techniques sont fréquemment mentionnées?
                
                4. STRUCTURE DE CONTENU: Quelle structure de contenu semble la plus efficace (sections, organisation)?
                
                5. MOTS-CLÉS SEO: Quels semblent être les mots-clés SEO principaux utilisés?
                
                Fournis une analyse détaillée et structurée pour chaque point.
                """
            },
            "tone_analysis": {
                "name": "Analyse de ton éditorial",
                "template": """
                Tu es un expert en analyse stylistique et éditoriale. Analyse le ton et le style du texte fourni.
                
                TEXTE À ANALYSER:
                {text}
                
                TÂCHE:
                Analyse ce texte et identifie les éléments suivants:
                
                1. DESCRIPTION DU TON: Décris le ton général du texte (formel, conversationnel, technique, etc.)
                
                2. CARACTÉRISTIQUES DU TON: Identifie 5 caractéristiques principales qui définissent ce ton
                
                3. STYLE D'ÉCRITURE: Décris le style d'écriture (direct, descriptif, narratif, etc.)
                
                4. NIVEAU DE VOCABULAIRE: Évalue le niveau de vocabulaire utilisé (simple, technique, spécialisé, etc.)
                
                5. STRUCTURE DES PHRASES: Analyse la structure des phrases (courtes, longues, complexes, etc.)
                
                Fournis une analyse détaillée et structurée pour chaque point.
                """
            },
            "self_improvement_generation": {
                "name": "Génération initiale (auto-amélioration)",
                "template": """
                Tu es un expert en rédaction de fiches produit optimisées pour le marketing et le SEO.
                
                TÂCHE:
                Génère une description de produit professionnelle pour {product_name} basée sur les informations suivantes.
                
                INFORMATIONS PRODUIT:
                - Description: {product_description}
                - Catégorie: {product_category}
                - Mots-clés: {product_keywords}
                
                SPÉCIFICATIONS TECHNIQUES:
                {technical_specs}
                
                TON ÉDITORIAL:
                {tone_instructions}
                
                OPTIMISATION SEO:
                - Optimisation demandée: {seo_optimization}
                - Mots-clés à intégrer: {seo_keywords}
                
                INFORMATIONS CONCURRENTIELLES:
                {competitor_insights}
                
                GUIDE SEO:
                {seo_guide_info}
                
                INSTRUCTIONS SUPPLÉMENTAIRES:
                - Crée une description complète et persuasive
                - Mets en avant les avantages et caractéristiques clés
                - Utilise des sous-titres pour structurer le contenu
                - Intègre naturellement les mots-clés SEO
                - Adapte le ton à la marque et au public cible
                
                DESCRIPTION DE PRODUIT:
                """
            },
            "self_improvement_evaluation": {
                "name": "Évaluation (auto-amélioration)",
                "template": """
                Tu es un expert en marketing, copywriting et SEO. Évalue la description de produit suivante selon des critères précis.
                
                DESCRIPTION DE PRODUIT À ÉVALUER:
                {generated_description}
                
                INFORMATIONS CONTEXTUELLES:
                - Nom du produit: {product_name}
                - Catégorie: {product_category}
                - Ton souhaité: {tone_summary}
                - Mots-clés SEO à intégrer: {seo_keywords}
                
                CRITÈRES D'ÉVALUATION:
                Évalue la description sur une échelle de 1 à 10 pour chacun des critères suivants:
                
                1. Précision technique: Les caractéristiques sont-elles correctement présentées?
                2. Ton et style: Le texte respecte-t-il le ton demandé?
                3. Optimisation SEO: Les mots-clés sont-ils intégrés naturellement?
                4. Structure: La structure est-elle claire et efficace?
                5. Persuasion: Le texte est-il convaincant pour l'acheteur potentiel?
                6. Différenciation: Le produit se distingue-t-il de la concurrence?
                
                Pour chaque critère, donne une note et une justification détaillée.
                Identifie également les 3 principaux points à améliorer, classés par ordre de priorité.
                
                {format_instructions}
                """
            },
            "self_improvement_improvement": {
                "name": "Amélioration (auto-amélioration)",
                "template": """
                Tu es un rédacteur expert en marketing et SEO. Améliore la description de produit suivante en te basant sur l'évaluation fournie.
                
                DESCRIPTION ORIGINALE:
                {generated_description}
                
                ÉVALUATION DÉTAILLÉE:
                {evaluation_summary}
                
                POINTS À AMÉLIORER (par ordre de priorité):
                {improvement_points}
                
                CONTEXTE PRODUIT:
                - Nom du produit: {product_name}
                - Catégorie: {product_category}
                - Ton souhaité: {tone_summary}
                - Mots-clés SEO à intégrer: {seo_keywords}
                
                CONSIGNES:
                1. Génère une nouvelle version améliorée qui corrige les faiblesses identifiées
                2. Conserve les points forts de la version originale
                3. Concentre-toi particulièrement sur les critères ayant reçu les notes les plus basses
                4. Assure-toi que tous les mots-clés SEO sont intégrés naturellement
                5. Respecte le ton et le style demandés
                
                DESCRIPTION AMÉLIORÉE:
                """
            },
            "self_improvement_verification": {
                "name": "Vérification (auto-amélioration)",
                "template": """
                Compare les deux versions de la description de produit et vérifie que les améliorations ont bien été apportées.
                
                VERSION ORIGINALE:
                {generated_description}
                
                VERSION AMÉLIORÉE:
                {improved_description}
                
                POINTS À AMÉLIORER IDENTIFIÉS:
                {improvement_points}
                
                VÉRIFICATION:
                1. Tous les points à améliorer ont-ils été traités? Explique comment.
                2. Y a-t-il des informations importantes qui ont été perdues? Si oui, lesquelles?
                3. Le ton et le style sont-ils cohérents avec la demande initiale?
                4. Les mots-clés SEO sont-ils toujours présents et bien intégrés?
                5. La version améliorée est-elle globalement meilleure que l'originale? Pourquoi?
                
                Si des problèmes persistent, identifie-les précisément.
                
                RÉSUMÉ DES AMÉLIORATIONS:
                """
            }
        }
        
        # Chargement des prompts personnalisés s'ils existent
        self.prompts = self._load_prompts()
        
        logger.debug(f"PromptManager initialisé avec {len(self.prompts)} prompts")
    
    def _load_prompts(self) -> Dict[str, Any]:
        """
        Charge les prompts personnalisés depuis le fichier.
        Si le fichier n'existe pas, utilise les prompts par défaut.
        
        Returns:
            Dict contenant les prompts
        """
        try:
            if os.path.exists(self.prompts_file_path):
                with open(self.prompts_file_path, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                logger.info(f"Prompts personnalisés chargés depuis {self.prompts_file_path}")
                return prompts
            else:
                logger.info("Fichier de prompts personnalisés non trouvé, utilisation des prompts par défaut")
                return self.default_prompts.copy()
        except Exception as e:
            logger.error(f"Erreur lors du chargement des prompts: {str(e)}")
            return self.default_prompts.copy()
    
    def _save_prompts(self) -> bool:
        """
        Sauvegarde les prompts personnalisés dans le fichier.
        
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            with open(self.prompts_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, ensure_ascii=False, indent=2)
            logger.info(f"Prompts personnalisés sauvegardés dans {self.prompts_file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des prompts: {str(e)}")
            return False
    
    def get_all_prompts(self) -> Dict[str, Any]:
        """
        Récupère tous les prompts.
        
        Returns:
            Dict contenant tous les prompts
        """
        return self.prompts
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un prompt spécifique.
        
        Args:
            prompt_id: Identifiant du prompt
            
        Returns:
            Dict contenant le prompt ou None s'il n'existe pas
        """
        return self.prompts.get(prompt_id)
    
    def update_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> bool:
        """
        Met à jour un prompt existant.
        
        Args:
            prompt_id: Identifiant du prompt
            prompt_data: Nouvelles données du prompt
            
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if prompt_id not in self.prompts:
            logger.warning(f"Tentative de mise à jour d'un prompt inexistant: {prompt_id}")
            return False
        
        try:
            self.prompts[prompt_id] = prompt_data
            success = self._save_prompts()
            logger.info(f"Prompt {prompt_id} mis à jour avec succès")
            return success
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du prompt {prompt_id}: {str(e)}")
            return False
    
    def reset_to_default(self, prompt_id: str = None) -> bool:
        """
        Réinitialise un prompt ou tous les prompts aux valeurs par défaut.
        
        Args:
            prompt_id: Identifiant du prompt à réinitialiser, ou None pour tous les réinitialiser
            
        Returns:
            bool: True si la réinitialisation a réussi, False sinon
        """
        try:
            if prompt_id:
                if prompt_id in self.default_prompts:
                    self.prompts[prompt_id] = self.default_prompts[prompt_id].copy()
                    logger.info(f"Prompt {prompt_id} réinitialisé aux valeurs par défaut")
                else:
                    logger.warning(f"Prompt par défaut inexistant: {prompt_id}")
                    return False
            else:
                self.prompts = self.default_prompts.copy()
                logger.info("Tous les prompts réinitialisés aux valeurs par défaut")
            
            success = self._save_prompts()
            return success
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation des prompts: {str(e)}")
            return False
