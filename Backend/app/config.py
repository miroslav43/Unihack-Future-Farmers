from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # PostgreSQL Neon DB
    NEON_DB: str = "postgresql://neondb_owner:npg_0fevq4lyzIwR@ep-dry-math-a480hccz-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Future Farmers API"
    
    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
