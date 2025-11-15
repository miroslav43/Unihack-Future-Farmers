"""Application settings and configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB Configuration
    MONGO_API_KEY: str
    DATABASE_NAME: str = "farmer_assessment_db"
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Farmer Assessment System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
    ]
    
    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: set = {".pdf", ".jpg", ".jpeg", ".png"}
    
    # AI/OCR Configuration
    TESSERACT_PATH: Optional[str] = None  # Set if custom path needed
    OCR_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Scoring Configuration
    MIN_BONITATE_SCORE: int = 1
    MAX_BONITATE_SCORE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
