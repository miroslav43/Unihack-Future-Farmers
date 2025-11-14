import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { ChevronUp, ChevronDown, Maximize2, Grid3x3 } from "lucide-react";
import { toast } from "sonner";

interface MotorConfig {
  id: number;
  speed: number;
  distance: number;
}

export default function ControlSera() {
  const [selectedCell, setSelectedCell] = useState<number | null>(null);
  const [roofPosition, setRoofPosition] = useState<"closed" | "partial" | "full">("closed");
  const [motors, setMotors] = useState<MotorConfig[]>([
    { id: 1, speed: 50, distance: 100 },
    { id: 2, speed: 50, distance: 100 },
    { id: 3, speed: 50, distance: 100 },
    { id: 4, speed: 50, distance: 100 },
  ]);

  const handleCellClick = (index: number) => {
    setSelectedCell(index);
    const row = Math.floor(index / 5) + 1;
    const col = (index % 5) + 1;
    toast.success(`Motoare trimise către poziția (${row}, ${col})`);
  };

  const handleRoofControl = (action: "closed" | "partial" | "full") => {
    setRoofPosition(action);
    const messages = {
      closed: "Acoperișul se închide complet",
      partial: "Acoperișul se deschide parțial",
      full: "Acoperișul se deschide complet",
    };
    toast.success(messages[action]);
  };

  const updateMotor = (id: number, field: "speed" | "distance", value: number) => {
    setMotors((prev) =>
      prev.map((motor) =>
        motor.id === id ? { ...motor, [field]: value } : motor
      )
    );
  };

  const sendMotorCommand = (motorId: number) => {
    const motor = motors.find((m) => m.id === motorId);
    toast.success(`Motor ${motorId}: Viteză ${motor?.speed}%, Distanță ${motor?.distance}cm`);
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex items-center gap-3">
        <Grid3x3 className="h-6 w-6 sm:h-8 sm:w-8 text-primary" />
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Control Seră</h1>
          <p className="text-muted-foreground">
            Controlează acoperișul, poziționează motoarele și setează parametrii
          </p>
        </div>
      </div>

      {/* Control Acoperis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChevronUp className="h-5 w-5" />
            Control Acoperis
          </CardTitle>
          <CardDescription>Deschide sau închide acoperișul serei</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button
              variant={roofPosition === "closed" ? "default" : "outline"}
              onClick={() => handleRoofControl("closed")}
              className="flex-1 min-w-[120px]"
            >
              <ChevronDown className="h-4 w-4 mr-2" />
              Închide Total
            </Button>
            <Button
              variant={roofPosition === "partial" ? "default" : "outline"}
              onClick={() => handleRoofControl("partial")}
              className="flex-1 min-w-[120px]"
            >
              <Maximize2 className="h-4 w-4 mr-2" />
              Deschide Parțial
            </Button>
            <Button
              variant={roofPosition === "full" ? "default" : "outline"}
              onClick={() => handleRoofControl("full")}
              className="flex-1 min-w-[120px]"
            >
              <ChevronUp className="h-4 w-4 mr-2" />
              Deschide Complet
            </Button>
          </div>
          
          {/* Visual indicator */}
          <div className="mt-6 relative">
            <div className="h-32 bg-muted/30 rounded-lg border-2 border-border relative overflow-hidden">
              <div className="absolute inset-x-0 bottom-0 h-24 bg-success/20 border-t-2 border-success/40" />
              <div
                className="absolute inset-x-0 top-0 bg-primary/80 transition-all duration-700 ease-in-out rounded-t-lg"
                style={{
                  height: roofPosition === "closed" ? "100%" : roofPosition === "partial" ? "50%" : "0%",
                }}
              >
                <div className="absolute inset-0 flex items-center justify-center text-primary-foreground font-semibold">
                  {roofPosition === "closed" ? "Închis" : roofPosition === "partial" ? "Parțial" : ""}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Matrice Poziționare */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Grid3x3 className="h-5 w-5" />
            Matrice Poziționare (5x3)
          </CardTitle>
          <CardDescription>
            Apasă pe o celulă pentru a trimite motoarele în acea zonă
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 gap-2 sm:gap-3 max-w-3xl mx-auto">
            {Array.from({ length: 15 }, (_, i) => (
              <button
                key={i}
                onClick={() => handleCellClick(i)}
                className={`
                  aspect-square rounded-lg border-2 transition-all duration-200
                  flex items-center justify-center font-bold text-sm sm:text-lg
                  ${
                    selectedCell === i
                      ? "bg-primary text-primary-foreground border-primary shadow-lg scale-105"
                      : "bg-card hover:bg-muted border-border hover:border-primary/50 hover:scale-105"
                  }
                `}
              >
                {i + 1}
              </button>
            ))}
          </div>
          {selectedCell !== null && (
            <div className="mt-4 text-center text-sm text-muted-foreground">
              Ultima poziție selectată: <span className="font-bold text-foreground">Celula {selectedCell + 1}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Control Motoare */}
      <Card>
        <CardHeader>
          <CardTitle>Control Motoare Individual</CardTitle>
          <CardDescription>Setează viteza și distanța pentru fiecare motor</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:gap-6 md:grid-cols-2">
            {motors.map((motor) => (
              <Card key={motor.id} className="bg-muted/30">
                <CardHeader>
                  <CardTitle className="text-lg">Motor {motor.id}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor={`speed-${motor.id}`}>Viteză</Label>
                      <span className="text-sm font-bold text-primary">{motor.speed}%</span>
                    </div>
                    <Slider
                      id={`speed-${motor.id}`}
                      value={[motor.speed]}
                      onValueChange={([value]) => updateMotor(motor.id, "speed", value)}
                      min={0}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor={`distance-${motor.id}`}>Distanță</Label>
                      <span className="text-sm font-bold text-primary">{motor.distance} cm</span>
                    </div>
                    <Slider
                      id={`distance-${motor.id}`}
                      value={[motor.distance]}
                      onValueChange={([value]) => updateMotor(motor.id, "distance", value)}
                      min={0}
                      max={500}
                      step={10}
                      className="w-full"
                    />
                  </div>

                  <Button
                    onClick={() => sendMotorCommand(motor.id)}
                    className="w-full"
                  >
                    Trimite Comandă
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
