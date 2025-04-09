import React, { useState, useEffect } from 'react';
import { Check, ChevronsUpDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Separator } from '@/components/ui/separator';

interface AIModel {
  id: string;
  name: string;
  description: string;
}

interface AIProvider {
  name: string;
  models: AIModel[];
}

interface AIModelSelectorProps {
  onSelect: (provider: string, model: string) => void;
  defaultProvider?: string;
  defaultModel?: string;
}

export function AIModelSelector({ onSelect, defaultProvider = 'OpenAI', defaultModel = 'gpt-4o' }: AIModelSelectorProps) {
  const [open, setOpen] = useState(false);
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [selectedProvider, setSelectedProvider] = useState<string>(defaultProvider);
  const [selectedModel, setSelectedModel] = useState<string>(defaultModel);
  
  // Récupérer les fournisseurs d'IA disponibles
  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setLoading(true);
        // Simulation de données pour le moment
        // Dans une implémentation réelle, vous utiliseriez api.getAIProviders()
        const mockProviders = [
          {
            name: "OpenAI",
            models: [
              { id: "gpt-4o", name: "GPT-4o", description: "Le modèle le plus avancé d'OpenAI" },
              { id: "gpt-4", name: "GPT-4", description: "Modèle puissant avec un bon rapport qualité/prix" },
              { id: "gpt-3.5-turbo", name: "GPT-3.5 Turbo", description: "Modèle économique et rapide" }
            ]
          },
          {
            name: "Google",
            models: [
              { id: "gemini-2.5-pro", name: "Gemini 2.5 Pro", description: "Le modèle le plus avancé de Google" },
              { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro", description: "Modèle multimodal avec un contexte étendu" }
            ]
          }
        ];
        
        setProviders(mockProviders);
        
        // Vérifier si le fournisseur et le modèle par défaut sont disponibles
        let providerExists = false;
        let modelExists = false;
        
        for (const provider of mockProviders) {
          if (provider.name === defaultProvider) {
            providerExists = true;
            for (const model of provider.models) {
              if (model.id === defaultModel) {
                modelExists = true;
                break;
              }
            }
            break;
          }
        }
        
        // Si le fournisseur par défaut n'existe pas, prendre le premier disponible
        if (!providerExists && mockProviders.length > 0) {
          setSelectedProvider(mockProviders[0].name);
          if (mockProviders[0].models.length > 0) {
            setSelectedModel(mockProviders[0].models[0].id);
            onSelect(mockProviders[0].name, mockProviders[0].models[0].id);
          }
        }
        // Si le modèle par défaut n'existe pas, prendre le premier du fournisseur
        else if (!modelExists && providerExists) {
          const provider = mockProviders.find(p => p.name === defaultProvider);
          if (provider && provider.models.length > 0) {
            setSelectedModel(provider.models[0].id);
            onSelect(defaultProvider, provider.models[0].id);
          }
        }
      } catch (err) {
        console.error('Erreur lors de la récupération des fournisseurs d\'IA:', err);
        setError('Erreur lors de la récupération des fournisseurs d\'IA');
      } finally {
        setLoading(false);
      }
    };
    
    fetchProviders();
  }, [defaultProvider, defaultModel, onSelect]);
  
  // Trouver le modèle sélectionné
  const selectedProviderData = providers.find(p => p.name === selectedProvider);
  const selectedModelData = selectedProviderData?.models.find(m => m.id === selectedModel);
  
  // Gérer la sélection d'un modèle
  const handleSelect = (providerId: string, modelId: string) => {
    setSelectedProvider(providerId);
    setSelectedModel(modelId);
    onSelect(providerId, modelId);
    setOpen(false);
  };

  // Filtrer les modèles en fonction de la recherche
  const filteredProviders = providers.map(provider => ({
    ...provider,
    models: provider.models.filter(model => 
      model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      model.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      provider.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(provider => provider.models.length > 0);
  
  if (loading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600"></div>
        <span className="text-sm text-gray-500">Chargement des modèles...</span>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="text-sm text-red-500">
        {error}
      </div>
    );
  }
  
  return (
    <div className="flex flex-col space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">Modèle d'IA</label>
        {selectedModelData && (
          <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold">
            {selectedProviderData?.name}
          </span>
        )}
      </div>
      
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between"
          >
            {selectedModelData ? selectedModelData.name : "Sélectionner un modèle..."}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[300px] p-0">
          <div className="p-2">
            <div className="flex items-center border rounded-md px-3 py-2 mb-2">
              <input
                placeholder="Rechercher un modèle..."
                className="flex-1 bg-transparent outline-none text-sm"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <div className="max-h-[300px] overflow-auto">
              {filteredProviders.length === 0 ? (
                <div className="py-6 text-center text-sm text-gray-500">
                  Aucun modèle trouvé.
                </div>
              ) : (
                filteredProviders.map((provider) => (
                  <div key={provider.name}>
                    <div className="px-2 py-1.5 text-xs font-semibold text-gray-500">
                      {provider.name}
                    </div>
                    {provider.models.map((model) => (
                      <div
                        key={`${provider.name}-${model.id}`}
                        className={cn(
                          "flex items-center justify-between px-2 py-1.5 text-sm cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md",
                          selectedProvider === provider.name && selectedModel === model.id
                            ? "bg-gray-100 dark:bg-gray-800"
                            : ""
                        )}
                        onClick={() => handleSelect(provider.name, model.id)}
                      >
                        <div className="flex flex-col">
                          <span>{model.name}</span>
                          <span className="text-xs text-gray-500 truncate max-w-[200px]">
                            {model.description}
                          </span>
                        </div>
                        <Check
                          className={cn(
                            "h-4 w-4",
                            selectedProvider === provider.name && selectedModel === model.id
                              ? "opacity-100"
                              : "opacity-0"
                          )}
                        />
                      </div>
                    ))}
                    <Separator className="my-1" />
                  </div>
                ))
              )}
            </div>
          </div>
        </PopoverContent>
      </Popover>
      
      {selectedModelData && (
        <div className="text-xs text-gray-500 mt-1">
          {selectedModelData.description}
        </div>
      )}
    </div>
  );
}
