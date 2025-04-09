# RFP Frontend - Documentation Technique

## Guide de démarrage rapide

### Installation et configuration

```bash
# Installer les dépendances
npm install

# Créer un fichier .env.local avec l'URL de l'API
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Lancer le serveur de développement
npm run dev
```

### Vérification de l'installation

Une fois le serveur démarré, vous pouvez vérifier que tout fonctionne correctement :

1. Ouvrez http://localhost:3000 dans votre navigateur
2. Vérifiez que la page d'accueil s'affiche correctement
3. Testez le formulaire de génération de description avec un exemple simple

## Structure du projet

```
frontend/
├── src/
│   ├── app/                 # Pages de l'application (Next.js App Router)
│   │   ├── page.tsx         # Page d'accueil (génération individuelle)
│   │   ├── batch/           # Page de génération par lot
│   │   │   └── page.tsx     # Interface de génération par lot
│   │   ├── history/         # Historique des générations
│   │   │   └── page.tsx     # Interface d'historique
│   │   └── settings/        # Paramètres de l'application
│   │       └── page.tsx     # Interface des paramètres
│   ├── components/          # Composants réutilisables
│   │   ├── ui/              # Composants UI de base (shadcn/ui)
│   │   ├── specs-extractor/ # Composant d'extraction de spécifications
│   │   │   └── index.tsx    # Interface d'extraction
│   │   ├── tone-selector/   # Sélecteur de ton et style
│   │   │   └── index.tsx    # Interface de sélection
│   │   └── product-form/    # Formulaire de produit
│   │       └── index.tsx    # Interface du formulaire
│   ├── lib/                 # Utilitaires et services
│   │   ├── api.ts           # Service d'API
│   │   ├── types.ts         # Types TypeScript
│   │   └── utils.ts         # Fonctions utilitaires
│   └── styles/              # Styles globaux
│       └── globals.css      # CSS global (Tailwind)
├── public/                  # Fichiers statiques
├── next.config.js           # Configuration Next.js
├── package.json             # Dépendances et scripts
├── tailwind.config.js       # Configuration Tailwind CSS
└── .env.local               # Variables d'environnement
```

## Technologies utilisées

- **Next.js 15** : Framework React avec rendu côté serveur
- **React 19** : Bibliothèque UI
- **Tailwind CSS 4** : Framework CSS utilitaire
- **shadcn/ui** : Composants UI réutilisables basés sur Radix UI
- **React Hook Form** : Gestion des formulaires
- **Axios** : Client HTTP pour les requêtes API
- **TypeScript** : Typage statique

## Composants principaux

### 1. Page d'accueil (`app/page.tsx`)

Page principale pour la génération individuelle de descriptions de produits.

**Fonctionnalités :**
- Formulaire complet pour les informations produit
- Sélection du ton et du style
- Options d'optimisation SEO
- Prévisualisation de la description générée
- Extraction de spécifications techniques

### 2. Page de génération par lot (`app/batch/page.tsx`)

Interface pour la génération de descriptions en lot via un fichier CSV.

**Fonctionnalités :**
- Upload de fichier CSV
- Configuration globale du ton et du style
- Options d'optimisation SEO
- Suivi de progression en temps réel
- Téléchargement des résultats

### 3. Extracteur de spécifications (`components/specs-extractor/index.tsx`)

Composant pour extraire automatiquement les spécifications techniques à partir de texte brut.

**Fonctionnalités :**
- Champ de texte pour coller les spécifications
- Extraction automatique via l'API
- Prévisualisation des spécifications extraites
- Boutons pour coller depuis le presse-papiers et effacer

### 4. Sélecteur de ton (`components/tone-selector/index.tsx`)

Composant pour sélectionner le ton, le style et le persona cible.

**Fonctionnalités :**
- Sélection du ton (Professionnel, Enthousiaste, etc.)
- Sélection du style (Informatif, Persuasif, etc.)
- Sélection du persona cible (Professionnel, Débutant, etc.)
- Personnalisation des options

## Services API

### Service API principal (`lib/api.ts`)

Service pour communiquer avec l'API backend.

**Méthodes principales :**

```typescript
// Génération de description individuelle
async function generateDescription(data: ProductDescriptionRequest): Promise<ProductResponse> {
  const response = await axios.post(`${API_URL}/generate-product-description`, data);
  return response.data;
}

// Génération par lot
async function batchGenerate(formData: FormData): Promise<BatchResponse> {
  const response = await axios.post(`${API_URL}/batch-generate`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

// Extraction de spécifications
async function extractSpecs(rawText: string): Promise<Record<string, string>> {
  const response = await axios.post(`${API_URL}/extract-specs`, { raw_text: rawText });
  return response.data.specs;
}

// Récupération du guide SEO
async function getSeoGuide(keywords: string): Promise<SeoGuideResponse> {
  const response = await axios.post(`${API_URL}/get-seo-guide`, { keywords });
  return response.data;
}
```

