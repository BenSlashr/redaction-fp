'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useToast } from './ui/use-toast';
import { Loader2, Upload, FileText, X } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

interface ClientDocumentUploaderProps {
  clientId: string;
  onDocumentUploaded?: () => void;
}

const ClientDocumentUploader = ({ clientId, onDocumentUploaded }: ClientDocumentUploaderProps) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [sourceType, setSourceType] = useState('catalogue');
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { toast } = useToast();

  const handleSubmitText = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim() || !content.trim()) {
      toast({
        title: 'Erreur',
        description: 'Veuillez remplir tous les champs obligatoires.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsUploading(true);
    
    try {
      const response = await fetch('/api/client-document', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_id: clientId,
          title,
          content,
          source_type: sourceType,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }
      
      const data = await response.json();
      
      toast({
        title: 'Document téléchargé',
        description: `Le document "${title}" a été indexé avec succès (${data.chunk_count} chunks créés).`,
      });
      
      // Réinitialiser le formulaire
      setTitle('');
      setContent('');
      
      // Notifier le parent
      if (onDocumentUploaded) {
        onDocumentUploaded();
      }
    } catch (error) {
      console.error('Erreur lors du téléchargement du document:', error);
      toast({
        title: 'Erreur',
        description: 'Une erreur est survenue lors du téléchargement du document.',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmitFile = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      toast({
        title: 'Erreur',
        description: 'Veuillez sélectionner un fichier à télécharger.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('client_id', clientId);
      
      if (title.trim()) {
        formData.append('title', title);
      }
      
      formData.append('source_type', sourceType);
      
      const response = await fetch('/api/client-file', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }
      
      const data = await response.json();
      
      toast({
        title: 'Fichier téléchargé',
        description: `Le fichier "${data.title}" a été indexé avec succès (${data.chunk_count} chunks créés).`,
      });
      
      // Réinitialiser le formulaire
      setTitle('');
      setSelectedFile(null);
      
      // Notifier le parent
      if (onDocumentUploaded) {
        onDocumentUploaded();
      }
    } catch (error) {
      console.error('Erreur lors du téléchargement du fichier:', error);
      toast({
        title: 'Erreur',
        description: 'Une erreur est survenue lors du téléchargement du fichier.',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      
      // Utiliser le nom du fichier comme titre s'il n'y en a pas déjà un
      if (!title.trim()) {
        // Enlever l'extension du fichier pour le titre
        const fileName = file.name.split('.').slice(0, -1).join('.');
        setTitle(fileName);
      }
    }
  };

  const clearSelectedFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className="space-y-4">
      <Tabs value={activeTab} onValueChange={(value) => {
        if (value === 'text' || value === 'file') {
          setActiveTab(value);
        }
      }}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="file">Télécharger un fichier</TabsTrigger>
          <TabsTrigger value="text">Saisir du texte</TabsTrigger>
        </TabsList>
        
        <TabsContent value="file" className="space-y-4 pt-4">
          <form onSubmit={handleSubmitFile} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="file-title">Titre du document (optionnel)</Label>
              <Input
                id="file-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Sera extrait du nom du fichier si non renseigné"
                disabled={isUploading}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="file-sourceType">Type de document</Label>
              <Select
                value={sourceType}
                onValueChange={setSourceType}
                disabled={isUploading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="catalogue">Catalogue</SelectItem>
                  <SelectItem value="fiche_technique">Fiche technique</SelectItem>
                  <SelectItem value="guide_utilisateur">Guide utilisateur</SelectItem>
                  <SelectItem value="brochure">Brochure</SelectItem>
                  <SelectItem value="autre">Autre</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="file-upload">Fichier</Label>
              {selectedFile ? (
                <div className="flex items-center justify-between p-2 border rounded-md">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-blue-500" />
                    <span className="text-sm truncate max-w-[200px]">{selectedFile.name}</span>
                    <span className="text-xs text-gray-500">
                      ({(selectedFile.size / 1024).toFixed(1)} Ko)
                    </span>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={clearSelectedFile}
                    disabled={isUploading}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="flex items-center justify-center w-full">
                  <label
                    htmlFor="file-upload"
                    className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 border-gray-300 dark:border-gray-600"
                  >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-8 h-8 mb-3 text-gray-500 dark:text-gray-400" />
                      <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                        <span className="font-semibold">Cliquez pour télécharger</span> ou glissez-déposez
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        PDF, DOCX, TXT, HTML (max. 10 Mo)
                      </p>
                    </div>
                    <input
                      id="file-upload"
                      type="file"
                      className="hidden"
                      onChange={handleFileChange}
                      accept=".pdf,.docx,.doc,.txt,.html,.htm"
                      disabled={isUploading}
                    />
                  </label>
                </div>
              )}
            </div>
            
            <Button type="submit" disabled={isUploading || !selectedFile} className="w-full">
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Téléchargement...
                </>
              ) : (
                'Télécharger et indexer'
              )}
            </Button>
          </form>
        </TabsContent>
        
        <TabsContent value="text" className="space-y-4 pt-4">
          <form onSubmit={handleSubmitText} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Titre du document</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Catalogue produits 2023"
                disabled={isUploading}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="sourceType">Type de document</Label>
              <Select
                value={sourceType}
                onValueChange={setSourceType}
                disabled={isUploading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="catalogue">Catalogue</SelectItem>
                  <SelectItem value="fiche_technique">Fiche technique</SelectItem>
                  <SelectItem value="guide_utilisateur">Guide utilisateur</SelectItem>
                  <SelectItem value="brochure">Brochure</SelectItem>
                  <SelectItem value="autre">Autre</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="content">Contenu du document</Label>
              <Textarea
                id="content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Copiez-collez le contenu du document ici..."
                rows={10}
                disabled={isUploading}
                required
              />
            </div>
            
            <Button type="submit" disabled={isUploading} className="w-full">
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Téléchargement...
                </>
              ) : (
                'Télécharger et indexer'
              )}
            </Button>
          </form>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ClientDocumentUploader;
