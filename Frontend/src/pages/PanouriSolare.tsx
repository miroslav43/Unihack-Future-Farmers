import { Battery, Sun, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export default function PanouriSolare() {
  // Sample data
  const solarOutput = 3.2; // kW
  const batteryLevel = 76; // %
  const batteryCapacity = 10; // kWh
  const consumption = 1.8; // kW

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Panouri Solare</h1>
        <p className="text-muted-foreground mt-2">
          Monitorizare producție solară și nivel baterie în timp real
        </p>
      </div>

      {/* Energy Flow Animation */}
      <Card className="overflow-hidden bg-gradient-to-br from-background to-accent/5">
        <CardHeader>
          <CardTitle>Flux Energie</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative py-16 px-4">
            <div className="flex items-center justify-between">
              {/* Solar Panel Grid with Sun Rays */}
              <div className="flex flex-col items-center gap-4 z-10">
                <div className="relative">
                  {/* Sun rays animation */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    {[...Array(8)].map((_, i) => (
                      <div
                        key={i}
                        className="absolute w-1 bg-gradient-to-t from-yellow-400/60 to-transparent rounded-full animate-sun-ray"
                        style={{
                          height: '40px',
                          transform: `rotate(${i * 45}deg)`,
                          transformOrigin: 'center 60px',
                          animationDelay: `${i * 0.1}s`
                        }}
                      />
                    ))}
                  </div>
                  
                  {/* Solar Panels Grid (3x4 = 12 panels) */}
                  <div className="grid grid-cols-3 gap-1 p-3 bg-gradient-to-br from-gray-700 to-gray-800 rounded-2xl shadow-2xl relative z-10">
                    {[...Array(12)].map((_, i) => (
                      <div
                        key={i}
                        className="w-8 h-10 bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 rounded border border-blue-700/50 relative overflow-hidden animate-solar-shimmer"
                        style={{
                          animationDelay: `${i * 0.15}s`
                        }}
                      >
                        {/* Grid lines on panel */}
                        <div className="absolute inset-0 grid grid-cols-2 gap-[1px]">
                          {[...Array(4)].map((_, j) => (
                            <div key={j} className="bg-blue-700/20" />
                          ))}
                        </div>
                        {/* Shine effect */}
                        <div className="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent" />
                      </div>
                    ))}
                  </div>
                  
                  {/* Production indicator */}
                  <div className="absolute -top-2 -right-2 w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center animate-pulse shadow-lg">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-primary">{solarOutput} kW</p>
                  <p className="text-sm text-muted-foreground">Producție actuală</p>
                </div>
              </div>

              {/* Energy Flow Animation - Enhanced */}
              <div className="flex-1 relative h-20 mx-8">
                {/* Background glow */}
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-400/10 via-orange-400/10 to-primary/10 blur-xl rounded-full" />
                
                {/* Multiple flow lines */}
                <div className="absolute top-1/2 -translate-y-1/2 w-full h-3 overflow-hidden">
                  {[...Array(3)].map((_, lineIndex) => (
                    <div
                      key={lineIndex}
                      className="absolute w-full h-[2px] overflow-hidden"
                      style={{ top: `${lineIndex * 5}px` }}
                    >
                      {[...Array(6)].map((_, i) => (
                        <div
                          key={i}
                          className="absolute h-full w-12 rounded-full animate-flow-energy"
                          style={{
                            background: `linear-gradient(90deg, transparent, ${
                              lineIndex === 0 ? '#facc15' : lineIndex === 1 ? '#fb923c' : '#2E7D32'
                            }, transparent)`,
                            animationDelay: `${i * 0.6 + lineIndex * 0.2}s`,
                            left: '-3rem'
                          }}
                        />
                      ))}
                    </div>
                  ))}
                </div>
                
                {/* Energy particles */}
                {[...Array(8)].map((_, i) => (
                  <div
                    key={i}
                    className="absolute w-2 h-2 bg-yellow-400 rounded-full animate-flow-particles"
                    style={{
                      animationDelay: `${i * 0.5}s`,
                      top: `${Math.random() * 60 + 10}%`
                    }}
                  />
                ))}
              </div>

              {/* Battery with charging animation */}
              <div className="flex flex-col items-center gap-4 z-10">
                <div className="relative">
                  {/* Battery body */}
                  <div className="relative w-32 h-40 rounded-2xl bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center shadow-2xl border-4 border-gray-600 overflow-hidden">
                    {/* Battery terminal */}
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-12 h-3 bg-gray-600 rounded-t-lg" />
                    
                    {/* Battery level fill */}
                    <div className="absolute bottom-0 left-0 right-0 transition-all duration-1000 ease-out" style={{ height: `${batteryLevel}%` }}>
                      <div className="absolute inset-0 bg-gradient-to-t from-success via-accent to-success/80" />
                      <div className="absolute inset-0 bg-gradient-to-t from-transparent via-white/10 to-white/5" />
                      {/* Charging waves */}
                      <div className="absolute inset-0 overflow-hidden">
                        {[...Array(3)].map((_, i) => (
                          <div
                            key={i}
                            className="absolute w-full h-8 bg-white/10 animate-battery-wave"
                            style={{
                              bottom: `${i * 30}%`,
                              animationDelay: `${i * 0.5}s`
                            }}
                          />
                        ))}
                      </div>
                    </div>
                    
                    {/* Battery icon overlay */}
                    <Battery className="w-16 h-16 text-white/80 relative z-10" />
                    
                    {/* Percentage text */}
                    <div className="absolute inset-0 flex items-center justify-center z-20">
                      <span className="text-2xl font-bold text-white drop-shadow-lg">{batteryLevel}%</span>
                    </div>
                  </div>
                  
                  {/* Charging indicator */}
                  <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-gradient-to-br from-success to-accent rounded-full flex items-center justify-center animate-bounce shadow-lg">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-primary">{(batteryCapacity * batteryLevel / 100).toFixed(1)} kWh</p>
                  <p className="text-sm text-muted-foreground">Energie stocată</p>
                </div>
              </div>
            </div>
          </div>

          <style>{`
            @keyframes flow-energy {
              0% {
                transform: translateX(-3rem);
                opacity: 0;
              }
              15% {
                opacity: 1;
              }
              85% {
                opacity: 1;
              }
              100% {
                transform: translateX(calc(100% + 3rem));
                opacity: 0;
              }
            }
            
            @keyframes flow-particles {
              0% {
                transform: translateX(-1rem);
                opacity: 0;
                scale: 0.5;
              }
              10% {
                opacity: 1;
                scale: 1;
              }
              90% {
                opacity: 1;
                scale: 1;
              }
              100% {
                transform: translateX(calc(100% + 1rem));
                opacity: 0;
                scale: 0.5;
              }
            }
            
            @keyframes sun-ray {
              0%, 100% {
                opacity: 0.3;
                height: 40px;
              }
              50% {
                opacity: 0.8;
                height: 50px;
              }
            }
            
            @keyframes solar-shimmer {
              0%, 100% {
                box-shadow: inset 0 0 5px rgba(59, 130, 246, 0.3);
              }
              50% {
                box-shadow: inset 0 0 10px rgba(96, 165, 250, 0.6);
              }
            }
            
            @keyframes battery-wave {
              0% {
                transform: translateY(0);
                opacity: 0.5;
              }
              100% {
                transform: translateY(-100%);
                opacity: 0;
              }
            }
            
            .animate-flow-energy {
              animation: flow-energy 3.5s infinite linear;
            }
            
            .animate-flow-particles {
              animation: flow-particles 4s infinite linear;
            }
            
            .animate-sun-ray {
              animation: sun-ray 2s infinite ease-in-out;
            }
            
            .animate-solar-shimmer {
              animation: solar-shimmer 3s infinite ease-in-out;
            }
            
            .animate-battery-wave {
              animation: battery-wave 2s infinite linear;
            }
          `}</style>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Producție Zilnică</CardTitle>
            <Sun className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24.8 kWh</div>
            <p className="text-xs text-muted-foreground">
              +12% față de ieri
            </p>
            <Progress value={82} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Capacitate Baterie</CardTitle>
            <Battery className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(batteryCapacity * batteryLevel / 100).toFixed(1)} kWh</div>
            <p className="text-xs text-muted-foreground">
              din {batteryCapacity} kWh total
            </p>
            <Progress value={batteryLevel} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Consum Actual</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{consumption} kW</div>
            <p className="text-xs text-muted-foreground">
              Surplus: {(solarOutput - consumption).toFixed(1)} kW
            </p>
            <Progress value={(consumption / solarOutput) * 100} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Panel Details */}
      <Card>
        <CardHeader>
          <CardTitle>Detalii Panouri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Număr panouri</p>
                <p className="text-lg font-semibold">12 panouri</p>
              </div>
              <div>
                <p className="text-muted-foreground">Putere totală</p>
                <p className="text-lg font-semibold">4.8 kWp</p>
              </div>
              <div>
                <p className="text-muted-foreground">Eficiență actuală</p>
                <p className="text-lg font-semibold">67%</p>
              </div>
              <div>
                <p className="text-muted-foreground">Ore soare astăzi</p>
                <p className="text-lg font-semibold">6.2h</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Battery Info */}
      <Card>
        <CardHeader>
          <CardTitle>Informații Baterie</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Tip baterie</p>
              <p className="text-lg font-semibold">LiFePO4</p>
            </div>
            <div>
              <p className="text-muted-foreground">Cicli efectuați</p>
              <p className="text-lg font-semibold">342 / 5000</p>
            </div>
            <div>
              <p className="text-muted-foreground">Temperatură</p>
              <p className="text-lg font-semibold">28°C</p>
            </div>
            <div>
              <p className="text-muted-foreground">Stare</p>
              <p className="text-lg font-semibold text-success">Încărcare</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
