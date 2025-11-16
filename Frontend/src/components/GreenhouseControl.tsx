/**
 * Componenta de control pentru sera cu grilă 3x4
 * Dimensiuni seră: 45cm (lățime - X) x 63cm (lungime - Y)
 * Grilă: 3 coloane (pe X) x 4 rânduri (pe Y) = 12 poziții
 */
import {
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Crosshair,
  Grid3x3,
  Home,
  Loader2,
  MapPin,
  Settings,
  Square,
  Unlock,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { greenhouseAPI, Position } from "../services/greenhouseAPI";
import { ManualMotorControl } from "./ManualMotorControl";

// Constante pentru seră (dimensiuni reale)
const GREENHOUSE_WIDTH = 45; // cm (X - latura scurtă)
const GREENHOUSE_HEIGHT = 63; // cm (Y - latura lungă)
const GRID_COLS = 3; // 3 coloane
const GRID_ROWS = 4; // 4 rânduri
const DEFAULT_HOME_POSITION: Position = { x: 22.5, y: 31.5 }; // Centrul geometric default

// Poziții RELATIVE la HOME (0,0) pentru fiecare plantă
// X: -12, 0, +12 cm (3 coloane)
// Y: +18, +9, -9, -18 cm (4 rânduri) - nu există Y=0
const PLANT_POSITIONS_RELATIVE = [
  // Rând 1 (Y = +18cm)
  { x: -12, y: 18 }, // Poziția 1
  { x: 0, y: 18 }, // Poziția 2
  { x: 12, y: 18 }, // Poziția 3
  // Rând 2 (Y = +9cm)
  { x: -12, y: 9 }, // Poziția 4
  { x: 0, y: 9 }, // Poziția 5
  { x: 12, y: 9 }, // Poziția 6
  // Rând 3 (Y = -9cm)
  { x: -12, y: -9 }, // Poziția 7
  { x: 0, y: -9 }, // Poziția 8
  { x: 12, y: -9 }, // Poziția 9
  // Rând 4 (Y = -18cm)
  { x: -12, y: -18 }, // Poziția 10
  { x: 0, y: -18 }, // Poziția 11
  { x: 12, y: -18 }, // Poziția 12
];

export function GreenhouseControl() {
  const [activeTab, setActiveTab] = useState<"grid" | "manual">("grid");
  const [currentPosition, setCurrentPosition] = useState<Position>(() => {
    // Încarcă poziția din localStorage sau folosește default
    const saved = localStorage.getItem("greenhousePosition");
    return saved ? JSON.parse(saved) : DEFAULT_HOME_POSITION;
  });
  const [homePosition, setHomePosition] = useState<Position>(() => {
    // Încarcă poziția HOME din localStorage sau folosește default
    const saved = localStorage.getItem("greenhouseHomePosition");
    return saved ? JSON.parse(saved) : DEFAULT_HOME_POSITION;
  });
  const [positionOffset, setPositionOffset] = useState<Position>(() => {
    // Offset pentru calibrare - diferența între poziția fizică și logică
    const saved = localStorage.getItem("greenhousePositionOffset");
    return saved ? JSON.parse(saved) : { x: 0, y: 0 };
  });
  const [isMoving, setIsMoving] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPosition, setSelectedPosition] = useState<number | null>(null);
  const [showCalibration, setShowCalibration] = useState(false);
  const [roofMoving, setRoofMoving] = useState(false);
  const [autoTourRunning, setAutoTourRunning] = useState(false);

  // useRef pentru verificare INSTANT a AUTO TOUR (nu async ca state)
  const autoTourRunningRef = useRef(false);

  // Check conexiune la montare
  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 10000); // Check la fiecare 10s
    return () => clearInterval(interval);
  }, []);

  const checkConnection = async () => {
    try {
      const health = await greenhouseAPI.checkHealth();
      setIsConnected(health.esp32_reachable);
      setError(null);
    } catch (err) {
      setIsConnected(false);
      setError("Nu se poate conecta la API");
    }
  };

  const moveToPosition = async (positionIndex: number) => {
    if (isMoving) return;

    // Obține poziția relativă la HOME
    const relativePos = PLANT_POSITIONS_RELATIVE[positionIndex];

    // Calculează poziția absolută (HOME + offset relativ)
    const targetAbsolute = {
      x: homePosition.x + relativePos.x,
      y: homePosition.y + relativePos.y,
    };

    setIsMoving(true);
    setError(null);

    try {
      const response = await greenhouseAPI.moveToPosition({
        target_x: targetAbsolute.x,
        target_y: targetAbsolute.y,
        current_x: currentPosition.x,
        current_y: currentPosition.y,
        speed: 8,
      });

      setCurrentPosition({
        x: response.new_position.x,
        y: response.new_position.y,
      });
      setSelectedPosition(positionIndex);

      // Salvează poziția în localStorage
      localStorage.setItem(
        "greenhousePosition",
        JSON.stringify(response.new_position)
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Eroare la mișcare");
    } finally {
      setIsMoving(false);
    }
  };

  const goHome = async () => {
    if (isMoving) return;

    setIsMoving(true);
    setError(null);

    try {
      // Mută la poziția HOME salvată
      const response = await greenhouseAPI.moveToPosition({
        target_x: homePosition.x,
        target_y: homePosition.y,
        current_x: currentPosition.x,
        current_y: currentPosition.y,
        speed: 8,
      });

      setCurrentPosition({
        x: response.new_position.x,
        y: response.new_position.y,
      });
      setSelectedPosition(null);

      // Salvează poziția în localStorage
      localStorage.setItem(
        "greenhousePosition",
        JSON.stringify(response.new_position)
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Eroare la întoarcere HOME"
      );
    } finally {
      setIsMoving(false);
    }
  };

  const setAsHomePosition = () => {
    // Setează poziția curentă ca fiind HOME (0, 0)
    const newHomePosition = { ...currentPosition };
    setHomePosition(newHomePosition);

    // Salvează în localStorage
    localStorage.setItem(
      "greenhouseHomePosition",
      JSON.stringify(newHomePosition)
    );

    // Calculează offset-ul
    const newOffset = {
      x: currentPosition.x - DEFAULT_HOME_POSITION.x,
      y: currentPosition.y - DEFAULT_HOME_POSITION.y,
    };
    setPositionOffset(newOffset);
    localStorage.setItem("greenhousePositionOffset", JSON.stringify(newOffset));

    setError(null);
    alert(
      `✅ Poziția HOME setată la:\nX: ${newHomePosition.x.toFixed(
        2
      )} cm\nY: ${newHomePosition.y.toFixed(
        2
      )} cm\n\nAcest punct este acum considerat centrul (0,0) al serei.`
    );
  };

  const resetCalibration = () => {
    // Resetează la valorile default
    setHomePosition(DEFAULT_HOME_POSITION);
    setPositionOffset({ x: 0, y: 0 });

    localStorage.setItem(
      "greenhouseHomePosition",
      JSON.stringify(DEFAULT_HOME_POSITION)
    );
    localStorage.removeItem("greenhousePositionOffset");

    alert("✅ Calibrarea a fost resetată la valorile default.");
  };

  const emergencyStop = async () => {
    try {
      // Oprește AUTO TOUR dacă rulează
      setAutoTourRunning(false);
      autoTourRunningRef.current = false;

      await greenhouseAPI.emergencyStop();
      setIsMoving(false);
      setRoofMoving(false);
      setError(null);
    } catch (err) {
      setError("Eroare la emergency stop");
    }
  };

  const emergencyReleaseAll = async () => {
    if (
      !window.confirm(
        "⚠️ ATENȚIE: Vei relaxa TOATE motoarele (fără tensiune)!\n\nMotoarele vor deveni MOALE și nu vor mai ține poziția.\n\nContinui?"
      )
    ) {
      return;
    }

    try {
      const response = await fetch("http://localhost:8009/motors/release", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ motors: "all" }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      setIsMoving(false);
      setRoofMoving(false);
      setError(null);
      alert(
        "✅ TOATE motoarele au fost relaxate!\n\nMotoarele sunt acum MOALE și fără tensiune."
      );
    } catch (err) {
      setError("Eroare la emergency release all");
      console.error(err);
    }
  };

  // AUTO TOUR: Parcurge toate plantele în ordine ZIG-ZAG
  const startAutoTour = async () => {
    if (isMoving) return;

    const confirmed = window.confirm(
      "🤖 AUTO TOUR ZIG-ZAG\n\n" +
        "Sistemul va parcurge automat toate cele 12 plante:\n" +
        "• Rând 1: 🌱1 → 🌱2 → 🌱3 (stânga→dreapta)\n" +
        "• Rând 2: 🌱6 → 🌱5 → 🌱4 (dreapta→stânga)\n" +
        "• Rând 3: 🌱7 → 🌱8 → 🌱9 (stânga→dreapta)\n" +
        "• Rând 4: 🌱12 → 🌱11 → 🌱10 (dreapta→stânga)\n" +
        "• Delay 1 sec la fiecare plantă\n" +
        "• Delay 1 sec între rânduri\n" +
        "• La final: întoarcere la HOME (0,0)\n\n" +
        "Continui?"
    );

    if (!confirmed) return;

    setIsMoving(true);
    setAutoTourRunning(true);
    autoTourRunningRef.current = true; // Setează flag-ul INSTANT
    setError(null);

    try {
      // Ordinea ZIG-ZAG: 1,2,3 -> 6,5,4 -> 7,8,9 -> 12,11,10
      const zigzagOrder = [
        0,
        1,
        2, // Rând 1: index 0,1,2 (plante 1,2,3)
        5,
        4,
        3, // Rând 2: index 5,4,3 (plante 6,5,4) - INVERS
        6,
        7,
        8, // Rând 3: index 6,7,8 (plante 7,8,9)
        11,
        10,
        9, // Rând 4: index 11,10,9 (plante 12,11,10) - INVERS
      ];

      for (let step = 0; step < zigzagOrder.length; step++) {
        // Verifică dacă EMERGENCY STOP a fost apăsat
        if (!autoTourRunningRef.current) {
          console.log("[AUTO TOUR] Oprit prin EMERGENCY STOP");
          break;
        }

        const i = zigzagOrder[step];
        const relativePos = PLANT_POSITIONS_RELATIVE[i];
        const targetAbsolute = {
          x: homePosition.x + relativePos.x,
          y: homePosition.y + relativePos.y,
        };

        // Calculează distanța și timpul necesar pentru mișcare
        const deltaX = Math.abs(targetAbsolute.x - currentPosition.x);
        const deltaY = Math.abs(targetAbsolute.y - currentPosition.y);
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const speed = 8; // cm/s

        // Timp realist: include accelerare/decelerare + overhead motor
        // Formula: (distanță / viteză) * 2.0 pentru overhead FOARTE realist
        const baseTravelTime = (distance / speed) * 1000; // milisecunde
        const realisticTravelTime = baseTravelTime * 2.0; // ×2 pentru siguranță (accelerare + decelerare + overhead)

        console.log(
          `[AUTO TOUR] Planta ${i + 1}: (${relativePos.x}, ${
            relativePos.y
          }) - Dist: ${distance.toFixed(1)}cm, Timp estimat: ${(
            realisticTravelTime / 1000
          ).toFixed(1)}s`
        );

        const response = await greenhouseAPI.moveToPosition({
          target_x: targetAbsolute.x,
          target_y: targetAbsolute.y,
          current_x: currentPosition.x,
          current_y: currentPosition.y,
          speed: speed,
        });

        // Actualizează poziția curentă
        const newPosition = {
          x: response.new_position.x,
          y: response.new_position.y,
        };
        setCurrentPosition(newPosition);
        setSelectedPosition(i);

        localStorage.setItem("greenhousePosition", JSON.stringify(newPosition));

        // Verifică din nou dacă EMERGENCY STOP a fost apăsat
        if (!autoTourRunningRef.current) {
          console.log("[AUTO TOUR] Oprit prin EMERGENCY STOP");
          break;
        }

        // AȘTEAPTĂ ca motorul să ajungă la destinație
        // Buffer de 3 secunde pentru siguranță + timp realist de călătorie
        const waitTime = Math.max(realisticTravelTime + 3000, 3000); // Minimum 3 secunde
        console.log(
          `[AUTO TOUR] ⏱️ Aștept ${(waitTime / 1000).toFixed(
            1
          )}s ca motorul să execute comanda...`
        );
        await new Promise((resolve) => setTimeout(resolve, waitTime));

        // Verifică din nou după ce motorul a ajuns
        if (!autoTourRunningRef.current) {
          console.log("[AUTO TOUR] Oprit prin EMERGENCY STOP");
          break;
        }

        // La finalul fiecărui rând (după 3 plante), PAUZĂ 2 secunde între rânduri
        if ((step + 1) % 3 === 0 && step < zigzagOrder.length - 1) {
          console.log(
            `[AUTO TOUR] 🔄 Schimbare rând - Pauză 2 sec (după planta ${i + 1})`
          );
          await new Promise((resolve) => setTimeout(resolve, 2000));

          // Verifică din nou după pauză
          if (!autoTourRunningRef.current) {
            console.log("[AUTO TOUR] Oprit prin EMERGENCY STOP");
            break;
          }
        }

        // Actualizează currentPosition pentru următoarea iterație
        currentPosition.x = newPosition.x;
        currentPosition.y = newPosition.y;
      }

      // Dacă nu a fost oprit prin EMERGENCY STOP, merge la HOME
      if (autoTourRunningRef.current) {
        // Așteaptă 2 secunde înainte de a merge la HOME
        console.log(
          "[AUTO TOUR] 🏠 Pregătire întoarcere la HOME - Pauză 2 sec..."
        );
        await new Promise((resolve) => setTimeout(resolve, 2000));

        if (autoTourRunningRef.current) {
          // Calculează distanța până la HOME
          const deltaX = Math.abs(homePosition.x - currentPosition.x);
          const deltaY = Math.abs(homePosition.y - currentPosition.y);
          const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
          const speed = 8; // cm/s

          // Timp realist cu overhead
          const baseTravelTime = (distance / speed) * 1000;
          const realisticTravelTime = baseTravelTime * 2.0; // ×2 pentru siguranță

          console.log(
            `[AUTO TOUR] Întoarcere la HOME (0,0) - Dist: ${distance.toFixed(
              1
            )}cm, Timp estimat: ${(realisticTravelTime / 1000).toFixed(1)}s`
          );

          const homeResponse = await greenhouseAPI.moveToPosition({
            target_x: homePosition.x,
            target_y: homePosition.y,
            current_x: currentPosition.x,
            current_y: currentPosition.y,
            speed: speed,
          });

          setCurrentPosition({
            x: homeResponse.new_position.x,
            y: homeResponse.new_position.y,
          });
          setSelectedPosition(null);

          localStorage.setItem(
            "greenhousePosition",
            JSON.stringify(homeResponse.new_position)
          );

          // Așteaptă ca motorul să ajungă la HOME
          const waitTime = Math.max(realisticTravelTime + 3000, 3000); // Buffer 3 sec
          console.log(
            `[AUTO TOUR] ⏱️ Aștept ${(waitTime / 1000).toFixed(
              1
            )}s ca motorul să ajungă la HOME...`
          );
          await new Promise((resolve) => setTimeout(resolve, waitTime));

          alert(
            "✅ AUTO TOUR completat!\n\nToate plantele au fost vizitate și sistemul s-a întors la HOME."
          );
        }
      } else {
        alert("⚠️ AUTO TOUR oprit prin EMERGENCY STOP!");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Eroare la AUTO TOUR");
    } finally {
      setIsMoving(false);
      setAutoTourRunning(false);
      autoTourRunningRef.current = false;
    }
  };

  // Funcții control acoperiș
  const moveRoof = async (
    motors: string[],
    direction: 0 | 1,
    actionName: string
  ) => {
    if (roofMoving || isMoving) return;

    setRoofMoving(true);
    setError(null);

    try {
      const moveData: Record<
        string,
        { cm: number; speed: number; dir: number }
      > = {};

      motors.forEach((motor) => {
        moveData[motor] = {
          cm: 2, // 2cm distanță
          speed: 1, // 1cm/s viteză minimă
          dir: direction,
        };
      });

      const response = await fetch("http://localhost:8009/motors/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(moveData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Eroare la ${actionName}`);
      }

      const result = await response.json();
      console.log(`${actionName}:`, result);
    } catch (err) {
      setError(err instanceof Error ? err.message : `Eroare la ${actionName}`);
    } finally {
      setRoofMoving(false);
    }
  };

  const openRightRoof = () =>
    moveRoof(["roof_right"], 1, "deschidere acoperiș dreapta");
  const openLeftRoof = () =>
    moveRoof(["roof_left"], 1, "deschidere acoperiș stânga");
  const openBothRoofs = () =>
    moveRoof(["roof_left", "roof_right"], 1, "deschidere ambele acoperișuri");

  const closeRightRoof = () =>
    moveRoof(["roof_right"], 0, "închidere acoperiș dreapta");
  const closeLeftRoof = () =>
    moveRoof(["roof_left"], 0, "închidere acoperiș stânga");
  const closeBothRoofs = () =>
    moveRoof(["roof_left", "roof_right"], 0, "închidere ambele acoperișuri");

  const releaseRoofs = async () => {
    try {
      const response = await fetch("http://localhost:8009/motors/release", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ motors: ["roof_left", "roof_right"] }),
      });

      if (!response.ok) {
        throw new Error("Eroare la release");
      }

      setRoofMoving(false);
      setError(null);
    } catch (err) {
      setError("Eroare la release acoperișuri");
    }
  };

  // Calculează poziția relativă la HOME
  const getCurrentRelativePosition = (): Position => {
    return {
      x: currentPosition.x - homePosition.x,
      y: currentPosition.y - homePosition.y,
    };
  };

  // Găsește poziția curentă cea mai apropiată (pentru highlight)
  const findClosestPosition = (): number | null => {
    const relativePos = getCurrentRelativePosition();
    let closestIndex = 0;
    let minDistance = Infinity;

    PLANT_POSITIONS_RELATIVE.forEach((pos, index) => {
      const distance = Math.sqrt(
        Math.pow(pos.x - relativePos.x, 2) + Math.pow(pos.y - relativePos.y, 2)
      );
      if (distance < minDistance) {
        minDistance = distance;
        closestIndex = index;
      }
    });

    return minDistance < 2 ? closestIndex : null; // Toleranță 2cm
  };

  const closestPosition = findClosestPosition();
  const currentRelativePos = getCurrentRelativePosition();

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-lg p-6 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              🏡 Control Seră
            </h1>
            <p className="text-green-100 mt-1">
              {activeTab === "grid"
                ? "Grilă 3x4 - Poziționare precisă (12 poziții)"
                : "Control Manual Motoare"}
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2 justify-end">
              <div
                className={`w-3 h-3 rounded-full ${
                  isConnected ? "bg-green-400" : "bg-red-400"
                } animate-pulse`}
              />
              <span className="text-sm">
                {isConnected ? "Conectat" : "Deconectat"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b-2 border-gray-200">
        <button
          onClick={() => setActiveTab("grid")}
          className={`flex items-center gap-2 px-6 py-3 font-medium transition-all ${
            activeTab === "grid"
              ? "text-green-600 border-b-2 border-green-600 -mb-0.5"
              : "text-gray-600 hover:text-gray-800"
          }`}
        >
          <Grid3x3 className="w-5 h-5" />
          Grilă 3x4
        </button>
        <button
          onClick={() => setActiveTab("manual")}
          className={`flex items-center gap-2 px-6 py-3 font-medium transition-all ${
            activeTab === "manual"
              ? "text-purple-600 border-b-2 border-purple-600 -mb-0.5"
              : "text-gray-600 hover:text-gray-800"
          }`}
        >
          <Settings className="w-5 h-5" />
          Control Manual
        </button>
      </div>

      {/* Status Panel */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg p-4 shadow">
          <h3 className="text-sm font-medium text-gray-500 mb-2">
            Poziție Relativă la HOME
          </h3>
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">X:</span>
              <span
                className={`font-mono font-bold text-lg ${
                  Math.abs(currentRelativePos.x) < 0.5
                    ? "text-green-600"
                    : "text-blue-600"
                }`}
              >
                {currentRelativePos.x > 0 ? "+" : ""}
                {currentRelativePos.x.toFixed(1)} cm
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Y:</span>
              <span
                className={`font-mono font-bold text-lg ${
                  Math.abs(currentRelativePos.y) < 0.5
                    ? "text-green-600"
                    : "text-blue-600"
                }`}
              >
                {currentRelativePos.y > 0 ? "+" : ""}
                {currentRelativePos.y.toFixed(1)} cm
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-2 pt-2 border-t">
              Absolut: ({currentPosition.x.toFixed(1)},{" "}
              {currentPosition.y.toFixed(1)})
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 shadow">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Status</h3>
          <div className="flex items-center gap-2">
            {isMoving ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                <span className="text-blue-600 font-medium">În mișcare...</span>
              </>
            ) : (
              <>
                <Square className="w-5 h-5 text-green-600" />
                <span className="text-green-600 font-medium">Gata</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-red-800">Eroare</h4>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Content based on active tab */}
      {activeTab === "grid" && (
        <>
          {/* Roof Control Panel */}
          <div className="bg-gradient-to-r from-sky-50 to-blue-50 border-2 border-sky-200 rounded-lg p-5 shadow-md">
            <h3 className="text-lg font-bold text-sky-900 flex items-center gap-2 mb-4">
              <ChevronUp className="w-5 h-5" />
              Control Acoperiș
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Left Roof Controls */}
              <div className="bg-white rounded-lg p-4 border border-sky-200">
                <h4 className="font-semibold text-gray-700 mb-3 text-center">
                  Acoperiș Stânga
                </h4>
                <div className="space-y-2">
                  <button
                    onClick={openLeftRoof}
                    disabled={roofMoving || isMoving || !isConnected}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg 
                         flex items-center justify-center gap-2 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronUp className="w-5 h-5" />
                    Deschide Stânga
                  </button>
                  <button
                    onClick={closeLeftRoof}
                    disabled={roofMoving || isMoving || !isConnected}
                    className="w-full bg-orange-600 hover:bg-orange-700 text-white font-medium py-3 px-4 rounded-lg 
                         flex items-center justify-center gap-2 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronDown className="w-5 h-5" />
                    Închide Stânga
                  </button>
                </div>
              </div>

              {/* Right Roof Controls */}
              <div className="bg-white rounded-lg p-4 border border-sky-200">
                <h4 className="font-semibold text-gray-700 mb-3 text-center">
                  Acoperiș Dreapta
                </h4>
                <div className="space-y-2">
                  <button
                    onClick={openRightRoof}
                    disabled={roofMoving || isMoving || !isConnected}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg 
                         flex items-center justify-center gap-2 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronUp className="w-5 h-5" />
                    Deschide Dreapta
                  </button>
                  <button
                    onClick={closeRightRoof}
                    disabled={roofMoving || isMoving || !isConnected}
                    className="w-full bg-orange-600 hover:bg-orange-700 text-white font-medium py-3 px-4 rounded-lg 
                         flex items-center justify-center gap-2 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronDown className="w-5 h-5" />
                    Închide Dreapta
                  </button>
                </div>
              </div>
            </div>

            {/* Both Roofs + Release */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
              <button
                onClick={openBothRoofs}
                disabled={roofMoving || isMoving || !isConnected}
                className="bg-green-700 hover:bg-green-800 text-white font-bold py-3 px-4 rounded-lg 
                     flex items-center justify-center gap-2 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronUp className="w-5 h-5" />
                Deschide AMBELE
              </button>

              <button
                onClick={closeBothRoofs}
                disabled={roofMoving || isMoving || !isConnected}
                className="bg-orange-700 hover:bg-orange-800 text-white font-bold py-3 px-4 rounded-lg 
                     flex items-center justify-center gap-2 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronDown className="w-5 h-5" />
                Închide AMBELE
              </button>

              <button
                onClick={releaseRoofs}
                disabled={!isConnected}
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg 
                     flex items-center justify-center gap-2 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Unlock className="w-5 h-5" />
                RELEASE
              </button>
            </div>

            {/* Info */}
            <div className="bg-sky-100 rounded-lg p-3 text-xs text-sky-800 mt-4">
              <p className="font-medium mb-1">💡 Instrucțiuni:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>
                  <strong>Deschide/Închide:</strong> Mișcă acoperișul 2cm cu
                  viteză 1cm/s
                </li>
                <li>
                  <strong>RELEASE:</strong> Relaxează motoarele (moale) - pentru
                  ajustare manuală
                </li>
                <li>
                  Motoarele rămân "ținute" după mișcare până apeși RELEASE
                </li>
                <li>
                  Pentru siguranță, folosește RELEASE înainte de ajustări
                  manuale
                </li>
              </ul>
            </div>

            {roofMoving && (
              <div className="mt-3 flex items-center justify-center gap-2 text-blue-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm font-medium">
                  Acoperiș în mișcare...
                </span>
              </div>
            )}
          </div>

          {/* Calibration Panel */}
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-200 rounded-lg p-5 shadow-md">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-lg font-bold text-amber-900 flex items-center gap-2">
                  <Crosshair className="w-5 h-5" />
                  Calibrare Poziție HOME
                </h3>
                <p className="text-sm text-amber-700 mt-1">
                  Setează poziția curentă ca punct de referință (0,0)
                </p>
              </div>
              <button
                onClick={() => setShowCalibration(!showCalibration)}
                className="text-amber-600 hover:text-amber-800 text-sm font-medium"
              >
                {showCalibration ? "Ascunde ▲" : "Arată ▼"}
              </button>
            </div>

            {showCalibration && (
              <div className="space-y-3 mt-4 pt-4 border-t border-amber-200">
                <div className="bg-white rounded-lg p-3 border border-amber-200">
                  <div className="text-sm text-gray-600 space-y-1">
                    <div className="flex justify-between">
                      <span>Poziție HOME actuală:</span>
                      <span className="font-mono font-bold">
                        ({homePosition.x.toFixed(2)},{" "}
                        {homePosition.y.toFixed(2)})
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Offset calibrare:</span>
                      <span className="font-mono text-amber-600">
                        ({positionOffset.x.toFixed(2)},{" "}
                        {positionOffset.y.toFixed(2)})
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={setAsHomePosition}
                    disabled={isMoving || !isConnected}
                    className="flex-1 bg-amber-600 hover:bg-amber-700 text-white font-medium py-3 px-4 rounded-lg 
                         flex items-center justify-center gap-2 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <MapPin className="w-5 h-5" />
                    Setează ca HOME (0,0)
                  </button>

                  <button
                    onClick={resetCalibration}
                    className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-3 px-4 rounded-lg 
                         transition-colors"
                  >
                    Reset
                  </button>
                </div>

                <div className="bg-amber-100 rounded-lg p-3 text-xs text-amber-800">
                  <p className="font-medium mb-1">💡 Cum funcționează:</p>
                  <ol className="list-decimal list-inside space-y-1 ml-2">
                    <li>Mută motoarele în poziția dorită (manual sau grilă)</li>
                    <li>
                      Apasă "Setează ca HOME" pentru a marca poziția ca (0,0)
                    </li>
                    <li>
                      Toate mișcările ulterioare vor fi relative la acest punct
                    </li>
                    <li>Butonul "GO HOME" te va aduce înapoi aici</li>
                  </ol>
                </div>
              </div>
            )}
          </div>

          {/* Grid Control */}
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">
              Grilă Plante (3×4)
              <span className="text-sm text-gray-500 ml-2">
                Poziții relative la HOME (0,0)
              </span>
            </h2>

            {/* Legendă Coloane */}
            <div className="flex justify-around mb-2 text-xs text-gray-500 font-mono">
              <span>X: -12cm</span>
              <span>X: 0cm</span>
              <span>X: +12cm</span>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-2">
              {PLANT_POSITIONS_RELATIVE.map((pos, index) => {
                const isActive = closestPosition === index;
                const isSelected = selectedPosition === index;
                const buttonNum = index + 1;
                const isHomePosition = pos.x === 0 && pos.y === 0;

                return (
                  <button
                    key={index}
                    onClick={() => moveToPosition(index)}
                    disabled={isMoving || !isConnected}
                    className={`
                  relative p-4 rounded-lg font-medium transition-all transform
                  ${
                    isActive || isSelected
                      ? "bg-green-600 text-white scale-105 shadow-lg"
                      : isHomePosition
                      ? "bg-blue-100 text-blue-900 hover:bg-blue-200 border-2 border-blue-400"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }
                  ${
                    isMoving
                      ? "opacity-50 cursor-not-allowed"
                      : "hover:scale-105"
                  }
                  disabled:opacity-30 disabled:cursor-not-allowed
                `}
                  >
                    <div className="text-2xl font-bold mb-1">
                      {isHomePosition ? "🏠" : `🌱${buttonNum}`}
                    </div>
                    <div className="text-xs opacity-80">
                      ({pos.x > 0 ? "+" : ""}
                      {pos.x}, {pos.y > 0 ? "+" : ""}
                      {pos.y})
                    </div>
                    {isActive && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full animate-pulse" />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Legendă Rânduri */}
            <div className="flex justify-between text-xs text-gray-500 font-mono mt-2 px-2">
              <span>↑ Y: +18, +9, -9, -18 cm</span>
            </div>

            {/* Control Buttons */}
            <div className="flex flex-col gap-3">
              {/* Rând 1: GO HOME + AUTO TOUR */}
              <div className="flex gap-3">
                <button
                  onClick={goHome}
                  disabled={isMoving || !isConnected}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg 
                       flex items-center justify-center gap-2 transition-colors shadow-md
                       disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Home className="w-5 h-5" />
                  GO HOME ({homePosition.x.toFixed(1)},{" "}
                  {homePosition.y.toFixed(1)})
                </button>

                <button
                  onClick={startAutoTour}
                  disabled={isMoving || !isConnected}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 
                       text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 
                       transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                    />
                  </svg>
                  🤖 AUTO TOUR (12 plante)
                </button>
              </div>

              {/* Rând 2: STOP + EMERGENCY RELEASE */}
              <div className="flex gap-3">
                <button
                  onClick={emergencyStop}
                  disabled={!isConnected}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-6 rounded-lg 
                       flex items-center justify-center gap-2 transition-colors shadow-md
                       disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <AlertTriangle className="w-5 h-5" />
                  STOP
                </button>

                <button
                  onClick={emergencyReleaseAll}
                  disabled={!isConnected}
                  className="flex-1 bg-red-800 hover:bg-red-900 text-white font-bold py-3 px-6 rounded-lg 
                       flex items-center justify-center gap-2 transition-colors shadow-lg border-4 border-red-950
                       disabled:opacity-50 disabled:cursor-not-allowed animate-pulse"
                >
                  <Unlock className="w-6 h-6" />
                  🚨 EMERGENCY RELEASE ALL
                </button>
              </div>
            </div>
          </div>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">
              ℹ️ Informații Sistem
            </h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>
                • <strong>Poziție HOME (0,0):</strong> (
                {homePosition.x.toFixed(2)}cm, {homePosition.y.toFixed(2)}cm)
                absolut
              </li>
              <li>
                • <strong>Grilă plante:</strong> 3 coloane (X: -12, 0, +12) × 4
                rânduri (Y: +18, +9, -9, -18)
              </li>
              <li>
                • <strong>Range mișcare:</strong> X: ±12cm | Y: -18 la +18cm
                față de HOME
              </li>
              <li>
                • <strong>Total poziții:</strong>{" "}
                {PLANT_POSITIONS_RELATIVE.length} plante
              </li>
              <li>• 🏠 = poziție HOME (0,0) | 🌱 = poziție plantă</li>
              <li>• Butonul "GO HOME" te aduce mereu la (0,0)</li>
            </ul>
          </div>
        </>
      )}

      {/* Manual Control Tab */}
      {activeTab === "manual" && <ManualMotorControl />}
    </div>
  );
}
