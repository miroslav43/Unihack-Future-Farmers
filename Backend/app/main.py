from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config.settings import settings
from .config.database import db_manager
from .routes import (
    farmer_routes, 
    document_routes, 
    assessment_routes, 
    application_routes,
    order_routes,
    inventory_routes,
    crop_routes,
    task_routes,
    conversational_routes,
    ai_chat_routes,
    harvest_routes
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - COMPLETELY OPEN FOR DEVELOPMENT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(farmers.router, prefix=settings.API_V1_PREFIX)
app.include_router(buyers.router, prefix=settings.API_V1_PREFIX)
app.include_router(inventory.router, prefix=settings.API_V1_PREFIX)
app.include_router(contracts.router, prefix=settings.API_V1_PREFIX)
app.include_router(orders.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Future Farmers API",
        "version": "1.0.0",
        "database": "PostgreSQL (Neon DB)",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "PostgreSQL"}
# Include routers
app.include_router(farmer_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(document_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(assessment_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(application_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(order_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(inventory_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(crop_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(task_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(conversational_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_chat_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(harvest_routes.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
