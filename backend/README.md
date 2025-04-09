# RFP Backend - Documentation Technique

## Guide de démarrage rapide

### Installation et configuration

```bash
# Installer les dépendances
pip install -r requirements.txt

# Créer un fichier .env avec les clés API nécessaires
cat > .env << EOL
OPENAI_API_KEY=votre_clé_openai
THOT_API_KEY=votre_clé_thot
VALUESERP_API_KEY=votre_clé_valueserp
LOG_LEVEL=INFO
EOL

# Lancer le serveur
uvicorn main:app --reload
```

### Vérification de l'installation

Une fois le serveur démarré, vous pouvez vérifier que tout fonctionne correctement :

1. Ouvrez http://localhost:8000/docs dans votre navigateur pour accéder à la documentation interactive de l'API
2. Testez l'endpoint `/` pour vérifier que l'API répond
3. Testez l'endpoint `/extract-specs` avec un exemple de texte contenant des spécifications

## Structure du projet

```
backend/
├── services/                # Services métier
│   ├── langchain_service.py       # Générateur de descriptions
│   ├── self_improving_chain.py    # Chaîne d'auto-amélioration
│   ├── thot_seo_service.py        # Service SEO
│   ├── competitor_analyzer.py     # Analyse concurrentielle
│   ├── specs_extractor.py         # Extraction de spécifications
│   ├── batch_processor.py         # Traitement par lot
│   └── prompt_manager.py          # Gestion des prompts
├── prompts/                 # Templates de prompts
│   ├── product_description.txt    # Prompt principal
│   ├── evaluation.txt             # Prompt d'évaluation
│   ├── improvement.txt            # Prompt d'amélioration
│   └── verification.txt           # Prompt de vérification
├── main.py                  # Point d'entrée de l'API
├── requirements.txt         # Dépendances Python
└── .env                     # Variables d'environnement
```

## Vue d'ensemble

Le backend de RFP est construit avec FastAPI et fournit toutes les fonctionnalités nécessaires à la génération de descriptions de produits. Il utilise LangChain pour orchestrer les modèles d'IA et intègre plusieurs API externes pour enrichir les descriptions générées.

## Flux de traitement des données

1. **Réception de la requête** : L'API reçoit une requête contenant les informations du produit et les options de génération
2. **Prétraitement** : Les données sont validées et préparées
3. **Génération de la description** : Le service `ProductDescriptionGenerator` génère une description initiale
4. **Amélioration (optionnelle)** : Si l'option est activée, `SelfImprovingChain` améliore la description
5. **Renvoi du résultat** : La description finale est renvoyée au client

## Dépendances principales

```
fastapi>=0.104.0
uvicorn>=0.23.2
langchain>=0.0.335
langchain-openai>=0.0.1
python-dotenv>=1.0.0
pydantic>=2.4.2
python-multipart>=0.0.6
requests>=2.28.0
beautifulsoup4>=4.11.0
pandas>=1.5.0
```

## Services principaux

### 1. ProductDescriptionGenerator (`services/langchain_service.py`)
Service principal qui génère les descriptions de produits en utilisant LangChain et OpenAI.

**Fonctionnalités clés :**
- Génération de descriptions de produits optimisées pour le SEO
- Personnalisation du ton et du style
- Intégration des spécifications techniques
- Formatage des insights concurrentiels et du guide SEO

**Exemple d'utilisation :**
```python
from services.langchain_service import ProductDescriptionGenerator

generator = ProductDescriptionGenerator()
result = generator.generate_product_description({
    "product_info": {
        "name": "Batterie externe 10000mAh",
        "description": "Batterie portable de haute capacité",
        "category": "Accessoires",
        "keywords": ["batterie", "portable", "charge rapide", "usb-c"],
        "technical_specs": {
            "Capacité": "10000mAh",
            "Ports": "USB-C + USB-A",
            "Poids": "180g"
        }
    },
    "tone_style": {
        "tone": "Professionnel",
        "style": "Informatif",
        "persona_target": "Professionnel"
    },
    "seo_optimization": True
})
```

### 2. SelfImprovingChain (`services/self_improving_chain.py`)
Chaîne d'auto-amélioration qui évalue et améliore les descriptions générées.

