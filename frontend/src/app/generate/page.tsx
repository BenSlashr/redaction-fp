'use client';

import { useState } from 'react';
import Link from 'next/link';
import ToneSelector from '../components/ToneSelector';
import TemplateSelector from '../components/TemplateSelector';
import { SpecsExtractor } from '../../components/specs-extractor';
import { AIModelSelector } from '../../components/ai-model-selector';
import { api } from '../../lib/api';
import RAGFeature from '../components/RAGFeature';

// Types
interface TechnicalSpec {
  name: string;
  value: string;
}

interface ProductFormData {
  name: string;
  description: string;
  category: string;
  keywords: string;
  technicalSpecs: TechnicalSpec[];
}

interface ToneFormData {
  brandName: string;
  toneDescription: string;
  toneExample: string;
  personaTarget: string;
}

interface OptionsFormData {
  seoOptimization: boolean;
  competitorAnalysis: boolean;
  debugMode?: boolean;
  useSeoGuide?: boolean;
  seoGuideKeywords?: string;
  useAutoImprovement?: boolean;
  useRAG?: boolean;
  clientId?: string;
  selectedDocuments?: string[];
}

interface AIModelData {
  providerType: string;
  modelName: string;
}

export default function GeneratePage() {
  // États pour les différentes étapes du formulaire
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedContent, setGeneratedContent] = useState<string>('');
  const [competitorInsights, setCompetitorInsights] = useState<any>(null);
  const [seoGuideInsights, setSeoGuideInsights] = useState<any>(null);
  const [improvementResults, setImprovementResults] = useState<any>(null);
  const [aiModelInfo, setAiModelInfo] = useState<any>(null);
  
  // États pour les templates
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [selectedSections, setSelectedSections] = useState<string[]>([]);
  const [useTemplateMode, setUseTemplateMode] = useState<boolean>(false);

  // États pour les données du formulaire
  const [productData, setProductData] = useState<ProductFormData>({
    name: "",
    description: "",
    category: "",
    keywords: "",
    technicalSpecs: [{ name: "", value: "" }]
  });

  const [toneData, setToneData] = useState<ToneFormData>({
    brandName: "",
    toneDescription: "",
    toneExample: "",
    personaTarget: ""
  });

  const [optionsData, setOptionsData] = useState<OptionsFormData>({
    seoOptimization: true,
    competitorAnalysis: false,
    debugMode: false,
    useSeoGuide: false,
    seoGuideKeywords: "",
    useAutoImprovement: false,
    useRAG: false,
    clientId: "default",
    selectedDocuments: []
  });

  const [aiModelData, setAiModelData] = useState<AIModelData>({
    providerType: "OpenAI",
    modelName: "gpt-4o"
  });

  // Gestionnaires d'événements
  const handleProductChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProductData(prev => ({ ...prev, [name]: value }));
  };

  const handleToneChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setToneData(prev => ({ ...prev, [name]: value }));
  };

  const handleOptionsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked, value } = e.target;
    if (name === 'seoGuideKeywords') {
      setOptionsData(prev => ({ ...prev, [name]: value }));
    } else {
      setOptionsData(prev => ({ ...prev, [name]: checked }));
    }
  };

  const handleRAGSettingsChange = (settings: {
    useRAG: boolean;
    clientId: string;
    selectedDocuments?: string[];
  }) => {
    setOptionsData(prev => ({
      ...prev,
      useRAG: settings.useRAG,
      clientId: settings.clientId,
      selectedDocuments: settings.selectedDocuments || []
    }));
  };
  
  // Gestionnaire pour les changements de template
  const handleTemplateChange = (templateId: string, sections: string[]) => {
    setSelectedTemplate(templateId);
    setSelectedSections(sections);
  };
  
  // Gestionnaire pour activer/désactiver le mode template
  const handleTemplateModeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUseTemplateMode(e.target.checked);
  };

  const addTechnicalSpec = () => {
    setProductData(prev => ({
      ...prev,
      technicalSpecs: [...prev.technicalSpecs, { name: "", value: "" }]
    }));
  };

  const removeTechnicalSpec = (index: number) => {
    setProductData(prev => ({
      ...prev,
      technicalSpecs: prev.technicalSpecs.filter((_, i) => i !== index)
    }));
  };

  const handleTechnicalSpecChange = (index: number, field: 'name' | 'value', value: string) => {
    setProductData(prev => {
      const updatedSpecs = [...prev.technicalSpecs];
      updatedSpecs[index][field] = value;
      return { ...prev, technicalSpecs: updatedSpecs };
    });
  };

  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, 4));
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const analyzeCompetitors = async () => {
    if (!productData.name) {
      alert("Veuillez d'abord saisir le nom du produit");
      return;
    }

    try {
      // Préparation des données pour l'API
      const requestData = {
        product_name: productData.name,
        product_category: productData.category,
        search_query: `${productData.name} fiche technique caractéristiques`,
        debug_mode: optionsData.debugMode || false
      };

      // Appel à l'API backend
      const response = await fetch("http://localhost:8000/analyze-competitors", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const result = await response.json();

      // Stockage des résultats pour les utiliser lors de la génération
      setCompetitorInsights(result);

      alert("Analyse des concurrents terminée avec succès!");
    } catch (error) {
      console.error("Erreur lors de l'analyse des concurrents:", error);
      alert(`Erreur lors de l'analyse des concurrents: ${error}`);
    }
  };

  const getSeoGuide = async () => {
    if (!optionsData.seoGuideKeywords) {
      alert("Veuillez d'abord saisir des mots-clés pour le guide SEO");
      return;
    }

    try {
      // Préparation des données pour l'API
      const requestData = {
        keywords: optionsData.seoGuideKeywords,
        debug_mode: optionsData.debugMode || false
      };

      // Appel à l'API backend
      const response = await fetch("http://localhost:8000/get-seo-guide", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const result = await response.json();

      // Stockage des résultats pour les utiliser lors de la génération
      setSeoGuideInsights(result);

      alert("Guide SEO récupéré avec succès!");
    } catch (error) {
      console.error("Erreur lors de la récupération du guide SEO:", error);
      alert(`Erreur lors de la récupération du guide SEO: ${error}`);
    }
  };

  const generateProductDescription = async () => {
    setIsGenerating(true);

    try {
      // Vérifier si l'analyse concurrentielle est activée mais pas encore effectuée
      if (optionsData.competitorAnalysis && !competitorInsights) {
        const shouldAnalyze = confirm("L'analyse des concurrents est activée mais n'a pas encore été effectuée. Voulez-vous l'effectuer maintenant avant de générer le contenu ?");

        if (shouldAnalyze) {
          await analyzeCompetitors();
        }
      }

      // Vérifier si le guide SEO est activé mais pas encore récupéré
      if (optionsData.useSeoGuide && optionsData.seoGuideKeywords && !seoGuideInsights) {
        const shouldGetSeoGuide = confirm("Le guide SEO est activé mais n'a pas encore été récupéré. Voulez-vous le récupérer maintenant avant de générer le contenu ?");

        if (shouldGetSeoGuide) {
          await getSeoGuide();
        }
      }

      // Préparation des données pour l'API
      const baseRequestData = {
        product_info: {
          name: productData.name,
          description: productData.description,
          category: productData.category,
          keywords: productData.keywords.split(",").map(k => k.trim()),
          technical_specs: productData.technicalSpecs.reduce((acc, spec) => {
            if (spec.name && spec.value) {
              acc[spec.name] = spec.value;
            }
            return acc;
          }, {} as Record<string, string>)
        },
        tone_style: {
          brand_name: toneData.brandName,
          tone_description: toneData.toneDescription,
          tone_example: toneData.toneExample,
          persona_target: toneData.personaTarget
        },
        seo_optimization: optionsData.seoOptimization,
        competitor_analysis: optionsData.competitorAnalysis,
        competitor_insights: competitorInsights,
        use_seo_guide: optionsData.useSeoGuide,
        seo_guide_keywords: optionsData.seoGuideKeywords,
        seo_guide_insights: seoGuideInsights,
        auto_improve: optionsData.useAutoImprovement,
        ai_provider: {
          provider_type: aiModelData.providerType,
          model_name: aiModelData.modelName
        },
        use_rag: optionsData.useRAG,
        client_id: optionsData.clientId,
        document_ids: optionsData.selectedDocuments
      };

      // Appel à l'API backend
      console.log("Données envoyées à l'API:", baseRequestData);

      try {
        // Utiliser l'API client au lieu de fetch directement
        let result;
        
        // Si le mode template est activé, utiliser l'endpoint de génération avec template
        if (useTemplateMode && selectedTemplate) {
          const templateRequestData = {
            ...baseRequestData,
            template_id: selectedTemplate,
            sections: selectedSections
          };
          result = await api.generateWithTemplate(templateRequestData);
        }
        // Si RAG est activé, utiliser l'endpoint RAG
        else if (optionsData.useRAG) {
          result = await api.generateWithRAG(baseRequestData);
        } else {
          result = await api.generateDescription(baseRequestData);
        }

        // Stocker les informations sur le modèle d'IA utilisé
        setAiModelInfo(result.ai_provider);

        if (optionsData.useAutoImprovement) {
          // Stocker les résultats de l'auto-amélioration
          setImprovementResults(result);

          // Formatage du contenu généré avec la version améliorée
          let formattedContent = `# ${productData.name}\n\n`;
          
          // Vérifier si le résultat est au format template (avec sections)
          if (typeof result.product_description === 'object' && result.product_description.sections) {
            // Format template: concaténer les sections avec la version améliorée si disponible
            const sections = result.product_description.sections;
            sections.forEach((section: any) => {
              formattedContent += `## ${section.name}\n\n${section.content}\n\n`;
            });
          } else {
            // Format standard: utiliser la version améliorée ou standard
            formattedContent += result.improved_description || result.product_description;
          }

          setGeneratedContent(formattedContent);
        } else {
          // Formatage du contenu généré
          let formattedContent = `# ${productData.name}\n\n`;
          
          // Vérifier si le résultat est au format template (avec sections)
          if (typeof result.product_description === 'object' && result.product_description.sections) {
            // Format template: concaténer les sections
            const sections = result.product_description.sections;
            sections.forEach((section: any) => {
              formattedContent += `## ${section.name}\n\n${section.content}\n\n`;
            });
          } else {
            // Format standard: utiliser directement la description
            formattedContent += result.product_description;
          }

          // Ajout des suggestions SEO si disponibles
          if (result.seo_suggestions && result.seo_suggestions.length > 0) {
            formattedContent += "\n\n## Suggestions SEO\n";
            result.seo_suggestions.forEach((suggestion: string) => {
              formattedContent += `- ${suggestion}\n`;
            });
          }

          // Ajout des insights concurrentiels si disponibles
          if (result.competitor_insights && result.competitor_insights.length > 0) {
            formattedContent += "\n\n## Insights concurrentiels\n";
            result.competitor_insights.forEach((insight: string) => {
              formattedContent += `- ${insight}\n`;
            });
          }

          setGeneratedContent(formattedContent);
        }

        setIsGenerating(false);
        setCurrentStep(4);
      } catch (error) {
        console.error("Erreur lors de l'appel à l'API:", error);

        // En cas d'erreur, on utilise le contenu simulé comme fallback
        setGeneratedContent(`# ${productData.name}

${productData.description}

## Caractéristiques principales
${productData.technicalSpecs.filter(spec => spec.name && spec.value)
  .map(spec => `- **${spec.name}**: ${spec.value}`).join('\n')}

## Pourquoi choisir ce produit ?
Ce produit offre une expérience utilisateur exceptionnelle grâce à ses fonctionnalités avancées et sa qualité supérieure. Idéal pour les utilisateurs exigeants qui recherchent performance et fiabilité.

## Spécifications techniques détaillées
${productData.technicalSpecs.filter(spec => spec.name && spec.value)
  .map(spec => `- **${spec.name}**: ${spec.value}`).join('\n')}

*Note: Contenu de secours généré localement suite à une erreur de connexion avec l'API.*`);

        setIsGenerating(false);
        setCurrentStep(4);
      }
    } catch (error) {
      console.error("Erreur lors de la génération:", error);
      setIsGenerating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await generateProductDescription();
  };

  // Rendu conditionnel en fonction de l'étape actuelle
  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold">Informations sur le produit</h2>

            <div className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Nom du produit *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={productData.name}
                  onChange={handleProductChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                  required
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description brève *
                </label>
                <textarea
                  id="description"
                  name="description"
                  value={productData.description}
                  onChange={handleProductChange}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                  required
                />
              </div>

              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Catégorie
                </label>
                <input
                  type="text"
                  id="category"
                  name="category"
                  value={productData.category}
                  onChange={handleProductChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                />
              </div>

              <div>
                <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Mots-clés (séparés par des virgules)
                </label>
                <input
                  type="text"
                  id="keywords"
                  name="keywords"
                  value={productData.keywords}
                  onChange={handleProductChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                  placeholder="ex: smartphone, android, photo, batterie"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Spécifications techniques
                  </label>
                  <button
                    type="button"
                    onClick={addTechnicalSpec}
                    className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                  >
                    + Ajouter une spécification
                  </button>
                </div>

                {/* Extracteur de spécifications */}
                <div className="mb-4">
                  <SpecsExtractor
                    onSpecsExtracted={(specs) => {
                      // Remplacer les spécifications existantes par celles extraites
                      setProductData(prev => ({
                        ...prev,
                        technicalSpecs: specs.length > 0 ? specs : [{ name: "", value: "" }]
                      }));
                    }}
                    className="mb-4"
                  />
                </div>

                {productData.technicalSpecs.map((spec, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={spec.name}
                      onChange={(e) => handleTechnicalSpecChange(index, 'name', e.target.value)}
                      placeholder="Nom (ex: Processeur)"
                      className="w-1/2 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                    />
                    <input
                      type="text"
                      value={spec.value}
                      onChange={(e) => handleTechnicalSpecChange(index, 'value', e.target.value)}
                      placeholder="Valeur (ex: Snapdragon 888)"
                      className="w-1/2 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                    />
                    {index > 0 && (
                      <button
                        type="button"
                        onClick={() => removeTechnicalSpec(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold">Ton et audience cible</h2>

            <div className="space-y-4">
              <ToneSelector
                onToneSelect={(toneData) => {
                  setToneData({
                    brandName: toneData.brand_name || "",
                    toneDescription: toneData.tone_description || "",
                    toneExample: toneData.tone_example || "",
                    personaTarget: toneData.persona_target || ""
                  });
                }}
              />

              <div>
                <label htmlFor="personaTarget" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Persona cible (lecteur)
                </label>
                <textarea
                  id="personaTarget"
                  name="personaTarget"
                  value={toneData.personaTarget}
                  onChange={handleToneChange}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                  placeholder="Décrivez le public cible de votre description (ex: professionnels du secteur, débutants, experts techniques, décideurs d'entreprise, particuliers...)"
                />
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Cette information aidera l'IA à adapter le langage, le ton et les arguments pour ce public spécifique.
                </p>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold">Options de génération</h2>

            <div className="space-y-4">
              {/* Sélecteur de modèle d'IA */}
              <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium mb-3">Modèle d'IA</h3>
                <AIModelSelector
                  onSelect={(providerType, modelName) => {
                    setAiModelData({
                      providerType,
                      modelName
                    });
                  }}
                  defaultProvider={aiModelData.providerType}
                  defaultModel={aiModelData.modelName}
                />
              </div>

              {/* Template Feature */}
              <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center mb-3">
                  <input
                    type="checkbox"
                    id="useTemplateMode"
                    name="useTemplateMode"
                    checked={useTemplateMode}
                    onChange={handleTemplateModeChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="useTemplateMode" className="ml-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Utiliser un template de fiche produit
                  </label>
                </div>
                
                {useTemplateMode && (
                  <div className="mt-2">
                    <TemplateSelector onTemplateChange={handleTemplateChange} />
                  </div>
                )}
              </div>
              
              {/* RAG Feature */}
              <div className="mb-6">
                <RAGFeature
                  onRAGSettingsChange={handleRAGSettingsChange}
                  defaultClientId={optionsData.clientId}
                />
              </div>

              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id="seoOptimization"
                    name="seoOptimization"
                    type="checkbox"
                    checked={optionsData.seoOptimization}
                    onChange={handleOptionsChange}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="seoOptimization" className="font-medium text-gray-700 dark:text-gray-300">
                    Optimisation SEO
                  </label>
                  <p className="text-gray-500 dark:text-gray-400">
                    Optimise le contenu pour les moteurs de recherche en utilisant les mots-clés fournis
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id="competitorAnalysis"
                    name="competitorAnalysis"
                    type="checkbox"
                    checked={optionsData.competitorAnalysis}
                    onChange={handleOptionsChange}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="competitorAnalysis" className="font-medium text-gray-700 dark:text-gray-300">
                    Analyse des concurrents
                  </label>
                  <p className="text-gray-500 dark:text-gray-400">
                    Analyse les fiches produit concurrentes pour créer un contenu compétitif
                  </p>
                </div>
              </div>

              {optionsData.competitorAnalysis && (
                <div className="mt-4 space-y-4">
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="debugMode"
                        name="debugMode"
                        type="checkbox"
                        checked={optionsData.debugMode || false}
                        onChange={handleOptionsChange}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                    </div>
                    <div className="ml-3 text-sm">
                      <label htmlFor="debugMode" className="font-medium text-gray-700 dark:text-gray-300">
                        Mode debug
                      </label>
                      <p className="text-gray-500 dark:text-gray-400">
                        Affiche des informations détaillées sur l'analyse des concurrents
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={analyzeCompetitors}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
                  >
                    Analyser les concurrents
                  </button>

                  {competitorInsights && (
                    <div className="mt-2 text-sm text-green-600 dark:text-green-400">
                      ✓ Analyse des concurrents effectuée
                    </div>
                  )}
                </div>
              )}

              <div className="flex items-start mt-6">
                <div className="flex items-center h-5">
                  <input
                    id="useSeoGuide"
                    name="useSeoGuide"
                    type="checkbox"
                    checked={optionsData.useSeoGuide || false}
                    onChange={handleOptionsChange}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="useSeoGuide" className="font-medium text-gray-700 dark:text-gray-300">
                    Guide SEO
                  </label>
                  <p className="text-gray-500 dark:text-gray-400">
                    Utilise un guide SEO pour optimiser le contenu avec des mots-clés pertinents
                  </p>
                </div>
              </div>

              {optionsData.useSeoGuide && (
                <div className="mt-4 space-y-4">
                  <div>
                    <label htmlFor="seoGuideKeywords" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Mots-clés pour le guide SEO
                    </label>
                    <input
                      type="text"
                      id="seoGuideKeywords"
                      name="seoGuideKeywords"
                      value={optionsData.seoGuideKeywords || ""}
                      onChange={handleOptionsChange}
                      placeholder="ex: logiciel IA, intelligence artificielle"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    />
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      Entrez les mots-clés principaux pour lesquels vous souhaitez optimiser votre contenu
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={getSeoGuide}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
                  >
                    Récupérer le guide SEO
                  </button>

                  {seoGuideInsights && (
                    <div className="mt-2 text-sm text-green-600 dark:text-green-400">
                      ✓ Guide SEO récupéré avec succès
                    </div>
                  )}
                </div>
              )}

              <div className="flex items-start mt-6">
                <div className="flex items-center h-5">
                  <input
                    id="useAutoImprovement"
                    name="useAutoImprovement"
                    type="checkbox"
                    checked={optionsData.useAutoImprovement || false}
                    onChange={handleOptionsChange}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="useAutoImprovement" className="font-medium text-gray-700 dark:text-gray-300">
                    Auto-amélioration
                  </label>
                  <p className="text-gray-500 dark:text-gray-400">
                    Utilise une chaîne d'auto-évaluation et d'amélioration pour optimiser la qualité du contenu
                  </p>
                </div>
              </div>

              {optionsData.useAutoImprovement && (
                <div className="mt-2 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <p className="text-sm text-yellow-700 dark:text-yellow-400">
                    <span className="font-medium">Note:</span> L'auto-amélioration utilise plusieurs modèles d'IA en séquence pour évaluer et améliorer le contenu. Ce processus peut prendre plus de temps mais produit des descriptions de meilleure qualité.
                  </p>
                </div>
              )}

              <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
                <h3 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">Résumé de votre demande</h3>
                <ul className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
                  <li><strong>Produit:</strong> {productData.name}</li>
                  <li><strong>Catégorie:</strong> {productData.category || 'Non spécifiée'}</li>
                  <li><strong>Spécifications:</strong> {productData.technicalSpecs.filter(s => s.name && s.value).length} spécification(s)</li>
                  <li><strong>Ton:</strong> {toneData.toneDescription || 'Standard'}</li>
                  <li><strong>Options:</strong> {[
                    optionsData.seoOptimization ? 'Optimisation SEO' : '',
                    optionsData.competitorAnalysis ? 'Analyse concurrentielle' : '',
                    optionsData.useRAG ? 'Enrichissement données client' : '',
                    optionsData.useSeoGuide ? 'Guide SEO' : '',
                    optionsData.useAutoImprovement ? 'Auto-amélioration' : ''
                  ].filter(Boolean).join(', ') || 'Aucune'}</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold">Description générée</h2>

            {/* Informations sur le modèle d'IA utilisé */}
            {aiModelInfo && (
              <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm">
                <p className="font-medium">Généré avec {aiModelInfo.provider} {aiModelInfo.model}</p>
                {aiModelInfo.pricing && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    Coût estimé: {aiModelInfo.pricing.input}$ / 1K tokens (entrée) • {aiModelInfo.pricing.output}$ / 1K tokens (sortie)
                  </p>
                )}
              </div>
            )}

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
              <div className="prose dark:prose-invert max-w-none">
                {generatedContent.split('\n').map((line, index) => {
                  // Traitement des titres
                  if (line.startsWith('# ')) {
                    return <h1 key={index} className="text-2xl font-bold mb-4">{line.substring(2)}</h1>;
                  } else if (line.startsWith('## ')) {
                    return <h2 key={index} className="text-xl font-semibold mt-6 mb-3">{line.substring(3)}</h2>;
                  } else if (line.startsWith('### ')) {
                    return <h3 key={index} className="text-lg font-medium mt-4 mb-2">{line.substring(4)}</h3>;
                  }
                  // Traitement des listes
                  else if (line.startsWith('- ')) {
                    return <li key={index} className="ml-4">{line.substring(2)}</li>;
                  }
                  // Traitement du texte en gras
                  else if (line.includes('**')) {
                    const parts = line.split('**');
                    return (
                      <p key={index} className="mb-2">
                        {parts.map((part, i) => {
                          return i % 2 === 0 ? part : <strong key={i}>{part}</strong>;
                        })}
                      </p>
                    );
                  }
                  // Traitement du texte en italique
                  else if (line.startsWith('*') && line.endsWith('*')) {
                    return <p key={index} className="text-sm italic text-gray-600 dark:text-gray-400 mt-4">{line.substring(1, line.length - 1)}</p>;
                  }
                  // Traitement des paragraphes normaux
                  else if (line.trim() !== '') {
                    return <p key={index} className="mb-2">{line}</p>;
                  }
                  // Traitement des lignes vides
                  else {
                    return <br key={index} />;
                  }
                })}
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => {
                  navigator.clipboard.writeText(generatedContent);
                  alert("Contenu copié dans le presse-papiers !");
                }}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
              >
                Copier le contenu
              </button>
              <button
                type="button"
                onClick={() => setCurrentStep(1)}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg"
              >
                Générer une nouvelle description
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <header className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <Link href="/" className="text-blue-600 dark:text-blue-400 hover:underline flex items-center">
              <span className="mr-2">←</span> Retour à l'accueil
            </Link>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Étape {currentStep} sur {currentStep === 4 ? '3' : '3'}
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Générateur de Fiches Produit
          </h1>
        </header>

        <main className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 md:p-8 max-w-4xl mx-auto">
          {/* Utilisation de div au lieu de form pour éviter la soumission automatique */}
          <div>
            {renderStep()}

            <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700 flex justify-between">
              {currentStep > 1 && currentStep !== 4 && (
                <button
                  type="button"
                  onClick={prevStep}
                  className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Précédent
                </button>
              )}

              {currentStep < 3 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg ml-auto"
                >
                  Suivant
                </button>
              ) : currentStep === 3 ? (
                <button
                  type="button"
                  onClick={generateProductDescription}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg ml-auto"
                  disabled={isGenerating}
                >
                  {isGenerating ? 'Génération...' : 'Générer la fiche produit'}
                </button>
              ) : null}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
