"use client";

import { useState } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "./ui/card";
import { useToast } from "./ui/use-toast";
import { Loader2, ClipboardPaste, Trash } from "lucide-react";

interface Specification {
  name: string;
  value: string;
}

interface SpecsExtractorProps {
  onSpecsExtracted: (specs: Specification[]) => void;
  className?: string;
}

export function SpecsExtractor({ onSpecsExtracted, className = "" }: SpecsExtractorProps) {
  const [rawText, setRawText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [extractedSpecs, setExtractedSpecs] = useState<Specification[]>([]);
  const { toast } = useToast();

  const handleExtract = async () => {
    if (!rawText.trim()) {
      toast({
        title: "Texte vide",
        description: "Veuillez coller un texte contenant des spécifications techniques.",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsLoading(true);
      
      // Appel direct à l'API backend
      const response = await fetch("http://localhost:8000/extract-specs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: rawText }),
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }

      const data = await response.json();
      setExtractedSpecs(data.specs);
      onSpecsExtracted(data.specs);
      
      toast({
        title: "Spécifications extraites",
        description: `${data.specs.length} spécifications ont été extraites avec succès.`,
      });
    } catch (error) {
      console.error("Erreur lors de l'extraction:", error);
      toast({
        title: "Erreur",
        description: "Impossible d'extraire les spécifications. Veuillez réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setRawText(text);
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible d'accéder au presse-papiers. Veuillez coller manuellement.",
        variant: "destructive",
      });
    }
  };

  const handleClear = () => {
    setRawText("");
    setExtractedSpecs([]);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Extracteur de spécifications</CardTitle>
        <CardDescription>
          Collez le texte contenant vos spécifications techniques et cliquez sur "Extraire".
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="relative">
            <Textarea
              placeholder="Collez ici vos spécifications techniques (ex: Couleur: Rouge, Poids: 5kg...)"
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="min-h-[150px] font-mono text-sm"
            />
            <div className="absolute top-2 right-2 flex space-x-1">
              <Button
                variant="outline"
                size="icon"
                onClick={handlePaste}
                title="Coller depuis le presse-papiers"
              >
                <ClipboardPaste className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={handleClear}
                title="Effacer"
              >
                <Trash className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {extractedSpecs.length > 0 && (
            <div className="border rounded-md p-4">
              <h3 className="font-medium mb-2">Spécifications extraites:</h3>
              <div className="grid grid-cols-2 gap-2">
                {extractedSpecs.map((spec, index) => (
                  <div key={index} className="flex">
                    <span className="font-medium mr-2">{spec.name}:</span>
                    <span>{spec.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button
          onClick={handleExtract}
          disabled={isLoading || !rawText.trim()}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Extraction...
            </>
          ) : (
            "Extraire les spécifications"
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
