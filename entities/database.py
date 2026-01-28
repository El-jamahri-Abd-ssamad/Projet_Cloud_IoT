from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from helpers.config import logger
from helpers.config import DATABASE_URL, DEBUG

# Créer l'engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=DEBUG
)

# Créer la session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Session thread-safe
ScopedSession = scoped_session(SessionLocal)

def get_db():
    """
    Dependency pour obtenir une session DB
    Utilisation: db = get_db()
    """
    db = ScopedSession()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()
        ScopedSession.remove()

def init_db():
    """
    Initialiser la base de données (créer les tables)
    """
    from .device import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")