"""Main FastAPI application"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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
    """Application lifespan events"""
    # Startup
    logger.info("Starting application...")
    try:
        await db_manager.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await db_manager.disconnect()
    logger.info("Database disconnected")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/api/docs",
        "health": "/health"
    }


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
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
