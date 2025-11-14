import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Download, FileText } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const generate7DayData = () => {
  const data = [];
  const now = new Date();
  for (let i = 6; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
    data.push({
      date: date.toLocaleDateString("ro-RO", { day: "2-digit", month: "short" }),
      temp: 18 + Math.random() * 12,
      humidity: 45 + Math.random() * 25,
      soil: 35 + Math.random() * 20,
      light: 8000 + Math.random() * 10000,
      water: 60 + Math.random() * 30,
    });
  }
  return data;
};

const events = [
  { time: "30.10.2025 18:23", type: "Alertă", details: "Umiditate sol scăzută (<35%) - Parcelă A" },
  { time: "30.10.2025 14:15", type: "Info", details: "Irigare automată pornită - 15 minute" },
  { time: "30.10.2025 09:42", type: "Alertă", details: "Temperatură ridicată (>32°C)" },
  { time: "29.10.2025 21:10", type: "Info", details: "Nivel apă rezervor: 45% - reumplere recomandată" },
  { time: "29.10.2025 16:30", type: "Success", details: "AI: Frunze sănătoase detectate - toate parcelele" },
  { time: "29.10.2025 12:18", type: "Alertă", details: "Ploaie detectată - irigare automată oprită" },
  { time: "28.10.2025 19:05", type: "Info", details: "Analiză AI completată - insecte risc scăzut" },
];

export default function Rapoarte() {
  const { toast } = useToast();
  const historicalData = generate7DayData();

  const handleExport = (format: string) => {
    toast({
      title: `Export ${format.toUpperCase()}`,
      description: "Fișierul va fi descărcat în câteva secunde...",
    });
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Rapoarte & Istoric</h1>
        <p className="text-muted-foreground">
          Istoricul complet al senzorilor și evenimente importante
        </p>
      </div>

      {/* Historical Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>Istoric senzori (7 zile)</CardTitle>
              <CardDescription>Evoluția parametrilor măsurați în ultima săptămână</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => handleExport("csv")}>
                <Download className="h-4 w-4 mr-2" />
                CSV
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport("png")}>
                <Download className="h-4 w-4 mr-2" />
                PNG
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport("pdf")}>
                <Download className="h-4 w-4 mr-2" />
                PDF
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={historicalData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="temp"
                stroke="hsl(var(--chart-1))"
                strokeWidth={2}
                name="Temperatură (°C)"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="humidity"
                stroke="hsl(var(--chart-2))"
                strokeWidth={2}
                name="Umiditate aer (%)"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="soil"
                stroke="hsl(var(--chart-3))"
                strokeWidth={2}
                name="Umiditate sol (%)"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Events Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Evenimente & alarme
          </CardTitle>
          <CardDescription>Istoric evenimente din ultimele 30 zile</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold">Timp</th>
                  <th className="text-left py-3 px-4 font-semibold">Tip</th>
                  <th className="text-left py-3 px-4 font-semibold">Detalii</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event, idx) => (
                  <tr key={idx} className="border-b hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4 text-sm text-muted-foreground whitespace-nowrap">
                      {event.time}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          event.type === "Alertă"
                            ? "bg-destructive/10 text-destructive"
                            : event.type === "Success"
                            ? "bg-success/10 text-success"
                            : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {event.type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm">{event.details}</td>
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
