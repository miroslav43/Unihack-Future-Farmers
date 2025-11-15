/**
 * API Service pentru controlul serei ESP32
 */

const API_BASE_URL = 'http://localhost:8001';

export interface Position {
  x: number;
  y: number;
}

export interface PositionRequest {
  target_x: number;
  target_y: number;
  current_x: number;
  current_y: number;
  speed?: number;
}

export interface PositionResponse {
  moved: string[];
  delta_x: number;
  delta_y: number;
  new_position: {
    x: number;
    y: number;
  };
}

export interface HomeRequest {
  current_x: number;
  current_y: number;
  speed?: number;
}

export interface MotorStatus {
  en: boolean;
  sp_cm: number;
  dir: number;
  cm_rem: number;
  cfg: {
    mmrev: number;
    ms: number;
    max_cm: number;
    steps_mm: number;
  };
}

export interface StatusResponse {
  roof_left: MotorStatus;
  roof_right: MotorStatus;
  axis_x: MotorStatus;
  axis_y: MotorStatus;
}

export const greenhouseAPI = {
  /**
   * Verifică starea conexiunii cu ESP32
   */
  async checkHealth(): Promise<{ status: string; esp32_reachable: boolean; esp32_host: string }> {
    const response = await fetch(`${API_BASE_URL}/motors/health`);
    if (!response.ok) throw new Error('Failed to check health');
    return response.json();
  },

  /**
   * Mișcă către o poziție absolută
   */
  async moveToPosition(request: PositionRequest): Promise<PositionResponse> {
    const response = await fetch(`${API_BASE_URL}/motors/position`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...request,
        speed: request.speed || 8,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to move to position');
    }

    return response.json();
  },

  /**
   * Întoarce la poziția HOME (centru)
   */
  async goHome(request: HomeRequest): Promise<PositionResponse> {
    const response = await fetch(`${API_BASE_URL}/motors/home`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...request,
        speed: request.speed || 8,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to go home');
    }

    return response.json();
  },

  /**
   * Oprește toate motoarele (emergency stop)
   */
  async emergencyStop(): Promise<{ emergency_stop: boolean }> {
    const response = await fetch(`${API_BASE_URL}/motors/emergency-stop`, {
      method: 'POST',
    });

    if (!response.ok) throw new Error('Failed to emergency stop');
    return response.json();
  },

  /**
   * Obține status-ul motoarelor
   */
  async getStatus(): Promise<StatusResponse> {
    const response = await fetch(`${API_BASE_URL}/motors/status`);
    if (!response.ok) throw new Error('Failed to get status');
    return response.json();
  },

  /**
   * Oprește motoarele specificate
   */
  async stopMotors(motors: string[] | 'all'): Promise<{ stopped: string | boolean; ok?: boolean }> {
    const response = await fetch(`${API_BASE_URL}/motors/stop`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ motors }),
    });

    if (!response.ok) throw new Error('Failed to stop motors');
    return response.json();
  },
};
