/**
 * Control manual pentru fiecare motor individual
 */
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Gauge,
  Move,
} from "lucide-react";
import { useState } from "react";
import { greenhouseAPI } from "../services/greenhouseAPI";

interface MotorControlProps {
  motorName: string;
  displayName: string;
  icon: React.ReactNode;
  maxCm?: number;
}

function SingleMotorControl({
  motorName,
  displayName,
  icon,
  maxCm = 100,
}: MotorControlProps) {
  const [cm, setCm] = useState(10);
  const [speed, setSpeed] = useState(8);
  const [direction, setDirection] = useState(1);
  const [isMoving, setIsMoving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMove = async () => {
    setIsMoving(true);
    setError(null);

    try {
      const moveData = {
        [motorName]: {
          cm,
          speed,
          dir: direction,
        },
      };

      const response = await fetch("http://localhost:8009/motors/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(moveData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to move motor");
      }

      const result = await response.json();
      console.log(`${motorName} moved:`, result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Eroare la mișcare");
    } finally {
      setIsMoving(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-blue-100 rounded-lg">{icon}</div>
        <h3 className="text-lg font-semibold text-gray-800">{displayName}</h3>
      </div>

      {/* Distanță */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-700">
            Distanță (cm)
          </label>
          <span className="text-lg font-bold text-blue-600">{cm} cm</span>
        </div>
        <input
          type="range"
          min="1"
          max={maxCm}
          value={cm}
          onChange={(e) => setCm(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>1 cm</span>
          <span>{maxCm} cm</span>
        </div>
      </div>

      {/* Viteză */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-700 flex items-center gap-1">
            <Gauge className="w-4 h-4" />
            Viteză (cm/s)
          </label>
          <span className="text-lg font-bold text-green-600">{speed} cm/s</span>
        </div>
        <input
          type="range"
          min="1"
          max="30"
          value={speed}
          onChange={(e) => setSpeed(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>Lent (1)</span>
          <span>Rapid (30)</span>
        </div>
      </div>

      {/* Direcție */}
      <div className="space-y-2 mb-4">
        <label className="text-sm font-medium text-gray-700">Direcție</label>
        <div className="flex gap-2">
          <button
            onClick={() => setDirection(0)}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2
              ${
                direction === 0
                  ? "bg-orange-600 text-white shadow-md scale-105"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
          >
            <ArrowLeft className="w-5 h-5" />
            Înapoi (0)
          </button>
          <button
            onClick={() => setDirection(1)}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2
              ${
                direction === 1
                  ? "bg-blue-600 text-white shadow-md scale-105"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
          >
            Înainte (1)
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Buton Mișcă */}
      <button
        onClick={handleMove}
        disabled={isMoving}
        className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 
                 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-md hover:shadow-lg
                 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isMoving ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            În mișcare...
          </>
        ) : (
          <>
            <Move className="w-5 h-5" />
            Mișcă {displayName}
          </>
        )}
      </button>

      {/* Quick info */}
      <div className="mt-3 text-xs text-gray-500 text-center">
        Va mișca {cm}cm cu {speed}cm/s în direcția{" "}
        {direction === 1 ? "înainte" : "înapoi"}
      </div>
    </div>
  );
}

export function ManualMotorControl() {
  const [isConnected, setIsConnected] = useState(true);

  const emergencyStop = async () => {
    try {
      await greenhouseAPI.emergencyStop();
    } catch (err) {
      console.error("Emergency stop failed:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg p-6 text-white shadow-lg">
        <h2 className="text-2xl font-bold mb-2">🎛️ Control Manual Motoare</h2>
        <p className="text-purple-100">
          Controlează fiecare motor individual - setează distanța, viteza și
          direcția
        </p>
      </div>

      {/* Motors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SingleMotorControl
          motorName="axis_x"
          displayName="Axa X"
          icon={<ArrowRight className="w-6 h-6 text-blue-600" />}
          maxCm={45}
        />

        <SingleMotorControl
          motorName="axis_y"
          displayName="Axa Y"
          icon={<ArrowRight className="w-6 h-6 rotate-90 text-green-600" />}
          maxCm={63}
        />

        <SingleMotorControl
          motorName="roof_left"
          displayName="Acoperiș Stânga"
          icon={<Move className="w-6 h-6 text-orange-600" />}
          maxCm={40}
        />

        <SingleMotorControl
          motorName="roof_right"
          displayName="Acoperiș Dreapta"
          icon={<Move className="w-6 h-6 text-red-600" />}
          maxCm={30}
        />
      </div>

      {/* Emergency Stop */}
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
        <button
          onClick={emergencyStop}
          className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-6 rounded-lg 
                   transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
        >
          <AlertTriangle className="w-6 h-6" />
          🛑 EMERGENCY STOP - Oprește Toate Motoarele
        </button>
      </div>

      {/* Info Panel */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">
          💡 Informații Control Manual
        </h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>
            • <strong>Distanță</strong>: 1-100 cm (limitat la max per motor)
          </li>
          <li>
            • <strong>Viteză</strong>: 1-30 cm/s
          </li>
          <li>
            • <strong>Axa X</strong>: Max 45cm (latura scurtă) |{" "}
            <strong>Axa Y</strong>: Max 63cm (latura lungă)
          </li>
          <li>
            • <strong>Roof Left</strong>: Max 40cm | <strong>Roof Right</strong>
            : Max 30cm
          </li>
          <li>
            • <strong>Direcție 0</strong>: Înapoi | <strong>Direcție 1</strong>:
            Înainte
          </li>
        </ul>
      </div>
    </div>
  );
}
