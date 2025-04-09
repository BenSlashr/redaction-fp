'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Separator } from './ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import RAGToggle from './RAGToggle';

interface RAGFeatureProps {
  onRAGSettingsChange?: (settings: {
    useRAG: boolean;
    clientId: string;
    selectedDocuments?: string[];
  }) => void;
  defaultClientId?: string;
}

const RAGFeature = ({ 
  onRAGSettingsChange,
  defaultClientId = 'default'
}: RAGFeatureProps) => {
  const [activeTab, setActiveTab] = useState('settings');
  const [ragSettings, setRagSettings] = useState({
    useRAG: false,
    clientId: defaultClientId,
    selectedDocuments: [] as string[]
  });

  const handleToggleRAG = (useRag: boolean, clientId: string, selectedDocuments?: string[]) => {
    const newSettings = {
      useRAG: useRag,
      clientId,
      selectedDocuments: selectedDocuments || []
    };
    
    setRagSettings(newSettings);
    
    if (onRAGSettingsChange) {
      onRAGSettingsChange(newSettings);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Données client</CardTitle>
        <CardDescription>
          Enrichissez vos descriptions produit avec les données spécifiques de votre client
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="settings">Paramètres</TabsTrigger>
            <TabsTrigger value="info">Comment ça marche</TabsTrigger>
          </TabsList>
          
          <TabsContent value="settings" className="space-y-4 pt-4">
            <RAGToggle 
              onToggleRAG={handleToggleRAG}
              defaultClientId={defaultClientId}
            />
          </TabsContent>
          
          <TabsContent value="info" className="space-y-4 pt-4">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Enrichissement par RAG (Retrieval-Augmented Generation)</h3>
              
              <p className="text-sm text-muted-foreground">
                Cette fonctionnalité utilise la technologie RAG pour enrichir les descriptions de produits 
                avec des informations spécifiques à votre client, extraites de vos documents.
              </p>
              
              <Separator />
              
              <div className="space-y-2">
                <h4 className="font-medium">Comment ça fonctionne :</h4>
                <ol className="list-decimal list-inside space-y-2 text-sm">
                  <li>Téléchargez des documents contenant des informations sur votre client</li>
                  <li>Activez la fonctionnalité RAG lors de la génération</li>
                  <li>Sélectionnez les documents pertinents à utiliser</li>
                  <li>L'IA analysera automatiquement ces documents pour enrichir la description générée</li>
                </ol>
              </div>
              
              <Separator />
              
              <div className="space-y-2">
                <h4 className="font-medium">Types de documents recommandés :</h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Catalogues de produits</li>
                  <li>Fiches techniques</li>
                  <li>Brochures commerciales</li>
                  <li>Guides utilisateurs</li>
                  <li>Présentations d'entreprise</li>
                </ul>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default RAGFeature;
