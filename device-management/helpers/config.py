import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/device_management"
)

# Configuration Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Configuration RabbitMQ
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

# Configuration Application
APP_NAME = os.getenv("APP_NAME", "Device Management API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")

# Configuration du logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "./logs/device-management.log")

# Configuration des paramètres par défaut
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
DEFAULT_SORT_BY = "created_at"
DEFAULT_SORT_ORDER = "desc"

# Timeouts
DEVICE_HEARTBEAT_TIMEOUT = int(os.getenv("DEVICE_HEARTBEAT_TIMEOUT", "300"))  # 5 minutes
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 heure

# Initialiser SQLAlchemy de manière tardive pour éviter les problèmes de compatibilité Python 3.14
_engine = None
_SessionLocal = None
_Base = None

def get_engine():
    """Obtenir le moteur SQLAlchemy de manière tardive"""
    global _engine
    if _engine is None:
        try:
            from sqlalchemy import create_engine
            import sys
            
            # Désactiver l'avertissement TypeOnly pour Python 3.14
            if sys.version_info >= (3, 14):
                import warnings
                warnings.filterwarnings('ignore', category=DeprecationWarning)
            
            _engine = create_engine(
                DATABASE_URL,
                pool_size=20,
                max_overflow=40,
                echo=DEBUG,
                future=True
            )
        except Exception as e:
            print(f"❌ Erreur création engine: {e}")
            raise
    return _engine

def get_sessionlocal():
    """Obtenir la session locale de manière tardive"""
    global _SessionLocal
    if _SessionLocal is None:
        try:
            from sqlalchemy.orm import sessionmaker
            engine = get_engine()
            _SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine,
                expire_on_commit=False
            )
        except Exception as e:
            print(f"❌ Erreur création SessionLocal: {e}")
            raise
    return _SessionLocal

def get_base():
    """Obtenir la base déclarative de manière tardive"""
    global _Base
    if _Base is None:
        try:
            from sqlalchemy.ext.declarative import declarative_base
            _Base = declarative_base()
        except Exception as e:
            print(f"❌ Erreur création Base: {e}")
            raise
    return _Base

# Accesseurs pour compatibilité
class _EngineProperty:
    def __get__(self, obj, objtype=None):
        return get_engine()

class _SessionLocalProperty:
    def __get__(self, obj, objtype=None):
        return get_sessionlocal()

class _BaseProperty:
    def __get__(self, obj, objtype=None):
        return get_base()

# Export les accesseurs
engine = _EngineProperty()
SessionLocal = _SessionLocalProperty()
Base = _BaseProperty()
