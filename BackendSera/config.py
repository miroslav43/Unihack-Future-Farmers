"""
Configurări pentru backend-ul de control ESP32
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Configurări ESP32
    ESP32_HOST: str = "esp-multi.local"  # sau IP direct, ex: "192.168.1.100"
    ESP32_PORT: int = 8080
    ESP32_TIMEOUT: int = 10  # secunde
    
    # Configurări API
    API_TITLE: str = "ESP32 Greenhouse Control API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Backend FastAPI pentru controlul serelor cu ESP32"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
