import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Save, Server, Bell } from "lucide-react";

export default function Setari() {
  const { toast } = useToast();
  const [apiBase, setApiBase] = useState("http://localhost:3000");
  const [realtimeMode, setRealtimeMode] = useState("SSE");
  const [soilMin, setSoilMin] = useState(35);
  const [tempMax, setTempMax] = useState(32);

  const handleSave = () => {
    toast({
      title: "Setări salvate",
      description: "Configurațiile au fost actualizate cu succes.",
    });
  };

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold mb-2">Setări</h1>
        <p className="text-muted-foreground">
          Configurează surse de date și praguri pentru alertele automate
        </p>
      </div>

      {/* Data Sources */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5 text-primary" />
            Surse date
          </CardTitle>
          <CardDescription>
            Configurează endpoint-urile API pentru conectarea la backend
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="api-base">API Base URL</Label>
            <Input
              id="api-base"
              placeholder="http://localhost:3000"
              value={apiBase}
              onChange={(e) => setApiBase(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              URL-ul de bază pentru toate cererile API către backend
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="realtime-mode">Mod realtime</Label>
            <Select value={realtimeMode} onValueChange={setRealtimeMode}>
              <SelectTrigger id="realtime-mode">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="SSE">SSE (Server-Sent Events)</SelectItem>
                <SelectItem value="WebSocket">WebSocket</SelectItem>
                <SelectItem value="Polling">Polling</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Metoda de obținere a datelor în timp real de la senzori
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Alert Thresholds */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-primary" />
            Praguri alerte
          </CardTitle>
          <CardDescription>
            Definește valorile critice pentru declanșarea alertelor automate
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="soil-min">Umiditate sol minimă (%)</Label>
            <Input
              id="soil-min"
              type="number"
              min="0"
              max="100"
              value={soilMin}
              onChange={(e) => setSoilMin(Number(e.target.value))}
            />
            <p className="text-xs text-muted-foreground">
              Alertă când umiditatea solului scade sub acest prag
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="temp-max">Temperatură maximă (°C)</Label>
            <Input
              id="temp-max"
              type="number"
              min="0"
              max="50"
              value={tempMax}
              onChange={(e) => setTempMax(Number(e.target.value))}
            />
            <p className="text-xs text-muted-foreground">
              Alertă când temperatura depășește acest prag
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave} size="lg">
          <Save className="h-4 w-4 mr-2" />
          Salvează setările
        </Button>
      </div>
    </div>
  );
}
