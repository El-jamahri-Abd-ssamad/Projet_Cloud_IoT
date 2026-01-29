from sqlalchemy.orm import Session
from helpers.config import engine, SessionLocal, Base
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Initialiser la base de données"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_db():
    """Dépendance pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def close_db():
    """Fermer la connexion à la base de données"""
    try:
        engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Failed to close database connection: {e}")
