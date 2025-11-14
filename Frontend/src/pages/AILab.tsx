import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, Loader2, Leaf, Bug, Mic, Volume2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function AILab() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [leafResult, setLeafResult] = useState<any>(null);
  const [insectResult, setInsectResult] = useState<any>(null);
  const { toast } = useToast();

  const handleFileUpload = async (type: "leaf" | "insect", file: File) => {
    setIsProcessing(true);
    
    // Simulate API call
    setTimeout(() => {
      if (type === "leaf") {
        setLeafResult({
          crop: "Roșii",
          health: "Sănătoase",
          confidence: 0.94,
          details: "Frunzele prezintă o culoare verde vibrantă, fără pete sau decolorări. Nu au fost detectate semne de boli sau dăunători.",
        });
      } else {
        setInsectResult({
          species: "Afide verzi (Myzus persicae)",
          risk: "Scăzut",
          actions: [
            "Monitorizare zilnică pentru creșterea populației",
            "Introducerea insectelor benefice (buburuze)",
            "Dacă nivelul crește, aplică sapun insecticid organic",
          ],
        });
      }
      setIsProcessing(false);
      toast({
        title: "Analiză completă",
        description: "Rezultatele sunt afișate mai jos.",
      });
    }, 2000);
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">AI Lab</h1>
        <p className="text-muted-foreground">
          Instrumente AI pentru analiza culturilor și identificare probleme
        </p>
      </div>

      <Tabs defaultValue="leaves" className="space-y-4 md:space-y-6">
        <TabsList className="grid w-full grid-cols-3 h-auto">
          <TabsTrigger value="leaves" className="flex-col sm:flex-row gap-1 sm:gap-2 py-2 text-xs sm:text-sm">
            <Leaf className="h-3 w-3 sm:h-4 sm:w-4" />
            <span>Frunze</span>
          </TabsTrigger>
          <TabsTrigger value="insects" className="flex-col sm:flex-row gap-1 sm:gap-2 py-2 text-xs sm:text-sm">
            <Bug className="h-3 w-3 sm:h-4 sm:w-4" />
            <span>Insecte</span>
          </TabsTrigger>
          <TabsTrigger value="voice" className="flex-col sm:flex-row gap-1 sm:gap-2 py-2 text-xs sm:text-sm">
            <Mic className="h-3 w-3 sm:h-4 sm:w-4" />
            <span>Voice</span>
          </TabsTrigger>
        </TabsList>

        {/* Leaf Classification */}
        <TabsContent value="leaves" className="space-y-4 md:space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Clasificare frunze (sănătoase / nesănătoase)</CardTitle>
              <CardDescription>
                Culturile: fasole, roșii, cartofi, ardei, porumb
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-muted rounded-lg p-4 sm:p-8 text-center hover:border-primary transition-colors cursor-pointer">
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  id="leaf-upload"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload("leaf", file);
                  }}
                  disabled={isProcessing}
                />
                <label htmlFor="leaf-upload" className="cursor-pointer">
                  <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-sm font-medium mb-1">
                    Click pentru a încărca imagine
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Formatele acceptate: JPG, PNG, WEBP
                  </p>
                </label>
              </div>

              {isProcessing && (
                <div className="flex items-center justify-center gap-2 py-4">
                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  <span className="text-sm">Se analizează imaginea...</span>
                </div>
              )}

              {leafResult && !isProcessing && (
                <div className="space-y-4 p-6 bg-muted/50 rounded-lg">
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Cultură</p>
                      <p className="text-lg font-semibold">{leafResult.crop}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Stare</p>
                      <p className="text-lg font-semibold text-success">{leafResult.health}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Încredere</p>
                      <p className="text-lg font-semibold">{(leafResult.confidence * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Detalii analiză</p>
                    <p className="text-sm">{leafResult.details}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Insect Classification */}
        <TabsContent value="insects" className="space-y-4 md:space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Clasificare insecte pe cultură</CardTitle>
              <CardDescription>
                Încarcă imagini sau video cu insecte pentru identificare
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-muted rounded-lg p-4 sm:p-8 text-center hover:border-primary transition-colors cursor-pointer">
                <input
                  type="file"
                  accept="image/*,video/*"
                  className="hidden"
                  id="insect-upload"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload("insect", file);
                  }}
                  disabled={isProcessing}
                />
                <label htmlFor="insect-upload" className="cursor-pointer">
                  <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-sm font-medium mb-1">
                    Click pentru a încărca fișier
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Formatele acceptate: JPG, PNG, MP4, MOV
                  </p>
                </label>
              </div>

              {isProcessing && (
                <div className="flex items-center justify-center gap-2 py-4">
                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  <span className="text-sm">Se analizează conținutul...</span>
                </div>
              )}

              {insectResult && !isProcessing && (
                <div className="space-y-4 p-6 bg-muted/50 rounded-lg">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Specie</p>
                      <p className="text-lg font-semibold">{insectResult.species}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Risc</p>
                      <p className="text-lg font-semibold text-warning">{insectResult.risk}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Acțiuni recomandate</p>
                    <ul className="space-y-2">
                      {insectResult.actions.map((action: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5" />
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Voice Interface */}
        <TabsContent value="voice" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Voice ↔ Text</CardTitle>
              <CardDescription>
                Interacționează cu sistemul folosind vocea
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Button className="flex-1" size="lg">
                    <Mic className="h-5 w-5 mr-2" />
                    Ține apăsat pentru a vorbi
                  </Button>
                  <Button variant="outline" size="lg">
                    <Volume2 className="h-5 w-5" />
                  </Button>
                </div>

                <div className="p-4 bg-muted/50 rounded-lg min-h-[100px]">
                  <p className="text-sm text-muted-foreground italic">
                    Răspunsul va apărea aici...
                  </p>
                </div>

                <div>
                  <p className="text-sm font-medium mb-2">Întrebări exemple:</p>
                  <div className="space-y-2">
                    {[
                      "Ce vreme avem săptămâna viitoare?",
                      "Când pot recolta roșiile?",
                      "Rezumat starea culturilor",
                    ].map((example, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        size="sm"
                        className="w-full justify-start"
                        onClick={() => {
                          toast({
                            title: "Procesare comandă vocală...",
                            description: `"${example}"`,
                          });
                        }}
                      >
                        {example}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
