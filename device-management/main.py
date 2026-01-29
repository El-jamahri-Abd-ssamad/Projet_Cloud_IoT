import uvicorn
import logging
import sys
import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import tardif de SQLAlchemy pour éviter les problèmes de compatibilité
def get_config():
    try:
        from helpers.config import Base, engine, APP_NAME, APP_VERSION, LOG_LEVEL, LOG_FILE
        return Base, engine, APP_NAME, APP_VERSION, LOG_LEVEL, LOG_FILE
    except Exception as e:
        print(f"Warning: Could not import config: {e}")
        return None, None, "Device Management API", "1.0.0", "INFO", "./logs/app.log"

Base, engine, APP_NAME, APP_VERSION, LOG_LEVEL, LOG_FILE = get_config()

# Configuration du logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    # Initialiser la base de données
    try:
        from entities.database import init_db
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    
    # Connecter à RabbitMQ (optionnel)
    try:
        from helpers.rabbitmq_helper import rabbitmq_helper
        await rabbitmq_helper.connect()
        logger.info("RabbitMQ connected")
    except Exception as e:
        logger.warning(f"RabbitMQ connection failed (optional): {e}")
    
    # Vérifier Redis (optionnel)
    try:
        from helpers.redis_helper import redis_helper
        if redis_helper.connect():
            logger.info("Redis connected")
        else:
            logger.warning("Redis not available, caching disabled")
    except Exception as e:
        logger.warning(f"Redis connection failed (optional): {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    try:
        from helpers.rabbitmq_helper import rabbitmq_helper
        await rabbitmq_helper.close()
    except:
        pass
    
    try:
        from helpers.redis_helper import redis_helper
        redis_helper.close()
    except:
        pass
    
    logger.info("Application shutdown complete")

# Créer l'application FastAPI
app = FastAPI(
    title=APP_NAME,
    description="Microservice for managing IoT devices",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    
    # Exécuter la requête
    response = await call_next(request)
    
    # Calculer le temps d'exécution
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    # Logger
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}ms"
    )
    
    return response

# Route de santé
@app.get("/health")
async def health_check():
    """Endpoint de santé"""
    try:
        return {
            "status": "healthy",
            "service": APP_NAME,
            "version": APP_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Service is running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Route racine
@app.get("/")
async def root():
    return {
        "message": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "devices": "/api/v1/devices"
        }
    }

# Inclure les routes des devices (optionnel si la DB n'est pas disponible)
try:
    from controller.device_manager_controller import router as device_router
    app.include_router(device_router)
    logger.info("Device routes included")
except Exception as e:
    logger.warning(f"Could not include device routes: {e}")

# Handler d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Server starting on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info"
    )