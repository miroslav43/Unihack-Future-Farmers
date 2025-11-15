"""
Rute API pentru controlul ESP32
"""
from .motor_routes import router as motor_router

__all__ = ["motor_router"]
