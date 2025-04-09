'use client';

import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useToast } from './ui/use-toast';
import { Loader2, Trash2, RefreshCw, FileText } from 'lucide-react';
import ClientDocumentUploader from './ClientDocumentUploader';

interface Document {
  document_id: string;
  title: string;
  source_type: string;
}

interface ClientDataSummary {
  client_id: string;
  document_count: number;
  document_types: Record<string, number>;
  documents: Document[];
}

interface ClientDocumentManagerProps {
  clientId: string;
  onSelectDocuments?: (documentIds: string[]) => void;
}

const ClientDocumentManager = ({ clientId, onSelectDocuments }: ClientDocumentManagerProps) => {
  const [clientData, setClientData] = useState<ClientDataSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('documents');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const { toast } = useToast();

  const fetchClientData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/client-data/${clientId}`);
      
      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }
      
      const data = await response.json();
      setClientData(data);
    } catch (error) {
      console.error('Erreur lors de la récupération des données client:', error);
      toast({
        title: 'Erreur',
        description: 'Impossible de récupérer les données client.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (clientId) {
      fetchClientData();
    }
  }, [clientId]);

  const handleDeleteDocument = async (documentId: string) => {
    try {
      const response = await fetch(`/api/client-document/${documentId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }
      
      // Mettre à jour la liste des documents
      fetchClientData();
      
      // Supprimer de la sélection si nécessaire
      if (selectedDocuments.includes(documentId)) {
        const newSelection = selectedDocuments.filter(id => id !== documentId);
        setSelectedDocuments(newSelection);
        if (onSelectDocuments) {
          onSelectDocuments(newSelection);
        }
      }
      
      toast({
        title: 'Document supprimé',
        description: 'Le document a été supprimé avec succès.',
      });
    } catch (error) {
      console.error('Erreur lors de la suppression du document:', error);
      toast({
        title: 'Erreur',
        description: 'Impossible de supprimer le document.',
        variant: 'destructive',
      });
    }
  };

  const handleToggleDocument = (documentId: string) => {
    let newSelection: string[];
    
    if (selectedDocuments.includes(documentId)) {
      newSelection = selectedDocuments.filter(id => id !== documentId);
    } else {
      newSelection = [...selectedDocuments, documentId];
    }
    
    setSelectedDocuments(newSelection);
    
    if (onSelectDocuments) {
      onSelectDocuments(newSelection);
    }
  };

  const getSourceTypeBadge = (sourceType: string) => {
    const types: Record<string, { label: string, variant: "default" | "secondary" | "outline" }> = {
      catalogue: { label: 'Catalogue', variant: 'default' },
      fiche_technique: { label: 'Fiche technique', variant: 'secondary' },
      guide_utilisateur: { label: 'Guide utilisateur', variant: 'outline' },
      brochure: { label: 'Brochure', variant: 'default' },
      autre: { label: 'Autre', variant: 'outline' },
    };
    
    const type = types[sourceType] || { label: sourceType, variant: 'outline' };
    
    return (
      <Badge variant={type.variant}>
        {type.label}
      </Badge>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Données client</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchClientData}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          <span className="ml-2">Actualiser</span>
        </Button>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="documents">Documents ({clientData?.document_count || 0})</TabsTrigger>
          <TabsTrigger value="upload">Ajouter un document</TabsTrigger>
        </TabsList>
        
        <TabsContent value="documents" className="space-y-4">
          {isLoading ? (
            <div className="flex justify-center items-center h-40">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : clientData && clientData.documents.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {clientData.documents.map((doc) => (
                <Card key={doc.document_id} className={`cursor-pointer ${selectedDocuments.includes(doc.document_id) ? 'border-primary' : ''}`}>
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-base">{doc.title}</CardTitle>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteDocument(doc.document_id);
                        }}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                    <CardDescription>
                      {getSourceTypeBadge(doc.source_type)}
                    </CardDescription>
                  </CardHeader>
                  <CardFooter className="pt-2">
                    <Button
                      variant={selectedDocuments.includes(doc.document_id) ? "default" : "outline"}
                      size="sm"
                      className="w-full"
                      onClick={() => handleToggleDocument(doc.document_id)}
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      {selectedDocuments.includes(doc.document_id) ? 'Sélectionné' : 'Sélectionner'}
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-muted-foreground">Aucun document disponible pour ce client.</p>
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={() => setActiveTab('upload')}
                >
                  Ajouter un document
                </Button>
              </CardContent>
            </Card>
          )}
          
          {clientData && clientData.document_count > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
              <p className="text-sm font-medium w-full">Types de documents:</p>
              {Object.entries(clientData.document_types).map(([type, count]) => (
                <Badge key={type} variant="outline">
                  {type}: {count}
                </Badge>
              ))}
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="upload">
          <Card>
            <CardHeader>
              <CardTitle>Ajouter un document</CardTitle>
              <CardDescription>
                Téléchargez un document pour enrichir les générations de fiches produit.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ClientDocumentUploader
                clientId={clientId}
                onDocumentUploaded={() => {
                  fetchClientData();
                  setActiveTab('documents');
                }}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ClientDocumentManager;
