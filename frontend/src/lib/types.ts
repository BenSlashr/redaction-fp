// Types pour les informations produit
export interface ProductInfo {
  name: string;
  description: string;
  category?: string;
  keywords?: string[];
  technical_specs?: Record<string, string>;
}

// Types pour le ton et le style
export interface ToneStyle {
  tone?: string;
  style?: string;
  persona_target?: string;
}

// Types pour le fournisseur d'IA
export interface AIProvider {
  provider_type: string;
  model_name: string;
}

// Types pour la requête de génération de description
export interface ProductDescriptionRequest {
  product_info: ProductInfo;
  tone_style: ToneStyle;
  seo_optimization?: boolean;
  competitor_analysis?: boolean;
  use_seo_guide?: boolean;
  seo_guide_keywords?: string;
  auto_improve?: boolean;
  ai_provider?: AIProvider;
}

// Types pour la réponse de génération de description
export interface ProductResponse {
  product_description: string;
  seo_suggestions?: string[];
  competitor_insights?: any[];
  ai_provider?: {
    provider: string;
    model: string;
    pricing: {
      input: number;
      output: number;
      currency: string;
      unit: string;
    };
  };
}

// Types pour les modèles d'IA
export interface AIModel {
  id: string;
  name: string;
  description: string;
}

// Types pour les informations sur les fournisseurs d'IA
export interface AIProviderInfo {
  name: string;
  models: AIModel[];
}

// Types pour la réponse de récupération des fournisseurs d'IA
export interface AIProvidersResponse {
  providers: AIProviderInfo[];
}

// Types pour le guide SEO
export interface SeoGuideRequest {
  keywords: string;
}

export interface SeoGuideResponse {
  required_keywords: any[];
  complementary_keywords: any[];
  expressions: string[];
  questions: string[];
  word_count: number;
  target_score: number;
  max_overoptimization: number;
  competition: any[];
}

// Types pour l'analyse des concurrents
export interface CompetitorAnalysisRequest {
  product_name: string;
  product_category: string;
  search_query?: string;
}

export interface CompetitorAnalysisResponse {
  key_features: string[];
  unique_selling_points: string[];
  common_specifications: string[];
  content_structure: string;
  seo_keywords: string[];
}

// Types pour l'extraction des spécifications
export interface ExtractSpecsRequest {
  raw_text: string;
}

export interface ExtractSpecsResponse {
  specs: Record<string, string>;
}

// Types pour la génération par lot
export interface BatchProductRequest {
  products: ProductInfo[];
  tone_style: ToneStyle;
  seo_optimization: boolean;
  use_auto_improvement: boolean;
  competitor_analysis: boolean;
  use_seo_guide: boolean;
  ai_provider?: AIProvider;
}

export interface BatchProductResponse {
  results: {
    product_name: string;
    status: 'success' | 'error';
    product_description?: string;
    improved_description?: string;
    error?: string;
  }[];
}
