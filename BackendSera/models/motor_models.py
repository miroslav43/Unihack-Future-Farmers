"""
Modele Pydantic pentru operațiunile cu motoare
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Union, Optional, Literal
from enum import Enum


class MotorName(str, Enum):
    """Numele motoarele disponibile"""
    ROOF_LEFT = "roof_left"
    ROOF_RIGHT = "roof_right"
    AXIS_X = "axis_x"
    AXIS_Y = "axis_y"


class MotorCommand(BaseModel):
    """Comandă pentru un motor individual"""
    cm: float = Field(..., gt=0, le=1000, description="Distanța în centimetri (0-1000)")
    speed: float = Field(..., gt=0, le=30, description="Viteza în cm/s (1-30)")
    dir: Literal[0, 1] = Field(..., description="Direcție: 1 = înainte, 0 = înapoi")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cm": 10.0,
                "speed": 5.0,
                "dir": 1
            }
        }


class MoveRequest(BaseModel):
    """Request pentru mișcarea unuia sau mai multor motoare"""
    roof_left: Optional[MotorCommand] = None
    roof_right: Optional[MotorCommand] = None
    axis_x: Optional[MotorCommand] = None
    axis_y: Optional[MotorCommand] = None
    
    @field_validator('*')
    @classmethod
    def check_at_least_one_motor(cls, v, info):
        # Aceasta se va executa pentru fiecare câmp
        return v
    
    def model_post_init(self, __context):
        """Validează că cel puțin un motor este specificat"""
        if not any([self.roof_left, self.roof_right, self.axis_x, self.axis_y]):
            raise ValueError("Trebuie specificat cel puțin un motor")
    
    class Config:
        json_schema_extra = {
            "example": {
                "roof_left": {"cm": 20, "speed": 5, "dir": 1},
                "axis_x": {"cm": 10, "speed": 3, "dir": 0}
            }
        }


class StopRequest(BaseModel):
    """Request pentru oprirea motoarelor"""
    motors: Union[Literal["all"], List[MotorName]] = Field(
        ..., 
        description="Lista de motoare de oprit sau 'all' pentru toate"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "motors": ["axis_x", "axis_y"]
            }
        }


class MotorConfigParams(BaseModel):
    """Parametri de configurare pentru un motor"""
    mm_per_rev: Optional[float] = Field(None, gt=0, description="Milimetri per rotație")
    microstep: Optional[int] = Field(None, gt=0, description="Microstep-uri")
    max_speed: Optional[float] = Field(None, gt=0, le=50, description="Viteza maximă în cm/s")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mm_per_rev": 40.0,
                "microstep": 8,
                "max_speed": 30.0
            }
        }


class ConfigRequest(BaseModel):
    """Request pentru configurarea motoarelor"""
    roof_left: Optional[MotorConfigParams] = None
    roof_right: Optional[MotorConfigParams] = None
    axis_x: Optional[MotorConfigParams] = None
    axis_y: Optional[MotorConfigParams] = None


class MotorConfig(BaseModel):
    """Configurația unui motor"""
    mmrev: float = Field(..., description="Milimetri per rotație")
    ms: int = Field(..., description="Microsteps")
    max_cm: float = Field(..., description="Viteza maximă în cm/s")
    steps_mm: float = Field(..., description="Pași per milimetru")


class MotorStatus(BaseModel):
    """Status-ul unui motor"""
    en: bool = Field(..., description="Motor activat (ON/OFF)")
    sp_cm: float = Field(..., description="Viteza curentă în cm/s")
    dir: int = Field(..., description="Direcția: 1 = înainte, 0 = înapoi")
    cm_rem: float = Field(..., description="Centimetri rămași până la target")
    cfg: MotorConfig = Field(..., description="Configurația motorului")


class StatusResponse(BaseModel):
    """Response pentru status-ul tuturor motoarelor"""
    roof_left: MotorStatus
    roof_right: MotorStatus
    axis_x: MotorStatus
    axis_y: MotorStatus


class MoveResponse(BaseModel):
    """Response pentru comanda de mișcare"""
    moved: List[str] = Field(..., description="Lista motoarelor care au fost mișcate")


class StopResponse(BaseModel):
    """Response pentru comanda de stop"""
    stopped: Union[Literal["all"], bool] = Field(..., description="Motoarele oprite")
    ok: Optional[bool] = None


class EmergencyStopResponse(BaseModel):
    """Response pentru emergency stop"""
    emergency_stop: bool = Field(..., description="Emergency stop executat")


class PositionRequest(BaseModel):
    """Request pentru poziționare absolută"""
    target_x: float = Field(..., description="Poziția target pe axa X (orice valoare)")
    target_y: float = Field(..., description="Poziția target pe axa Y (orice valoare)")
    current_x: float = Field(..., description="Poziția curentă pe axa X")
    current_y: float = Field(..., description="Poziția curentă pe axa Y")
    speed: float = Field(8, gt=0, le=30, description="Viteza de deplasare în cm/s")
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_x": 28.125,
                "target_y": 47.5,
                "current_x": 22.5,
                "current_y": 31.5,
                "speed": 8
            }
        }


class PositionResponse(BaseModel):
    """Response pentru poziționare"""
    moved: List[str] = Field(..., description="Lista motoarelor mișcate")
    delta_x: float = Field(..., description="Deplasarea pe axa X")
    delta_y: float = Field(..., description="Deplasarea pe axa Y")
    new_position: Dict[str, float] = Field(..., description="Noua poziție {x, y}")


class HomeRequest(BaseModel):
    """Request pentru întoarcere la centru"""
    current_x: float = Field(..., description="Poziția curentă pe axa X")
    current_y: float = Field(..., description="Poziția curentă pe axa Y")
    speed: float = Field(8, gt=0, le=30, description="Viteza de deplasare în cm/s")
