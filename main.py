import uvicorn
from controllers.auth_controller import router
from helpers.config import Base,engine
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from datetime import datetime
from contextlib import asynccontextmanager
from helpers import config
from entities.database import init_db, get_db
from controllers.device_controller import router as device_router
from helpers.rabbitmq_helper import rabbitmq_helper
from helpers.redis_helper import redis_helper

app=FastAPI(
title="Authentication app",
description="Micro service signing app "
)
#create one time - wrap in try/except to handle missing database
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.warning(f"Failed to create database tables: {e}")
    logging.warning("Continuing without database initialization. Make sure your database is running.")

app.include_router(router)


# Configuration du logging
LOG_LEVEL = logging.INFO
LOG_FILE = './logs/app.log'

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
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Connecter à RabbitMQ
    try:
        await rabbitmq_helper.connect()
        logger.info("RabbitMQ connected")
    except Exception as e:
        logger.error(f"RabbitMQ connection failed: {e}")
    
    # Vérifier Redis
    if redis_helper.get_client():
        logger.info("Redis connected")
    else:
        logger.warning("Redis not available, caching disabled")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await rabbitmq_helper.close()
    logger.info("RabbitMQ connection closed")

# Créer l'application FastAPI
APP_NAME = "Authentication API"
APP_VERSION = "1.0.0"

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
async def health_check(db=Depends(get_db)):
    """Endpoint de santé"""
    try:
        # Vérifier la base de données
        db.execute("SELECT 1")
        
        # Vérifier Redis
        redis_healthy = redis_helper.get_client() is not None
        
        return {
            "status": "healthy",
            "service": config.APP_NAME,
            "version": config.APP_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "redis": "connected" if redis_healthy else "disconnected",
            "rabbitmq": "connected"
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
        "message": config.APP_NAME,
        "version": config.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "devices": "/api/v1/devices"
        }
    }

# Inclure les routes
app.include_router(device_router)

# Handler d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc) if True else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True
    
    logger.info(f"Server starting on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )