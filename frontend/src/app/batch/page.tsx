'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { useToast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Upload, FileText, Download, ArrowLeft, Check, AlertCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';

// Types pour les données CSV
interface ProductRow {
  name: string;
  description: string;
  category: string;
  keywords: string;
  technicalSpecs: Record<string, string>;
  [key: string]: any;
}

interface BatchGenerationResult {
  productName: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  content?: string;
  error?: string;
}

interface BatchResult {
  product_name: string;
  status: string;
  product_description?: string;
  improved_description?: string;
  original_description?: string;
  seo_suggestions?: string[];
  competitor_insights?: string[];
  evaluation?: Record<string, any>;
  error?: string;
}

export default function BatchPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [csvData, setCsvData] = useState<ProductRow[]>([]);
  const [csvHeaders, setCsvHeaders] = useState<string[]>([]);
  const [mappings, setMappings] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState('upload');
  const [results, setResults] = useState<BatchGenerationResult[]>([]);
  const [progress, setProgress] = useState(0);
  const [selectedToneId, setSelectedToneId] = useState('professional');
  const [personaTarget, setPersonaTarget] = useState('');
  const [useSeoOptimization, setUseSeoOptimization] = useState(true);
  const [useAutoImprovement, setUseAutoImprovement] = useState(false);
  const [useCompetitorAnalysis, setUseCompetitorAnalysis] = useState(false);
  const [useSeoGuide, setUseSeoGuide] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  
  // Fonction pour gérer le téléchargement du modèle CSV
  const handleDownloadTemplate = () => {
    const headers = ['name', 'description', 'category', 'keywords', 'spec_name_1', 'spec_value_1', 'spec_name_2', 'spec_value_2'];
    const csvContent = [
      headers.join(','),
      '"Smartphone XYZ","Un smartphone puissant avec une excellente autonomie","Électronique","smartphone,mobile,technologie","Écran","6.7 pouces OLED","Batterie","5000 mAh"',
      '"Chaise de bureau","Chaise ergonomique pour un confort optimal","Mobilier","chaise,bureau,ergonomie","Matériau","Cuir synthétique","Poids max","150 kg"'
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'template_produits.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  // Fonction pour gérer l'upload du fichier CSV
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };
  
  // Fonction pour analyser le fichier CSV
  const parseCSV = (text: string): { headers: string[], data: any[] } => {
    // Fonction pour parser une ligne CSV en tenant compte des guillemets
    const parseCSVLine = (line: string): string[] => {
      const result: string[] = [];
      let current = '';
      let inQuotes = false;
      
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"' && (i === 0 || line[i-1] !== '\\')) {
          inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
          result.push(current);
          current = '';
        } else {
          current += char;
        }
      }
      
      if (current) {
        result.push(current);
      }
      
      return result.map(val => val.replace(/^"|"$/g, ''));
    };
    
    const lines = text.split(/\r\n|\n/);
    const headers = parseCSVLine(lines[0]);
    
    const data = lines.slice(1)
      .filter(line => line.trim())
      .map(line => {
        const values = parseCSVLine(line);
        const row: Record<string, any> = {};
        
        headers.forEach((header, index) => {
          if (index < values.length) {
            row[header] = values[index];
          } else {
            row[header] = '';
          }
        });
        
        return row;
      });
    
    return { headers, data };
  };
  
  // Fonction pour traiter le fichier CSV
  const handleProcessCSV = async () => {
    if (!file) return;
    
    setIsUploading(true);
    
    try {
      const text = await file.text();
      const { headers, data } = parseCSV(text);
      
      // Initialiser les mappings par défaut
      const defaultMappings: Record<string, string> = {};
      headers.forEach(header => {
        // Essayer de faire correspondre les en-têtes avec nos champs attendus
        const lowerHeader = header.toLowerCase();
        if (lowerHeader.includes('name') || lowerHeader.includes('nom')) {
          defaultMappings[header] = 'name';
        } else if (lowerHeader.includes('desc')) {
          defaultMappings[header] = 'description';
        } else if (lowerHeader.includes('cat')) {
          defaultMappings[header] = 'category';
        } else if (lowerHeader.includes('key') || lowerHeader.includes('mot')) {
          defaultMappings[header] = 'keywords';
        } else if (lowerHeader.includes('spec_name') || lowerHeader.includes('spec_nom')) {
          defaultMappings[header] = 'spec_name';
        } else if (lowerHeader.includes('spec_value') || lowerHeader.includes('spec_valeur')) {
          defaultMappings[header] = 'spec_value';
        }
      });
      
      setMappings(defaultMappings);
      setCsvHeaders(headers);
      
      // Transformer les données pour notre format
      const transformedData = data.map(row => {
        const product: ProductRow = {
          name: '',
          description: '',
          category: '',
          keywords: '',
          technicalSpecs: {}
        };
        
        // Extraire les spécifications techniques
        const specNames: string[] = [];
        const specValues: string[] = [];
        
        headers.forEach(header => {
          if (defaultMappings[header] === 'spec_name' && row[header]) {
            specNames.push(row[header]);
          } else if (defaultMappings[header] === 'spec_value' && row[header]) {
            specValues.push(row[header]);
          }
        });
        
        // Créer les paires de spécifications
        for (let i = 0; i < Math.min(specNames.length, specValues.length); i++) {
          if (specNames[i] && specValues[i]) {
            product.technicalSpecs[specNames[i]] = specValues[i];
          }
        }
        
        // Remplir les autres champs
        headers.forEach(header => {
          const mapping = defaultMappings[header];
          if (mapping && mapping !== 'spec_name' && mapping !== 'spec_value') {
            product[mapping] = row[header];
          }
        });
        
        return product;
      });
      
      setCsvData(transformedData);
      setActiveTab('mapping');
      
      toast({
        title: "Fichier CSV chargé avec succès",
        description: `${transformedData.length} produits trouvés dans le fichier.`,
      });
    } catch (error) {
      console.error("Erreur lors du traitement du CSV:", error);
      toast({
        title: "Erreur",
        description: "Impossible de traiter le fichier CSV. Vérifiez le format.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };
  
  // Fonction pour mettre à jour les mappings
  const handleMappingChange = (header: string, value: string) => {
    setMappings(prev => ({
      ...prev,
      [header]: value
    }));
  };
  
  // Fonction pour générer les descriptions en lot
  const handleBatchGeneration = async () => {
    if (csvData.length === 0) return;
    
    setIsProcessing(true);
    setProgress(0);
    setResults(csvData.map(row => ({
      productName: row.name,
      status: 'pending'
    })));
    
    setActiveTab('results');
    
    // Appel à l'API
    const response = await fetch("http://localhost:8000/batch-generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        products: csvData.map(product => ({
          name: product.name,
          description: product.description,
          category: product.category,
          keywords: product.keywords.split(',').map(k => k.trim()),
          technical_specs: product.technicalSpecs
        })),
        tone_style: {
          predefined_tone_id: selectedToneId,
          persona_target: personaTarget
        },
        seo_optimization: useSeoOptimization,
        use_auto_improvement: useAutoImprovement,
        competitor_analysis: useCompetitorAnalysis,
        use_seo_guide: useSeoGuide
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Traiter les résultats
    result.results.forEach((resultItem: BatchResult, idx: number) => {
      setResults(prev => {
        const updated = [...prev];
        
        if (resultItem.status === "success") {
          let formattedContent = '';
          
          if (useAutoImprovement) {
            formattedContent = `# ${csvData[idx].name}\n\n${resultItem.improved_description || ''}`;
            
            // Ajouter l'évaluation si disponible
            if (resultItem.evaluation) {
              formattedContent += "\n\n## Évaluation\n";
              Object.entries(resultItem.evaluation as Record<string, any>).forEach(([key, value]) => {
                formattedContent += `- **${key}**: ${value}\n`;
              });
            }
          } else {
            formattedContent = `# ${csvData[idx].name}\n\n${resultItem.product_description || ''}`;
            
            // Ajout des suggestions SEO si disponibles
            if (resultItem.seo_suggestions && resultItem.seo_suggestions.length > 0) {
              formattedContent += "\n\n## Suggestions SEO\n";
              resultItem.seo_suggestions.forEach((suggestion: string) => {
                formattedContent += `- ${suggestion}\n`;
              });
            }
            
            // Ajout des insights concurrentiels si disponibles
            if (resultItem.competitor_insights && resultItem.competitor_insights.length > 0) {
              formattedContent += "\n\n## Insights concurrentiels\n";
              resultItem.competitor_insights.forEach((insight: string) => {
                formattedContent += `- ${insight}\n`;
              });
            }
          }
          
          updated[idx] = {
            productName: csvData[idx].name,
            status: 'completed',
            content: formattedContent
          };
        } else {
          updated[idx] = {
            productName: csvData[idx].name,
            status: 'failed',
            error: resultItem.error || "Une erreur inconnue s'est produite"
          };
        }
        
        return updated;
      });
    });
    
    setIsProcessing(false);
    
    toast({
      title: "Génération terminée",
      description: `${csvData.length} descriptions de produits ont été générées.`,
    });
  };
  
  // Fonction pour exporter les résultats
  const handleExportResults = () => {
    const completedResults = results.filter(r => r.status === 'completed');
    if (completedResults.length === 0) return;
    
    const content = completedResults.map(result => {
      return `# ${result.productName}\n\n${result.content}\n\n---\n\n`;
    }).join('');
    
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'descriptions_produits.md');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center mb-6">
        <Link href="/" className="flex items-center text-blue-600 hover:text-blue-800 mr-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Retour
        </Link>
        <h1 className="text-3xl font-bold">Génération par lot</h1>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="upload">1. Upload CSV</TabsTrigger>
          <TabsTrigger value="mapping" disabled={csvData.length === 0}>2. Paramètres</TabsTrigger>
          <TabsTrigger value="results" disabled={results.length === 0}>3. Résultats</TabsTrigger>
        </TabsList>
        
        <TabsContent value="upload">
          <Card>
            <CardHeader>
              <CardTitle>Importer un fichier CSV</CardTitle>
              <CardDescription>
                Importez un fichier CSV contenant les informations de vos produits. 
                Chaque ligne représente un produit à traiter.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  ref={fileInputRef}
                  className="hidden"
                />
                
                <div className="flex flex-col items-center justify-center space-y-4">
                  <Upload className="h-12 w-12 text-gray-400" />
                  <div>
                    <p className="text-lg font-medium">
                      {file ? file.name : "Glissez-déposez votre fichier CSV ou cliquez pour parcourir"}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Format accepté: CSV (valeurs séparées par des virgules)
                    </p>
                  </div>
                  <Button 
                    onClick={() => fileInputRef.current?.click()}
                    variant="outline"
                    className="mt-2"
                  >
                    Parcourir
                  </Button>
                </div>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  <h3 className="text-md font-medium">Besoin d'un modèle ?</h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Téléchargez notre modèle CSV pour vous assurer que votre fichier est correctement formaté.
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleDownloadTemplate}
                  className="flex items-center"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Télécharger le modèle
                </Button>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button 
                onClick={handleProcessCSV} 
                disabled={!file || isUploading}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Traitement...
                  </>
                ) : (
                  "Continuer"
                )}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="mapping">
          <Card>
            <CardHeader>
              <CardTitle>Paramètres de génération</CardTitle>
              <CardDescription>
                Configurez les paramètres pour la génération des descriptions de produits.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Style et ton</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Ton
                    </label>
                    <select
                      value={selectedToneId}
                      onChange={(e) => setSelectedToneId(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                    >
                      <option value="professional">Professionnel</option>
                      <option value="casual">Décontracté</option>
                      <option value="luxury">Luxe</option>
                      <option value="technical">Technique</option>
                      <option value="educational">Éducatif</option>
                      <option value="enthusiastic">Enthousiaste</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Persona cible (optionnel)
                    </label>
                    <input
                      type="text"
                      value={personaTarget}
                      onChange={(e) => setPersonaTarget(e.target.value)}
                      placeholder="ex: Professionnels du secteur, débutants..."
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                    />
                  </div>
                </div>
                
                <Separator />
                
                <h3 className="text-lg font-medium">Options</h3>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="seoOptimization"
                      checked={useSeoOptimization}
                      onChange={(e) => setUseSeoOptimization(e.target.checked)}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="seoOptimization" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                      Optimisation SEO
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="autoImprovement"
                      checked={useAutoImprovement}
                      onChange={(e) => setUseAutoImprovement(e.target.checked)}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="autoImprovement" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                      Auto-amélioration (génération plus lente mais de meilleure qualité)
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="competitorAnalysis"
                      checked={useCompetitorAnalysis}
                      onChange={(e) => setUseCompetitorAnalysis(e.target.checked)}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="competitorAnalysis" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                      Analyse concurrentielle
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="useSeoGuide"
                      checked={useSeoGuide}
                      onChange={(e) => setUseSeoGuide(e.target.checked)}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="useSeoGuide" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                      Utiliser le guide SEO
                    </label>
                  </div>
                </div>
                
                <Separator />
                
                <h3 className="text-lg font-medium">Aperçu des données ({csvData.length} produits)</h3>
                {csvData.length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead className="bg-gray-50 dark:bg-gray-800">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Nom
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Description
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Catégorie
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Spécifications
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                        {csvData.slice(0, 3).map((product, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                              {product.name}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">
                              {product.description}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                              {product.category}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                              {Object.entries(product.technicalSpecs).slice(0, 2).map(([key, value], i) => (
                                <div key={i}>{key}: {value}</div>
                              ))}
                              {Object.keys(product.technicalSpecs).length > 2 && "..."}
                            </td>
                          </tr>
                        ))}
                        {csvData.length > 3 && (
                          <tr>
                            <td colSpan={4} className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 text-center">
                              ... et {csvData.length - 3} autres produits
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button 
                variant="outline" 
                onClick={() => setActiveTab('upload')}
              >
                Retour
              </Button>
              <Button 
                onClick={handleBatchGeneration}
                disabled={csvData.length === 0 || isProcessing}
              >
                Générer {csvData.length} descriptions
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="results">
          <Card>
            <CardHeader>
              <CardTitle>Résultats de la génération</CardTitle>
              <CardDescription>
                Suivi de la génération des descriptions de produits.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {isProcessing && (
                <div className="space-y-2 mb-6">
                  <div className="flex justify-between text-sm">
                    <span>Progression: {progress}%</span>
                    <span>{results.filter(r => r.status === 'completed').length} sur {results.length}</span>
                  </div>
                  <Progress value={progress} />
                </div>
              )}
              
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{result.productName}</h3>
                      <div>
                        {result.status === 'pending' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200">
                            En attente
                          </span>
                        )}
                        {result.status === 'processing' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200">
                            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                            En cours
                          </span>
                        )}
                        {result.status === 'completed' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200">
                            <Check className="h-3 w-3 mr-1" />
                            Terminé
                          </span>
                        )}
                        {result.status === 'failed' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            Échec
                          </span>
                        )}
                      </div>
                    </div>
                    
                    {result.status === 'completed' && result.content && (
                      <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-md text-sm max-h-60 overflow-y-auto">
                        <pre className="whitespace-pre-wrap font-mono text-xs">{result.content}</pre>
                      </div>
                    )}
                    
                    {result.status === 'failed' && result.error && (
                      <Alert variant="destructive" className="mt-2">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Erreur</AlertTitle>
                        <AlertDescription>
                          {result.error}
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button 
                variant="outline" 
                onClick={() => setActiveTab('mapping')}
                disabled={isProcessing}
              >
                Retour aux paramètres
              </Button>
              <Button 
                onClick={handleExportResults}
                disabled={results.filter(r => r.status === 'completed').length === 0}
              >
                <Download className="h-4 w-4 mr-2" />
                Exporter les résultats
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
