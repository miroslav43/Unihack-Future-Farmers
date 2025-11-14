import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, CheckCircle2, Droplets, Thermometer } from "lucide-react";

interface SensorReading {
  parameter: string;
  value: number;
  unit: string;
  sensor: string;
  reference: string;
  timestamp: string;
}

export default function Senzori() {
  const [readings, setReadings] = useState<SensorReading[]>([
    {
      parameter: "Temperatură aer",
      value: 24.7,
      unit: "°C",
      sensor: "DHT11",
      reference: "GJJFDR_DHT11-module",
      timestamp: new Date().toLocaleString("ro-RO"),
    },
    {
      parameter: "Umiditate aer",
      value: 58.2,
      unit: "%",
      sensor: "DHT11",
      reference: "GJJFDR_DHT11-module",
      timestamp: new Date().toLocaleString("ro-RO"),
    },
    {
      parameter: "Umiditate sol",
      value: 41.0,
      unit: "%",
      sensor: "Higrometru sol",
      reference: "NDGWBX_hygro",
      timestamp: new Date().toLocaleString("ro-RO"),
    },
    {
      parameter: "Nivel apă",
      value: 72.0,
      unit: "%",
      sensor: "Water level sensor",
      reference: "NGCKNA_waterlevel",
      timestamp: new Date().toLocaleString("ro-RO"),
    },
    {
      parameter: "Luminozitate",
      value: 13500,
      unit: "lx",
      sensor: "Senzor de lumină",
      reference: "YQZBML_Mod-light",
      timestamp: new Date().toLocaleString("ro-RO"),
    },
  ]);

  const [waterLevel, setWaterLevel] = useState(72);
  const [alerts, setAlerts] = useState<Array<{ type: "warning" | "danger" | "info"; message: string }>>([]);

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setReadings((prev) =>
        prev.map((reading) => ({
          ...reading,
          value:
            reading.parameter === "Luminozitate"
              ? 8000 + Math.random() * 10000
              : reading.unit === "%"
              ? Math.max(0, Math.min(100, reading.value + (Math.random() - 0.5) * 5))
              : reading.unit === "°C"
              ? 18 + Math.random() * 12
              : reading.value,
          timestamp: new Date().toLocaleString("ro-RO"),
        }))
      );

      setWaterLevel((prev) => Math.max(0, Math.min(100, prev + (Math.random() - 0.5) * 3)));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const newAlerts = [];
    const soilReading = readings.find((r) => r.parameter === "Umiditate sol");
    const tempReading = readings.find((r) => r.parameter === "Temperatură aer");

    if (soilReading && soilReading.value < 35) {
      newAlerts.push({ type: "danger" as const, message: "Sol uscat – pornește irigare" });
    }

    if (tempReading && tempReading.value > 32) {
      newAlerts.push({ type: "warning" as const, message: "Temperatură ridicată – ventilație" });
    }

    if (waterLevel < 30) {
      newAlerts.push({ type: "danger" as const, message: "Nivel apă critic – umple rezervorul" });
    } else if (waterLevel < 50) {
      newAlerts.push({ type: "warning" as const, message: "Nivel apă scăzut – planifică reumplere" });
    }

    setAlerts(newAlerts);
  }, [readings, waterLevel]);

  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">Senzori și status</h1>
        <p className="text-muted-foreground">
          Parametrii măsurați din teren. Update live din sistem.
        </p>
      </div>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="space-y-3">
          {alerts.map((alert, idx) => (
            <Alert
              key={idx}
              variant={alert.type === "danger" ? "destructive" : "default"}
              className={alert.type === "warning" ? "border-warning" : ""}
            >
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{alert.message}</AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Gauges Row */}
      <div className="grid gap-4 md:gap-6 md:grid-cols-2">
        {/* Water Tank Gauge */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Droplets className="h-5 w-5 text-primary" />
              Rezervor apă
            </CardTitle>
            <CardDescription>Nivel curent în rezervor</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className="text-4xl sm:text-5xl font-bold mb-2">{waterLevel.toFixed(0)}%</div>
              <Progress value={waterLevel} className="h-3" />
            </div>
            <div className="flex flex-col sm:flex-row justify-between gap-2 text-xs sm:text-sm text-muted-foreground">
              <span>Critic: &lt;15%</span>
              <span>Scăzut: &lt;30%</span>
              <span>Optim: &gt;50%</span>
            </div>
          </CardContent>
        </Card>

        {/* Temperature Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Thermometer className="h-5 w-5 text-primary" />
              Status climatic
            </CardTitle>
            <CardDescription>Condiții actuale mediu</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              {readings.slice(0, 2).map((reading, idx) => (
                <div key={idx} className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1 sm:gap-0">
                  <span className="text-sm font-medium">{reading.parameter}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xl sm:text-2xl font-bold">
                      {reading.value.toFixed(1)} {reading.unit}
                    </span>
                    {reading.value > 20 && reading.unit === "°C" ? (
                      <CheckCircle2 className="h-5 w-5 text-success" />
                    ) : (
                      <CheckCircle2 className="h-5 w-5 text-success" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sensor Readings Table */}
      <Card>
        <CardHeader>
          <CardTitle>Citiri curente</CardTitle>
          <CardDescription>Toate valorile măsurate de senzori în timp real</CardDescription>
        </CardHeader>
        <CardContent>
              <div className="overflow-x-auto -mx-6 px-6">
                <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold">Parametru</th>
                  <th className="text-right py-3 px-4 font-semibold">Valoare</th>
                  <th className="text-left py-3 px-4 font-semibold">Unitate</th>
                  <th className="text-left py-3 px-4 font-semibold hidden md:table-cell">Senzor</th>
                  <th className="text-left py-3 px-4 font-semibold hidden lg:table-cell">Referință</th>
                  <th className="text-left py-3 px-4 font-semibold hidden xl:table-cell">Ultimul update</th>
                </tr>
              </thead>
              <tbody>
                {readings.map((reading, idx) => (
                  <tr key={idx} className="border-b hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4 font-medium">{reading.parameter}</td>
                    <td className="py-3 px-4 text-right font-bold">
                      {reading.unit === "lx" ? Math.round(reading.value) : reading.value.toFixed(1)}
                    </td>
                    <td className="py-3 px-4">{reading.unit}</td>
                    <td className="py-3 px-4 text-muted-foreground hidden md:table-cell">
                      {reading.sensor}
                    </td>
                    <td className="py-3 px-4 text-xs text-muted-foreground font-mono hidden lg:table-cell">
                      {reading.reference}
                    </td>
                    <td className="py-3 px-4 text-sm text-muted-foreground hidden xl:table-cell">
                      {reading.timestamp}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
