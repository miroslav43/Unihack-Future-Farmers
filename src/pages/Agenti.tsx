import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Cloud, Sprout, Users, Lightbulb, Wallet, Send } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

const agents = [
  {
    id: "weather",
    title: "Agent Meteo",
    description: "Întreabă despre vremea de azi și prognoza (+/- 1 lună).",
    tools: ["Web scraping / API meteo"],
    icon: Cloud,
  },
  {
    id: "crop",
    title: "Evoluție cultură",
    description: "Zile până la recoltare, estimări producție, remorci necesare.",
    tools: ["Senzori + istoric + modele simple"],
    icon: Sprout,
  },
  {
    id: "customers",
    title: "Clienți & Vânzări",
    description: "Proiecții de profit bazate pe vânzări istorice.",
    tools: ["Fișiere CSV/Excel"],
    icon: Wallet,
  },
  {
    id: "advisor",
    title: "Recomandări globale",
    description: "Analizează sezonul și recomandă ce să plantezi.",
    tools: ["Modele predictive"],
    icon: Lightbulb,
  },
  {
    id: "employees",
    title: "Monitorizare angajați",
    description: "Cost combustibil, salarii, planificare plăți.",
    tools: ["Baze de date interne"],
    icon: Users,
  },
];

interface Message {
  role: "user" | "agent";
  content: string;
  agentName?: string;
}

export default function Agenti() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !selectedAgent) return;

    const agent = agents.find((a) => a.id === selectedAgent);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: inputMessage },
    ]);

    // Simulate agent response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          content: getAgentResponse(selectedAgent, inputMessage),
          agentName: agent?.title,
        },
      ]);
    }, 1000);

    setInputMessage("");
  };

  const getAgentResponse = (agentId: string, question: string): string => {
    const responses: Record<string, string> = {
      weather:
        "Conform prognozei, pentru următoarele 7 zile temperaturile vor varia între 20-28°C, cu posibilitate de ploaie joi și vineri. Recomand planificarea irigării pentru luni și marți.",
      crop:
        "Bazat pe datele actuale și ritmul de creștere, roșiile vor fi gata de recoltat în aproximativ 12-14 zile. Estimez o producție de ~2.5 tone, necesitând 2 remorci pentru transport.",
      customers:
        "Analizând vânzările din ultimele 6 luni, profitul mediu lunar este de 15,200 RON. Pentru luna viitoare, proiectez o creștere de 8% datorită sezonului favorabil.",
      advisor:
        "Pentru plantarea de toamnă, recomand: ardei kapia (cerere mare), varză (rezistentă la frig), și spanac. Evită culturile sensibile la temperaturi sub 10°C.",
      employees:
        "Costul total lunar pentru 4 angajați: 12,400 RON (salarii) + 850 RON (combustibil). Următoarea plată programată: 25 noiembrie. Bugetul este în limitele normale.",
    };

    return responses[agentId] || "Procesez întrebarea ta și voi reveni cu un răspuns detaliat...";
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">Agenți inteligenți</h1>
        <p className="text-muted-foreground">
          Asistent AI specializat pentru diverse aspecte ale fermei
        </p>
      </div>

      <div className="grid gap-4 md:gap-6 lg:grid-cols-3">
        {/* Agent Cards */}
        <div className="lg:col-span-1 space-y-3 md:space-y-4">
          {agents.map((agent) => {
            const Icon = agent.icon;
            return (
              <Card
                key={agent.id}
                className={`cursor-pointer transition-all hover:shadow-lg ${
                  selectedAgent === agent.id ? "ring-2 ring-primary" : ""
                }`}
                onClick={() => setSelectedAgent(agent.id)}
              >
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Icon className="h-5 w-5 text-primary" />
                    {agent.title}
                  </CardTitle>
                  <CardDescription className="text-sm">{agent.description}</CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>

        {/* Chat Panel */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>
              {selectedAgent
                ? agents.find((a) => a.id === selectedAgent)?.title
                : "Selectează un agent"}
            </CardTitle>
            <CardDescription>
              {selectedAgent
                ? "Pune întrebări agentului selectat"
                : "Alege un agent din listă pentru a începe conversația"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <ScrollArea className="h-[400px] pr-4">
              {messages.length === 0 && selectedAgent && (
                <div className="text-center py-12 text-muted-foreground">
                  <p>Nu există mesaje încă. Începe conversația!</p>
                </div>
              )}
              
              {messages.length === 0 && !selectedAgent && (
                <div className="text-center py-12 text-muted-foreground">
                  <p>Selectează un agent pentru a începe</p>
                </div>
              )}

              <div className="space-y-4">
                {messages.map((message, idx) => (
                  <div
                    key={idx}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      {message.role === "agent" && message.agentName && (
                        <p className="text-xs font-semibold mb-1 opacity-70">
                          {message.agentName}
                        </p>
                      )}
                      <p className="text-sm">{message.content}</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            <div className="flex gap-2">
              <Input
                placeholder={
                  selectedAgent
                    ? "Întreabă agentul..."
                    : "Selectează un agent pentru a începe"
                }
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                disabled={!selectedAgent}
              />
              <Button onClick={handleSendMessage} disabled={!selectedAgent || !inputMessage.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
