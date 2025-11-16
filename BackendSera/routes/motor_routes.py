"""
Rute API pentru controlul motoarelor ESP32
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import logging

from models import (
    MoveRequest,
    StopRequest,
    ConfigRequest,
    StatusResponse,
    MoveResponse,
    StopResponse,
    EmergencyStopResponse,
    PositionRequest,
    PositionResponse,
    HomeRequest
)
from services import ESP32Service
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/motors", tags=["Motors"])


def get_esp32_service() -> ESP32Service:
    """Dependency pentru a obține instanța ESP32Service"""
    return ESP32Service()


@router.post("/move", response_model=MoveResponse, status_code=status.HTTP_200_OK)
async def move_motors(
    request: MoveRequest,
    esp32: ESP32Service = Depends(get_esp32_service)
) -> MoveResponse:
    """
    Mișcă unul sau mai multe motoare
    
    - **roof_left**: Comandă pentru motorul roof_left (opțional)
    - **roof_right**: Comandă pentru motorul roof_right (opțional)
    - **axis_x**: Comandă pentru motorul axis_x (opțional)
    - **axis_y**: Comandă pentru motorul axis_y (opțional)
    
    Fiecare comandă trebuie să conțină:
    - **cm**: Distanța în centimetri (0-1000)
    - **speed**: Viteza în cm/s (1-30)
    - **dir**: Direcția (1 = înainte, 0 = înapoi)
    """
    try:
        # Convertește request-ul Pydantic în dict, exclud valorile None
        move_data = request.model_dump(exclude_none=True)
        
        logger.info(f"[API] Move motors request: {move_data}")
        
        # Trimite comanda către ESP32
        response = await esp32.move_motors(move_data)
        
        return MoveResponse(**response)
        
    except Exception as e:
        logger.error(f"[API] Eroare la mișcarea motoarelor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la comunicarea cu ESP32: {str(e)}"
        )


@router.post("/stop", response_model=StopResponse, status_code=status.HTTP_200_OK)
async def stop_motors(
    request: StopRequest,
    esp32: ESP32Service = Depends(get_esp32_service)
) -> StopResponse:
    """
    Oprește motoarele specificate
    
    - **motors**: Lista de motoare de oprit sau "all" pentru toate
    
    Motoare disponibile: roof_left, roof_right, axis_x, axis_y
    """
    try:
        stop_data = request.model_dump()
        
        logger.info(f"[API] Stop motors request: {stop_data}")
        
        # Trimite comanda către ESP32
        response = await esp32.stop_motors(stop_data)
        
        return StopResponse(**response)
        
    except Exception as e:
        logger.error(f"[API] Eroare la oprirea motoarelor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la comunicarea cu ESP32: {str(e)}"
        )


@router.post("/emergency-stop", response_model=EmergencyStopResponse, status_code=status.HTTP_200_OK)
async def emergency_stop(
    esp32: ESP32Service = Depends(get_esp32_service)
) -> EmergencyStopResponse:
    """
    STOP DE URGENȚĂ - oprește toate motoarele imediat
    
    Această comandă oprește toate motoarele fără excepție.
    """
    try:
        logger.warning("[API] EMERGENCY STOP activat!")
        
        # Trimite comanda către ESP32
        response = await esp32.emergency_stop()
        
        return EmergencyStopResponse(**response)
        
    except Exception as e:
        logger.error(f"[API] Eroare la emergency stop: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la comunicarea cu ESP32: {str(e)}"
        )


@router.get("/status", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def get_status(
    esp32: ESP32Service = Depends(get_esp32_service)
) -> StatusResponse:
    """
    Obține status-ul curent al tuturor motoarelor
    
    Returnează:
    - **en**: Motor activat (true/false)
    - **sp_cm**: Viteza curentă în cm/s
    - **dir**: Direcția (1 = înainte, 0 = înapoi)
    - **cm_rem**: Centimetri rămași până la target
    - **cfg**: Configurația motorului (mmrev, microsteps, viteza max, steps/mm)
    """
    try:
        logger.info("[API] Cerere status motoare")
        
        # Obține status de la ESP32
        response = await esp32.get_status()
        
        return StatusResponse(**response)
        
    except Exception as e:
        logger.error(f"[API] Eroare la obținerea status-ului: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la comunicarea cu ESP32: {str(e)}"
        )


@router.post("/config", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def configure_motors(
    request: ConfigRequest,
    esp32: ESP32Service = Depends(get_esp32_service)
) -> StatusResponse:
    """
    Configurează parametrii motoarelor
    
    Pentru fiecare motor poți configura:
    - **mm_per_rev**: Milimetri per rotație
    - **microstep**: Numărul de microsteps
    - **max_speed**: Viteza maximă în cm/s
    
    Returnează status-ul actualizat al motoarelor.
    """
    try:
        config_data = request.model_dump(exclude_none=True)
        
        logger.info(f"[API] Configurare motoare: {config_data}")
        
        # Trimite configurația către ESP32
        response = await esp32.configure_motors(config_data)
        
        return StatusResponse(**response)
        
    except Exception as e:
        logger.error(f"[API] Eroare la configurarea motoarelor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la comunicarea cu ESP32: {str(e)}"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(
    esp32: ESP32Service = Depends(get_esp32_service)
) -> Dict[str, Any]:
    """
    Verifică starea conexiunii cu ESP32
    
    Returnează:
    - **status**: "ok" dacă ESP32 răspunde, "error" altfel
    - **esp32_host**: Hostname-ul ESP32
    - **esp32_reachable**: True dacă ESP32 este accesibil
    """
    is_reachable = await esp32.check_connection()
    
    return {
        "status": "ok" if is_reachable else "error",
        "esp32_host": f"{esp32.host}:{esp32.port}",
        "esp32_reachable": is_reachable
    }


@router.post("/position", response_model=PositionResponse, status_code=status.HTTP_200_OK)
async def move_to_position(
    request: PositionRequest,
    esp32: ESP32Service = Depends(get_esp32_service)
) -> PositionResponse:
    """
    Mișcă către o poziție absolută în seră
    
    Calculează diferența dintre poziția curentă și target și trimite comenzi către motoare.
    
    - **target_x**: Poziția țintă pe axa X (0-45cm) - latura scurtă
    - **target_y**: Poziția țintă pe axa Y (0-63cm) - latura lungă
    - **current_x**: Poziția curentă pe axa X
    - **current_y**: Poziția curentă pe axa Y
    - **speed**: Viteza de deplasare (cm/s)
    """
    try:
        # Calculează delta-urile
        delta_x = request.target_x - request.current_x
        delta_y = request.target_y - request.current_y
        
        logger.info(f"[API] Move to position: target=({request.target_x}, {request.target_y}), "
                   f"current=({request.current_x}, {request.current_y}), "
                   f"delta=({delta_x:.2f}, {delta_y:.2f})")
        
        # Determină direcțiile
        dir_x = 1 if delta_x >= 0 else 0
        dir_y = 1 if delta_y >= 0 else 0
        
        # Valori absolute
        abs_delta_x = abs(delta_x)
        abs_delta_y = abs(delta_y)
        
        moved = []
        
        # Construiește comanda de mișcare
        move_data = {}
        
        if abs_delta_x > 0.1:  # Toleranță de 1mm
            move_data["axis_x"] = {
                "cm": abs_delta_x,
                "speed": request.speed,
                "dir": dir_x
            }
            moved.append("axis_x")
        
        if abs_delta_y > 0.1:  # Toleranță de 1mm
            move_data["axis_y"] = {
                "cm": abs_delta_y,
                "speed": request.speed,
                "dir": dir_y
            }
            moved.append("axis_y")
        
        # Trimite comanda dacă există ceva de mișcat
        if move_data:
            await esp32.move_motors(move_data)
            logger.info(f"[API] Motors moved: {moved}")
        else:
            logger.info("[API] Already at target position")
        
        return PositionResponse(
            moved=moved,
            delta_x=delta_x,
            delta_y=delta_y,
            new_position={"x": request.target_x, "y": request.target_y}
        )
        
    except Exception as e:
        logger.error(f"[API] Eroare la poziționare: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la comunicarea cu ESP32: {str(e)}"
        )


@router.post("/release", status_code=status.HTTP_200_OK)
async def release_motors(
    request: StopRequest,
    esp32: ESP32Service = Depends(get_esp32_service)
) -> Dict[str, Any]:
    """
    RELEASE motoarele - relaxează (moale) pentru ajustare manuală
    
    Diferă de /stop care oprește dar lasă motoarele "tare" (hold).
    Release face motoarele "moale" și permite ajustare manuală.
    
    - **motors**: Lista de motoare de release sau "all" pentru toate
    
    Motoare disponibile: roof_left, roof_right, axis_x, axis_y
    """
    try:
        release_data = request.model_dump()
        
        logger.info(f"[API] Release motors request: {release_data}")
        
        # Trimite comanda către ESP32
        response = await esp32.release_motors(release_data)
        
        return response
        
    except Exception as e:
        logger.error(f"[API] Eroare la release motoare: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la comunicarea cu ESP32: {str(e)}"
        )


@router.post("/home", response_model=PositionResponse, status_code=status.HTTP_200_OK)
async def go_home(
    request: HomeRequest,
    esp32: ESP32Service = Depends(get_esp32_service)
) -> PositionResponse:
    """
    Întoarce la poziția HOME (centru) - (22.5cm, 16.5cm)
    
    - **current_x**: Poziția curentă pe axa X
    - **current_y**: Poziția curentă pe axa Y
    - **speed**: Viteza de deplasare (cm/s)
    """
    try:
        # Poziția HOME = centrul serei
        HOME_X = 22.5  # cm (45/2) - latura scurtă
        HOME_Y = 31.5  # cm (63/2) - latura lungă
        
        logger.info(f"[API] Go HOME from ({request.current_x}, {request.current_y})")
        
        # Folosim endpoint-ul de poziționare
        position_request = PositionRequest(
            target_x=HOME_X,
            target_y=HOME_Y,
            current_x=request.current_x,
            current_y=request.current_y,
            speed=request.speed
        )
        
        return await move_to_position(position_request, esp32)
        
    except Exception as e:
        logger.error(f"[API] Eroare la HOME: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la comunicarea cu ESP32: {str(e)}"
        )
