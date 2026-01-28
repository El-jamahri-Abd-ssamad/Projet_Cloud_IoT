# Install passlib if not already installed
import subprocess
import sys

try:
    from passlib.context import CryptContext
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'passlib'])
    from passlib.context import CryptContext

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import logging

try:
    from .config import session_factory, DATABASE_URL, DEBUG
except ImportError:
    from helpers.config import session_factory, DATABASE_URL, DEBUG

logger = logging.getLogger(__name__)

# Context pour le hashage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthHelper:
    """Helper pour l'authentification et JWT"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hasher un mot de passe"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Créer un token JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            config.JWT_SECRET_KEY,
            algorithm=config.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Vérifier et décoder un token JWT"""
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            return None
    
    @staticmethod
    def extract_user_id_from_token(token: str) -> Optional[str]:
        """Extraire l'ID utilisateur depuis un token"""
        payload = AuthHelper.verify_token(token)
        if payload and "sub" in payload:
            return payload["sub"]
        return None