"""
Serviciu pentru comunicarea cu ESP32
"""
import httpx
import logging
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class ESP32Service:
    """Serviciu pentru comunicarea HTTP cu ESP32"""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Inițializează serviciul ESP32
        
        Args:
            host: Hostname sau IP pentru ESP32 (opțional, se folosește din config)
            port: Port pentru ESP32 (opțional, se folosește din config)
        """
        self.host = host or settings.ESP32_HOST
        self.port = port or settings.ESP32_PORT
        self.base_url = f"http://{self.host}:{self.port}"
        self.timeout = settings.ESP32_TIMEOUT
        
        logger.info(f"ESP32Service inițializat pentru {self.base_url}")
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Face un request HTTP către ESP32
        
        Args:
            method: Metoda HTTP (GET, POST)
            endpoint: Endpoint-ul API (ex: /api/status)
            json_data: Date JSON pentru request (opțional)
            
        Returns:
            Response-ul JSON de la ESP32
            
        Raises:
            httpx.HTTPError: Dacă request-ul eșuează
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"[ESP32] {method} {url}")
                if json_data:
                    logger.debug(f"[ESP32] Request body: {json_data}")
                
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=json_data)
                else:
                    raise ValueError(f"Metodă HTTP nesuportată: {method}")
                
                response.raise_for_status()
                result = response.json()
                logger.debug(f"[ESP32] Response: {result}")
                return result
                
        except httpx.TimeoutException as e:
            logger.error(f"[ESP32] Timeout la conectarea către {url}: {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"[ESP32] Eroare HTTP la {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"[ESP32] Eroare neașteptată: {e}")
            raise
    
    async def move_motors(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trimite comenzi de mișcare către motoare
        
        Args:
            move_data: Dict cu comenzi pentru motoare
                      Ex: {"axis_x": {"cm": 10, "speed": 5, "dir": 1}}
        """
        # MAPARE: Motoarele sunt conectate fizic inversat
        # axis_y în cod → roof_left pe ESP32
        # roof_left în cod → axis_y pe ESP32
        MOTOR_MAPPING = {
            "axis_x": "axis_x",
            "axis_y": "roof_left",      # SWAP: axis_y devine roof_left
            "roof_left": "axis_y",      # SWAP: roof_left devine axis_y
            "roof_right": "roof_right"
        }
        
        # Convertește toate valorile cm și speed la întregi (ESP32 nu acceptă float-uri)
        cleaned_data = {}
        for motor, cmd in move_data.items():
            cm_value = cmd["cm"]
            
            # FIX: roof_left necesită +0.5cm extra pentru sincronizare
            if motor == "roof_left":
                cm_value = cm_value + 0.5
                logger.info(f"[ESP32] roof_left: offset aplicat {cmd['cm']} → {cm_value} cm")
            
            cm_value = int(round(cm_value))
            
            # Validare: nu trimite 0, minim 1cm
            if cm_value < 1:
                logger.warning(f"[ESP32] Skip {motor}: cm prea mic ({cm_value})")
                continue
            
            # Aplică maparea pentru motorul fizic
            physical_motor = MOTOR_MAPPING.get(motor, motor)
            
            # FIX: roof_left are direcția inversată fizic
            # dir: 1 = deschide, 0 = închide (logic)
            # Pentru roof_left: 1 logic → 0 fizic, 0 logic → 1 fizic
            direction = cmd["dir"]
            if motor == "roof_left":
                direction = 1 if cmd["dir"] == 0 else 0
                logger.info(f"[ESP32] roof_left: inversare direcție {cmd['dir']} → {direction}")
            
            cleaned_data[physical_motor] = {
                "cm": cm_value,
                "speed": int(cmd["speed"]),
                "dir": direction
            }
        
        if not cleaned_data:
            logger.warning("[ESP32] No valid motors to move")
            return {"moved": []}
        
        logger.info(f"[ESP32] POST {self.base_url}/api/move - data: {cleaned_data}")
        
        return await self._make_request("POST", "/api/move", cleaned_data)
    
    async def stop_motors(self, stop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Oprește motoarele specificate (dar le lasă "tare" - HOLD)
        
        IMPORTANT: NU aplicăm mapare pentru stop - trimitem direct numele motorului fizic
        
        Args:
            stop_data: Date de stop în format JSON
            
        Returns:
            Response de la ESP32
        """
        # NU aplicăm MOTOR_MAPPING pentru stop - trimitem direct
        return await self._make_request("POST", "/api/stop", stop_data)
    
    async def release_motors(self, release_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Relaxează motoarele specificate ("moale" - permite ajustare manuală)
        
        IMPORTANT: NU aplicăm mapare pentru release - trimitem direct numele motorului fizic
        
        Args:
            release_data: Date de release în format JSON
            
        Returns:
            Response de la ESP32
        """
        # NU aplicăm MOTOR_MAPPING pentru release - trimitem direct
        return await self._make_request("POST", "/api/release", release_data)
    
    async def emergency_stop(self) -> Dict[str, Any]:
        """
        Execută emergency stop pentru toate motoarele
        
        Returns:
            Response de la ESP32
        """
        return await self._make_request("POST", "/api/emergency_stop")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Obține status-ul tuturor motoarelor
        
        Returns:
            Status-ul motoarelor de la ESP32
        """
        return await self._make_request("GET", "/api/status")
    
    async def configure_motors(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configurează parametrii motoarelor
        
        Args:
            config_data: Date de configurare în format JSON
            
        Returns:
            Response de la ESP32 (status actualizat)
        """
        return await self._make_request("POST", "/api/config", config_data)
    
    async def check_connection(self) -> bool:
        """
        Verifică dacă ESP32 este accesibil
        
        Returns:
            True dacă ESP32 răspunde, False altfel
        """
        try:
            await self.get_status()
            logger.info("[ESP32] Conexiune OK")
            return True
        except Exception as e:
            logger.warning(f"[ESP32] Conexiune eșuată: {e}")
            return False
