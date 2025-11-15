/**
 * Componenta de control pentru sera cu grilă 4x3
 * Dimensiuni seră: 45cm (lățime) x 33cm (înălțime)
 */
import {
  AlertTriangle,
  Grid3x3,
  Home,
  Loader2,
  Settings,
  Square,
} from "lucide-react";
import { useEffect, useState } from "react";
import { greenhouseAPI, Position } from "../services/greenhouseAPI";
import { ManualMotorControl } from "./ManualMotorControl";

// Constante pentru seră
const GREENHOUSE_WIDTH = 45; // cm
const GREENHOUSE_HEIGHT = 33; // cm
const GRID_COLS = 4;
const GRID_ROWS = 3;
const HOME_POSITION: Position = { x: 22.5, y: 16.5 }; // Centrul serei

// Calculează poziția pentru fiecare buton în grilă
const calculateGridPositions = (): Position[] => {
  const positions: Position[] = [];
  const colWidth = GREENHOUSE_WIDTH / GRID_COLS;
  const rowHeight = GREENHOUSE_HEIGHT / GRID_ROWS;

  for (let row = 0; row < GRID_ROWS; row++) {
    for (let col = 0; col < GRID_COLS; col++) {
      positions.push({
        x: (col + 0.5) * colWidth,
        y: (row + 0.5) * rowHeight,
      });
    }
  }

  return positions;
};

const GRID_POSITIONS = calculateGridPositions();

export function GreenhouseControl() {
  const [activeTab, setActiveTab] = useState<"grid" | "manual">("grid");
  const [currentPosition, setCurrentPosition] =
    useState<Position>(HOME_POSITION);
  const [isMoving, setIsMoving] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPosition, setSelectedPosition] = useState<number | null>(null);

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

    const targetPos = GRID_POSITIONS[positionIndex];

    setIsMoving(true);
    setError(null);

    try {
      const response = await greenhouseAPI.moveToPosition({
        target_x: targetPos.x,
        target_y: targetPos.y,
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
      const response = await greenhouseAPI.goHome({
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

  const emergencyStop = async () => {
    try {
      await greenhouseAPI.emergencyStop();
      setIsMoving(false);
      setError(null);
    } catch (err) {
      setError("Eroare la emergency stop");
    }
  };

  // Găsește poziția curentă cea mai apropiată (pentru highlight)
  const findClosestPosition = (): number | null => {
    let closestIndex = 0;
    let minDistance = Infinity;

    GRID_POSITIONS.forEach((pos, index) => {
      const distance = Math.sqrt(
        Math.pow(pos.x - currentPosition.x, 2) +
          Math.pow(pos.y - currentPosition.y, 2)
      );
      if (distance < minDistance) {
        minDistance = distance;
        closestIndex = index;
      }
    });

    return minDistance < 2 ? closestIndex : null; // Toleranță 2cm
  };

  const closestPosition = findClosestPosition();

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
                ? "Grilă 4x3 - Poziționare precisă"
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
          Grilă 4x3
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
            Poziție Curentă
          </h3>
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">X:</span>
              <span className="font-mono font-bold text-lg">
                {currentPosition.x.toFixed(2)} cm
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Y:</span>
              <span className="font-mono font-bold text-lg">
                {currentPosition.y.toFixed(2)} cm
              </span>
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
          {/* Grid Control */}
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Grilă Poziții (4x3)</h2>

            <div className="grid grid-cols-4 gap-3 mb-6">
              {GRID_POSITIONS.map((pos, index) => {
                const isActive = closestPosition === index;
                const isSelected = selectedPosition === index;
                const buttonNum = index + 1;

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
                    <div className="text-2xl font-bold mb-1">{buttonNum}</div>
                    <div className="text-xs opacity-80">
                      ({pos.x.toFixed(1)}, {pos.y.toFixed(1)})
                    </div>
                    {isActive && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full animate-pulse" />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Control Buttons */}
            <div className="flex gap-3">
              <button
                onClick={goHome}
                disabled={isMoving || !isConnected}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg 
                     flex items-center justify-center gap-2 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Home className="w-5 h-5" />
                HOME (Centru)
              </button>

              <button
                onClick={emergencyStop}
                disabled={!isConnected}
                className="bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-6 rounded-lg 
                     flex items-center justify-center gap-2 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <AlertTriangle className="w-5 h-5" />
                STOP
              </button>
            </div>
          </div>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">ℹ️ Informații</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>
                • Dimensiuni seră: {GREENHOUSE_WIDTH}cm x {GREENHOUSE_HEIGHT}cm
              </li>
              <li>
                • Grilă: {GRID_COLS} coloane x {GRID_ROWS} rânduri = 12 poziții
              </li>
              <li>
                • Poziția HOME (centru): ({HOME_POSITION.x}cm, {HOME_POSITION.y}
                cm)
              </li>
              <li>• Click pe un număr pentru a mișca la poziția respectivă</li>
            </ul>
          </div>
        </>
      )}

      {/* Manual Control Tab */}
      {activeTab === "manual" && <ManualMotorControl />}
    </div>
  );
}
