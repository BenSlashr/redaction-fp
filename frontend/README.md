# RFP - Générateur de Fiches Produit

## Présentation du projet

RFP (Rédacteur de Fiches Produit) est une application web complète qui permet de générer automatiquement des descriptions de produits de haute qualité, optimisées pour le SEO et adaptées à différents publics cibles. L'application utilise des modèles d'IA avancés pour produire des descriptions professionnelles à partir d'informations de base sur les produits.

## Fonctionnalités principales

### 1. Génération de descriptions de produits
- Génération de descriptions détaillées et persuasives
- Intégration des spécifications techniques
- Personnalisation du ton et du style
- Optimisation SEO automatique
- Suggestions d'amélioration SEO

### 2. Ciblage de persona
- Adaptation du contenu à différents publics cibles
- Personas prédéfinis (professionnel, débutant, expert, entreprise, particulier)
- Personnalisation des personas

### 3. Analyse concurrentielle
- Analyse automatique des produits concurrents
- Extraction des arguments de vente uniques
- Identification des caractéristiques clés à mettre en avant
- Analyse des mots-clés utilisés par la concurrence

### 4. Guide SEO
- Recommandations SEO spécifiques au produit
- Suggestions de mots-clés et d'expressions à inclure
- Analyse des questions fréquentes à aborder
- Recommandations sur la longueur du contenu

### 5. Extraction automatique de spécifications
- Extraction de spécifications techniques à partir de texte brut
- Support de différents formats (tableaux, listes, etc.)
- Prévisualisation des spécifications extraites

### 6. Traitement par lot
- Génération simultanée de multiples descriptions
- Import de données produits via CSV
- Suivi de progression en temps réel
- Conservation de toutes les options de personnalisation

## Architecture technique

### Backend (Python/FastAPI)
- **FastAPI** : Framework API rapide et moderne
- **LangChain** : Orchestration des modèles d'IA et des chaînes de traitement
- **OpenAI API** : Modèles de langage avancés (GPT-4o)
- **THOT SEO API** : Analyse et recommandations SEO
- **ValueSERP API** : Analyse des résultats de recherche et de la concurrence

#### Services principaux
- `ProductDescriptionGenerator` : Génération de descriptions de produits
- `SelfImprovingChain` : Amélioration automatique des descriptions
- `ThotSeoService` : Intégration avec l'API THOT SEO
- `CompetitorAnalyzer` : Analyse des produits concurrents
- `SpecsExtractor` : Extraction de spécifications techniques
- `BatchProcessor` : Traitement par lot des descriptions

### Frontend (Next.js/React)
- **Next.js** : Framework React avec rendu côté serveur
- **Tailwind CSS** : Styling moderne et responsive
- **shadcn/ui** : Composants UI réutilisables
- **React Hook Form** : Gestion des formulaires
- **Axios** : Communication avec l'API backend

#### Pages principales
- `/` : Génération individuelle de descriptions
- `/batch` : Génération par lot via CSV
- `/history` : Historique des descriptions générées
- `/settings` : Configuration de l'application

## Installation et configuration

### Prérequis
- Python 3.10+
- Node.js 18+
- Clés API :
  - OpenAI API
  - THOT SEO API
  - ValueSERP API (optionnel)

### Installation du backend
1. Cloner le dépôt
2. Naviguer vers le dossier backend
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Créer un fichier `.env` avec les variables suivantes :
   ```
   OPENAI_API_KEY=votre_clé_openai
   THOT_API_KEY=votre_clé_thot
   VALUESERP_API_KEY=votre_clé_valueserp
   ```
5. Lancer le serveur :
   ```bash
   uvicorn main:app --reload
   ```

### Installation du frontend
1. Naviguer vers le dossier frontend
2. Installer les dépendances :
   ```bash
   npm install
   ```
3. Créer un fichier `.env.local` avec les variables suivantes :
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Lancer le serveur de développement :
   ```bash
   npm run dev
   ```

## Guide d'utilisation

### Génération individuelle
1. Accéder à la page d'accueil
2. Remplir les informations du produit :
   - Nom du produit
   - Description brève
   - Catégorie
   - Mots-clés
   - Spécifications techniques
3. Personnaliser les options :
   - Ton et style
   - Persona cible
   - Optimisation SEO
   - Analyse concurrentielle
   - Guide SEO
4. Cliquer sur "Générer la description"

### Extraction de spécifications
1. Dans le formulaire de génération, cliquer sur "Extraire les spécifications"
2. Coller le texte brut contenant les spécifications
3. Cliquer sur "Extraire"
4. Vérifier et ajuster les spécifications extraites
5. Cliquer sur "Utiliser ces spécifications"

### Génération par lot
1. Accéder à la page "Génération par lot"
2. Préparer un fichier CSV avec les colonnes suivantes :
   - name (obligatoire)
   - description
   - category
   - keywords (séparés par des virgules)
   - technical_specs (format JSON ou texte brut)
3. Télécharger le fichier CSV
4. Personnaliser les options globales
5. Cliquer sur "Générer les descriptions"
6. Suivre la progression en temps réel
7. Télécharger les résultats une fois terminé

## Personnalisation avancée

### Prompts personnalisés
Le système utilise un gestionnaire de prompts qui peut être personnalisé pour adapter les instructions données aux modèles d'IA. Les prompts sont stockés dans le dossier `prompts` du backend.

### Modèles de langage
Par défaut, l'application utilise GPT-4o, mais elle peut être configurée pour utiliser d'autres modèles OpenAI ou même d'autres fournisseurs de LLM compatibles avec LangChain.

### Styles et tons
L'application propose plusieurs styles et tons prédéfinis, mais vous pouvez créer vos propres combinaisons en modifiant les options dans le formulaire.

## Dépannage

### Problèmes courants
- **Erreur 401** : Vérifiez que vos clés API sont correctement configurées
- **Erreur lors de l'extraction des spécifications** : Assurez-vous que le format du texte est compatible
- **Génération par lot échoue** : Vérifiez le format de votre fichier CSV

### Logs
Les logs détaillés sont disponibles dans la console du backend et peuvent être configurés pour être plus ou moins verbeux en modifiant le niveau de log dans `main.py`.

## Développement futur

### Fonctionnalités planifiées
- Support multilingue
- Intégration avec d'autres plateformes e-commerce
- Amélioration de l'analyse concurrentielle
- Interface d'administration
- Historique des modifications

## Licence
Ce projet est sous licence propriétaire. Tous droits réservés.

---
