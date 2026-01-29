import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from helpers.config import JWT_SECRET

logger = logging.getLogger(__name__)

class AuthHelper:
    """Helper pour l'authentification JWT"""
    
    SECRET_KEY = JWT_SECRET
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    @staticmethod
    def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Créer un token JWT"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=AuthHelper.ACCESS_TOKEN_EXPIRE_MINUTES
                )
            
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(
                to_encode,
                AuthHelper.SECRET_KEY,
                algorithm=AuthHelper.ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating token: {e}")
            return None
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Vérifier un token JWT"""
        try:
            payload = jwt.decode(
                token,
                AuthHelper.SECRET_KEY,
                algorithms=[AuthHelper.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Décoder un token JWT sans vérifier la signature"""
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return payload
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return None
