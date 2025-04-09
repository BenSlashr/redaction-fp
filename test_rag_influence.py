import requests
import json
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration
API_URL = "http://localhost:8000"  # Ajustez si nécessaire

def test_rag_influence():
    """
    Test pour vérifier l'influence du RAG sur la génération de texte.
    Compare une génération avec et sans RAG pour le même produit.
    """
    print("Test de l'influence du RAG sur la génération de texte")
    print("====================================================")
    
    # Données de test
    product_info = {
        "name": "Perceuse sans fil professionnelle XDrill-5000",
        "description": "Perceuse sans fil haute performance pour professionnels",
        "category": "Outillage électroportatif",
        "keywords": ["perceuse sans fil", "perceuse professionnelle", "outillage électroportatif"],
        "technical_specs": {
            "Puissance": "18V",
            "Batterie": "Li-ion 4.0Ah",
            "Vitesse": "0-1800 tr/min",
            "Couple max": "60 Nm",
            "Mandrin": "13 mm"
        }
    }
    
    tone_style = {
        "brand_name": "ProTools",
        "tone_description": "Professionnel, technique, précis",
        "persona_target": "Artisans et professionnels du bâtiment"
    }
    
    # Requête sans RAG
    print("\n1. Génération SANS RAG:")
    payload_without_rag = {
        "product_info": product_info,
        "tone_style": tone_style,
        "seo_optimization": True,
        "competitor_analysis": False,
        "use_seo_guide": False,
        "ai_provider": {
            "provider_type": "openai",
            "model_name": "gpt-4o"
        }
    }
    
    try:
        response_without_rag = requests.post(
            f"{API_URL}/generate-product-description",
            json=payload_without_rag
        )
        response_without_rag.raise_for_status()
        result_without_rag = response_without_rag.json()
        print(f"Statut: {response_without_rag.status_code}")
        print(f"Description générée (premiers 200 caractères): {result_without_rag['product_description'][:200]}...")
    except Exception as e:
        print(f"Erreur lors de la génération sans RAG: {str(e)}")
        result_without_rag = {"product_description": "Erreur"}
    
    # Requête avec RAG
    print("\n2. Génération AVEC RAG:")
    payload_with_rag = {
        "product_info": product_info,
        "tone_style": tone_style,
        "seo_optimization": True,
        "competitor_analysis": False,
        "use_seo_guide": False,
        "use_rag": True,
        "client_id": "client123",  # Remplacez par un ID client valide
        "ai_provider": {
            "provider_type": "openai",
            "model_name": "gpt-4o"
        }
    }
    
    try:
        response_with_rag = requests.post(
            f"{API_URL}/generate-with-rag",
            json=payload_with_rag
        )
        response_with_rag.raise_for_status()
        result_with_rag = response_with_rag.json()
        print(f"Statut: {response_with_rag.status_code}")
        print(f"Description générée (premiers 200 caractères): {result_with_rag['product_description'][:200]}...")
    except Exception as e:
        print(f"Erreur lors de la génération avec RAG: {str(e)}")
        result_with_rag = {"product_description": "Erreur"}
    
    # Analyse des différences
    print("\n3. Comparaison des résultats:")
    
    # Vérifier si les descriptions sont différentes
    if result_without_rag["product_description"] != result_with_rag["product_description"]:
        print("✅ Les descriptions générées sont différentes, ce qui suggère que le RAG a influencé la génération.")
        
        # Sauvegarde des résultats pour analyse
        with open("rag_test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "sans_rag": result_without_rag,
                "avec_rag": result_with_rag
            }, f, ensure_ascii=False, indent=2)
        print("Les résultats complets ont été sauvegardés dans 'rag_test_results.json'")
    else:
        print("❌ Les descriptions générées sont identiques, ce qui suggère que le RAG n'a pas influencé la génération.")

if __name__ == "__main__":
    test_rag_influence()