**Fonctionnalités clés :**
- Évaluation de la qualité des descriptions
- Identification des points d'amélioration
- Génération de versions améliorées
- Vérification de la qualité finale

**Exemple d'utilisation :**
```python
from services.self_improving_chain import SelfImprovingChain

chain = SelfImprovingChain(openai_api_key="votre_clé_openai")
result = chain.generate_improved_description({
    "product_info": {...},
    "tone_style": {...},
    "seo_optimization": True
})
```

### 3. ThotSeoService (`services/thot_seo_service.py`)
Service d'intégration avec l'API THOT SEO pour obtenir des recommandations SEO.

**Fonctionnalités clés :**
- Récupération de guides SEO pour des mots-clés spécifiques
- Extraction d'insights SEO pertinents
- Formatage des recommandations pour le prompt

**Exemple d'utilisation :**
```python
from services.thot_seo_service import ThotSeoService

# La clé API est récupérée depuis les variables d'environnement
seo_service = ThotSeoService()
seo_guide = seo_service.get_seo_guide(keywords="batterie externe portable")
insights = seo_service.extract_seo_insights(seo_guide)
```

### 4. CompetitorAnalyzer (`services/competitor_analyzer.py`)
Service d'analyse des concurrents via ValueSERP et extraction de contenu web.

**Fonctionnalités clés :**
- Recherche de produits concurrents
- Extraction du contenu des pages concurrentes
- Analyse des caractéristiques clés et arguments de vente
- Identification des mots-clés pertinents

**Exemple d'utilisation :**
```python
from services.competitor_analyzer import CompetitorAnalyzer

analyzer = CompetitorAnalyzer(
    valueserp_api_key="votre_clé_valueserp",
    openai_api_key="votre_clé_openai"
)
insights = analyzer.analyze_competitors(
    product_name="Batterie externe 10000mAh",
    product_category="Accessoires",
    search_query="batterie externe portable 10000mAh"
)
```

### 5. SpecsExtractor (`services/specs_extractor.py`)
Service d'extraction automatique des spécifications techniques à partir de texte brut.

**Fonctionnalités clés :**
- Extraction de paires nom/valeur à partir de différents formats
- Support des formats tabulaires et avec séparateurs
- Nettoyage et normalisation des données extraites

**Exemple d'utilisation :**
```python
from services.specs_extractor import SpecsExtractor

extractor = SpecsExtractor()
specs = extractor.extract_specs("""
Capacité : 10000mAh
Ports : USB-C + USB-A
Poids : 180g
""")
```

### 6. BatchProcessor (`services/batch_processor.py`)
Service de traitement par lot pour générer plusieurs descriptions simultanément.

**Fonctionnalités clés :**
- Traitement parallèle des descriptions
- Support de toutes les options de personnalisation
- Gestion des erreurs et reprise après échec
- Suivi de progression en temps réel

**Exemple d'utilisation :**
```python
from services.batch_processor import BatchProcessor
from services.langchain_service import ProductDescriptionGenerator
from services.self_improving_chain import SelfImprovingChain

processor = BatchProcessor(
    product_generator=ProductDescriptionGenerator(),
    self_improving_chain=SelfImprovingChain(openai_api_key="votre_clé_openai"),
    thot_api_key="votre_clé_thot",
    valueserp_api_key="votre_clé_valueserp"
)

results = processor.process_batch(
    products=[...],  # Liste de produits
    tone_style={...},  # Style global
    seo_optimization=True,
    competitor_analysis=True,
    use_seo_guide=True,
    auto_improve=True
)
```

## API Endpoints

### Endpoints principaux

#### 1. `/generate-product-description` (POST)
Génère une description de produit à partir des informations fournies.

**Paramètres :**
- `product_info` : Informations sur le produit
- `tone_style` : Style et ton à utiliser
- `seo_optimization` : Activer l'optimisation SEO
- `competitor_analysis` : Activer l'analyse concurrentielle
- `use_seo_guide` : Utiliser le guide SEO
- `seo_guide_keywords` : Mots-clés pour le guide SEO
- `auto_improve` : Activer l'auto-amélioration

