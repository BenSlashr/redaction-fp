'use client';

import { useState } from 'react';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Button } from './ui/button';
import { InfoIcon } from 'lucide-react';
import ClientDocumentManager from './ClientDocumentManager';

interface RAGToggleProps {
  onToggleRAG: (useRag: boolean, clientId: string, selectedDocuments?: string[]) => void;
  defaultClientId?: string;
}

const RAGToggle = ({ onToggleRAG, defaultClientId = 'default' }: RAGToggleProps) => {
  const [useRAG, setUseRAG] = useState(false);
  const [clientId, setClientId] = useState(defaultClientId);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);

  const handleToggleRAG = (checked: boolean) => {
    setUseRAG(checked);
    onToggleRAG(checked, clientId, selectedDocuments);
  };

  const handleSelectDocuments = (documentIds: string[]) => {
    setSelectedDocuments(documentIds);
    if (useRAG) {
      onToggleRAG(useRAG, clientId, documentIds);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Switch
            id="rag-toggle"
            checked={useRAG}
            onCheckedChange={handleToggleRAG}
          />
          <Label htmlFor="rag-toggle" className="font-medium">
            Enrichir avec les données client
          </Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <InfoIcon className="h-4 w-4" />
                <span className="sr-only">Plus d'informations</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="space-y-2">
                <h4 className="font-medium">Enrichissement par RAG</h4>
                <p className="text-sm text-muted-foreground">
                  Cette fonctionnalité utilise vos documents client pour enrichir les descriptions générées.
                  L'IA analysera automatiquement les documents pertinents pour créer un contenu plus précis et personnalisé.
                </p>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {useRAG && (
        <div className="border rounded-lg p-4">
          <ClientDocumentManager
            clientId={clientId}
            onSelectDocuments={handleSelectDocuments}
          />
        </div>
      )}
    </div>
  );
};

export default RAGToggle;
