"""
Service d'extraction de spécifications techniques à partir de texte brut.
"""
import re
from typing import Dict, Any, List


class SpecsExtractor:
    """
    Extrait les spécifications techniques à partir de texte brut.
    """

    @staticmethod
    def extract_from_text(text: str) -> List[Dict[str, str]]:
        """
        Extrait les spécifications techniques à partir d'un texte brut.
        
        Args:
            text: Le texte brut contenant les spécifications
            
        Returns:
            Une liste de dictionnaires avec les clés 'name' et 'value'
        """
        # Nettoyer le texte (supprimer les espaces en trop, etc.)
        text = text.strip()
        
        # Liste pour stocker les spécifications
        specs = []
        
        # Différentes méthodes d'extraction selon le format détecté
        
        # 1. Format avec tabulations et plusieurs colonnes par ligne
        if '\t' in text:
            # Diviser par lignes
            lines = text.split('\n')
            for line in lines:
                # Diviser chaque ligne par tabulations
                parts = line.split('\t')
                # Traiter les parties par paires (nom: valeur)
                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts):
                        name = parts[i].strip().rstrip(':')
                        value = parts[i + 1].strip()
                        if name and value:  # Ignorer les paires vides
                            specs.append({"name": name, "value": value})
        
        # 2. Format avec ":" comme séparateur
        elif ':' in text and not specs:
            # Essayer de trouver des paires "nom: valeur" avec regex
            pattern = r'([^:]+):\s*([^,\n]+)'
            matches = re.findall(pattern, text)
            for name, value in matches:
                name = name.strip()
                value = value.strip()
                if name and value:  # Ignorer les paires vides
                    specs.append({"name": name, "value": value})
        
        # 3. Format avec lignes "nom: valeur"
        elif not specs:
            lines = text.split('\n')
            for line in lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    name = parts[0].strip()
                    value = parts[1].strip()
                    if name and value:  # Ignorer les paires vides
                        specs.append({"name": name, "value": value})
        
        return specs


# Exemple d'utilisation
if __name__ == "__main__":
    sample_text = """Couleur de la cuve :	bleue	Modèle :	Cuve nue
Matière :	Polyéthylène	Capacité :	5000 L
Diamètre :	1790 mm	Hauteur :	2210 mm
Poids :	101,50 kg	Trou d'homme :	400 mm"""
    
    extractor = SpecsExtractor()
    result = extractor.extract_from_text(sample_text)
    for spec in result:
        print(f"{spec['name']}: {spec['value']}")
