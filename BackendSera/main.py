"""
Backend FastAPI pentru controlul ESP32 - Sisteme de Seră
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from config import settings
from routes import motor_router

# Configurare logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events pentru aplicație"""
    # Startup
    logger.info("🚀 Backend FastAPI pornit")
    logger.info(f"📡 ESP32 Target: {settings.ESP32_HOST}:{settings.ESP32_PORT}")
    yield
    # Shutdown
    logger.info("👋 Backend FastAPI oprit")


# Creare aplicație FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

# Configurare CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Includere rute
app.include_router(motor_router)


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint root - informații despre API
    """
    return {
        "message": "ESP32 Greenhouse Control API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "esp32_target": f"{settings.ESP32_HOST}:{settings.ESP32_PORT}"
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Health check pentru API
    """
    return {
        "status": "healthy",
        "service": "greenhouse-control-api"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8009,  # Port unic pentru BackendSera (Backend principal e pe 8000)
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