**Exemple de requête :**
```json
{
  "product_info": {
    "name": "Batterie externe 10000mAh",
    "description": "Batterie portable de haute capacité",
    "category": "Accessoires",
    "keywords": ["batterie", "portable", "charge rapide", "usb-c"],
    "technical_specs": {
      "Capacité": "10000mAh",
      "Ports": "USB-C + USB-A",
      "Poids": "180g"
    }
  },
  "tone_style": {
    "tone": "Professionnel",
    "style": "Informatif",
    "persona_target": "Professionnel"
  },
  "seo_optimization": true,
  "competitor_analysis": true,
  "use_seo_guide": true,
  "seo_guide_keywords": "batterie externe portable",
  "auto_improve": true
}
```

#### 2. `/batch-generate` (POST)
Génère plusieurs descriptions de produits à partir d'un fichier CSV.

**Paramètres :**
- `file` : Fichier CSV contenant les produits
- `tone_style` : Style et ton global
- `seo_optimization` : Activer l'optimisation SEO
- `competitor_analysis` : Activer l'analyse concurrentielle
- `use_seo_guide` : Utiliser le guide SEO
- `auto_improve` : Activer l'auto-amélioration

#### 3. `/extract-specs` (POST)
Extrait les spécifications techniques à partir de texte brut.

**Paramètres :**
- `raw_text` : Texte brut contenant les spécifications

**Exemple de requête :**
```json
{
  "raw_text": "Capacité : 10000mAh\nPorts : USB-C + USB-A\nPoids : 180g"
}
```

#### 4. `/get-seo-guide` (POST)
Récupère un guide SEO pour des mots-clés spécifiques.

**Paramètres :**
- `keywords` : Mots-clés pour le guide SEO

**Exemple de requête :**
```json
{
  "keywords": "batterie externe portable"
}
```

## Configuration

### Variables d'environnement
Le backend utilise les variables d'environnement suivantes :

- `OPENAI_API_KEY` : Clé API OpenAI (obligatoire)
- `THOT_API_KEY` : Clé API THOT SEO (obligatoire pour les fonctionnalités SEO)
- `VALUESERP_API_KEY` : Clé API ValueSERP (optionnelle, pour l'analyse concurrentielle)
- `LOG_LEVEL` : Niveau de log (DEBUG, INFO, WARNING, ERROR)

### Fichier de configuration
Un fichier `.env` à la racine du projet peut être utilisé pour définir ces variables.

## Logging

Le système de logging est configuré dans `main.py` et utilise le module `logging` standard de Python. Les logs sont affichés dans la console et peuvent être configurés pour être plus ou moins verbeux en modifiant la variable d'environnement `LOG_LEVEL`.

## Gestion des erreurs

Le backend utilise un système de gestion d'erreurs centralisé qui :

1. Capture les exceptions
2. Les enregistre dans les logs
3. Renvoie des réponses d'erreur formatées au client

## Performance et optimisation

### Traitement parallèle
Le `BatchProcessor` utilise `ThreadPoolExecutor` pour traiter plusieurs produits en parallèle, ce qui améliore significativement les performances lors de la génération par lot.

### Mise en cache
Les résultats des appels API externes (THOT SEO, ValueSERP) peuvent être mis en cache pour éviter des appels répétés avec les mêmes paramètres.

## Dépannage

### Problèmes courants et solutions

#### 1. Erreur "API key not configured"
**Solution :** Vérifiez que les clés API sont correctement définies dans le fichier `.env`.

#### 2. Erreur lors de l'extraction des spécifications
**Solution :** Assurez-vous que le format du texte est compatible avec l'extracteur. Essayez de simplifier le format ou d'utiliser un format tabulaire standard.

#### 3. Erreur "401 Unauthorized" avec les API externes
**Solution :** Vérifiez que vos clés API sont valides et n'ont pas expiré.

#### 4. Erreur "Import Error" au démarrage
**Solution :** Vérifiez que toutes les dépendances sont installées avec `pip install -r requirements.txt`.

#### 5. Performances lentes lors de la génération par lot
**Solution :** Ajustez le paramètre `max_workers` dans `BatchProcessor` pour optimiser le nombre de threads en fonction de votre machine.

## Tests

Les tests unitaires et d'intégration peuvent être exécutés avec pytest :

```bash
pytest tests/
```

## Développement

### Lancement du serveur de développement
```bash
uvicorn main:app --reload
```

### Documentation API
Une documentation interactive de l'API est disponible à l'URL `/docs` lorsque le serveur est en cours d'exécution.

---
