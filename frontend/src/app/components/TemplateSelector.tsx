'use client';

import { useState, useEffect } from 'react';
import { api } from '../../lib/api';

interface ProductSectionTemplate {
  id: string;
  name: string;
  description: string;
}

interface ProductTemplate {
  id: string;
  name: string;
  description: string;
  sections: ProductSectionTemplate[];
}

interface TemplateSelectorProps {
  onTemplateChange: (templateId: string, selectedSections: string[]) => void;
}

export default function TemplateSelector({ onTemplateChange }: TemplateSelectorProps) {
  const [templates, setTemplates] = useState<ProductTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [selectedSections, setSelectedSections] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Récupérer les templates disponibles
  // Utiliser useEffect avec un tableau de dépendances vide pour éviter les boucles infinies
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true);
        const response = await api.getTemplates();
        console.log('Réponse de l\'API templates:', response);
        
        // Vérifier que la réponse contient bien les templates
        if (!response || !response.templates) {
          console.error('Réponse de l\'API invalide:', response);
          throw new Error('Format de réponse invalide');
        }
        
        setTemplates(response.templates);
        
        // Sélectionner le premier template par défaut
        if (response.templates.length > 0) {
          const defaultTemplate = response.templates[0];
          setSelectedTemplate(defaultTemplate.id);
          
          // Sélectionner toutes les sections par défaut
          const allSections = defaultTemplate.sections.map(section => section.id);
          setSelectedSections(allSections);
          
          // Notifier le parent du changement - mais seulement lors de l'initialisation
          onTemplateChange(defaultTemplate.id, allSections);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Erreur lors de la récupération des templates:', error);
        setError('Impossible de récupérer les templates. Veuillez réessayer plus tard.');
        setLoading(false);
      }
    };

    fetchTemplates();
    // Tableau de dépendances vide pour n'exécuter cet effet qu'une seule fois au montage du composant
  }, []);

  // Gérer le changement de template
  const handleTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const templateId = e.target.value;
    setSelectedTemplate(templateId);
    
    // Trouver le template sélectionné
    const template = templates.find(t => t.id === templateId);
    
    if (template) {
      // Sélectionner toutes les sections par défaut
      const allSections = template.sections.map(section => section.id);
      setSelectedSections(allSections);
      
      // Notifier le parent du changement
      onTemplateChange(templateId, allSections);
    }
  };

  // Gérer le changement de sélection des sections
  const handleSectionChange = (sectionId: string) => {
    setSelectedSections(prev => {
      // Si la section est déjà sélectionnée, la retirer
      // Sinon, l'ajouter
      const newSections = prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId];
      
      // Notifier le parent du changement
      onTemplateChange(selectedTemplate, newSections);
      
      return newSections;
    });
  };

  // Afficher un message de chargement
  if (loading) {
    return <div className="text-center py-4">Chargement des templates...</div>;
  }

  // Afficher un message d'erreur
  if (error) {
    return <div className="text-center py-4 text-red-500">{error}</div>;
  }

  // Trouver le template sélectionné
  const currentTemplate = templates.find(t => t.id === selectedTemplate);

  return (
    <div className="space-y-6">
      <div>
        <label htmlFor="template" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Template de fiche produit
        </label>
        <select
          id="template"
          name="template"
          value={selectedTemplate}
          onChange={handleTemplateChange}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
        >
          {templates.map(template => (
            <option key={template.id} value={template.id}>
              {template.name}
            </option>
          ))}
        </select>
        {currentTemplate && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {currentTemplate.description}
          </p>
        )}
      </div>

      {currentTemplate && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Sections à inclure
          </label>
          <div className="space-y-2">
            {currentTemplate.sections.map(section => (
              <div key={section.id} className="flex items-center">
                <input
                  type="checkbox"
                  id={`section-${section.id}`}
                  checked={selectedSections.includes(section.id)}
                  onChange={() => handleSectionChange(section.id)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor={`section-${section.id}`} className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                  {section.name}
                  <span className="ml-1 text-xs text-gray-500 dark:text-gray-400">
                    {section.description}
                  </span>
                </label>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