## Types principaux

Les types TypeScript principaux sont définis dans `lib/types.ts` :

```typescript
// Informations du produit
interface ProductInfo {
  name: string;
  description: string;
  category: string;
  keywords: string[];
  technical_specs: Record<string, string>;
}

// Style et ton
interface ToneStyle {
  tone: string;
  style: string;
  persona_target?: string;
}

// Requête de génération de description
interface ProductDescriptionRequest {
  product_info: ProductInfo;
  tone_style: ToneStyle;
  seo_optimization: boolean;
  competitor_analysis: boolean;
  use_seo_guide: boolean;
  seo_guide_keywords?: string;
  auto_improve: boolean;
}

// Réponse de génération de description
interface ProductResponse {
  product_description: string;
  seo_suggestions: string[];
  competitor_insights: any[];
}

// Réponse de génération par lot
interface BatchResponse {
  results: {
    product_name: string;
    status: 'success' | 'error';
    product_description?: string;
    improved_description?: string;
    error?: string;
  }[];
}
```

## Gestion des formulaires

Les formulaires utilisent React Hook Form pour la validation et la gestion des données :

```typescript
// Exemple d'utilisation de React Hook Form
const { register, handleSubmit, formState: { errors } } = useForm<ProductFormData>({
  defaultValues: {
    product_info: {
      name: '',
      description: '',
      category: '',
      keywords: [],
      technical_specs: {}
    },
    tone_style: {
      tone: 'Professionnel',
      style: 'Informatif'
    },
    seo_optimization: true,
    competitor_analysis: false,
    use_seo_guide: false,
    auto_improve: true
  }
});

const onSubmit = async (data: ProductFormData) => {
  try {
    setLoading(true);
    const result = await api.generateDescription(data);
    setResult(result);
  } catch (error) {
    setError('Une erreur est survenue lors de la génération');
  } finally {
    setLoading(false);
  }
};
```

## Composants UI

Le projet utilise shadcn/ui, une collection de composants UI réutilisables basés sur Radix UI et stylisés avec Tailwind CSS :

- `Button` : Boutons d'action
- `Input` : Champs de saisie
- `Textarea` : Zones de texte
- `Select` : Menus déroulants
- `Checkbox` : Cases à cocher
- `Tabs` : Onglets
- `Toast` : Notifications
- `Progress` : Barres de progression
- `Card` : Cartes pour afficher du contenu

## Gestion des erreurs

Le frontend gère les erreurs à plusieurs niveaux :

1. **Validation des formulaires** : React Hook Form valide les données avant l'envoi
2. **Gestion des erreurs API** : Try/catch pour capturer les erreurs de requête
3. **Affichage des erreurs** : Composant Toast pour afficher les messages d'erreur
4. **Gestion des états de chargement** : États de chargement pour informer l'utilisateur

## Optimisation des performances

### Code splitting

Next.js effectue automatiquement le code splitting pour charger uniquement le code nécessaire à chaque page.

### Mise en cache

Les résultats de génération peuvent être mis en cache côté client pour éviter des appels API répétés.

### Lazy loading

Les composants lourds sont chargés en lazy loading pour améliorer les performances initiales.

## Déploiement

### Build de production

```bash
# Générer la build de production
npm run build

# Démarrer le serveur de production
npm run start
```

### Environnements

- **Développement** : Utilise `.env.local` avec `NEXT_PUBLIC_API_URL=http://localhost:8000`
- **Production** : Utilise `.env.production` avec l'URL de l'API de production

## Dépannage

### Problèmes courants et solutions

#### 1. Erreur "Failed to fetch" lors des appels API
**Solution :** Vérifiez que le serveur backend est en cours d'exécution et que l'URL de l'API est correctement configurée dans `.env.local`.

#### 2. Problèmes d'affichage des composants UI
**Solution :** Assurez-vous que Tailwind CSS est correctement configuré et que les classes sont correctement appliquées.

#### 3. Erreur lors du téléchargement de fichiers CSV
**Solution :** Vérifiez que le format du fichier CSV est correct et que toutes les colonnes requises sont présentes.

#### 4. Problèmes de performance
**Solution :** Utilisez l'outil de développement React pour identifier les composants qui se re-render inutilement et optimisez-les avec `useMemo` et `useCallback`.

---

© 2025 RFP - Générateur de Fiches Produit
