import os
import subprocess
import sys

try:
    import redis
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'redis'])
    import redis

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
try:
    from .config import session_factory, DATABASE_URL, DEBUG
except ImportError:
    from helpers.config import session_factory, DATABASE_URL, DEBUG
import logging

logger = logging.getLogger(__name__)

class RedisHelper:
    """Helper pour les opérations Redis"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisHelper, cls).__new__(cls)
            cls._instance._init_redis()
        return cls._instance
    
    def _init_redis(self):
        """Initialiser la connexion Redis"""
        try:
            self._client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                password=os.getenv('REDIS_PASSWORD'),
                db=int(os.getenv('REDIS_DB', '0')),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Tester la connexion
            self._client.ping()
            logger.info("Connected to Redis successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None
    
    def get_client(self):
        """Obtenir le client Redis"""
        if self._client is None:
            self._init_redis()
        return self._client
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Stocker une valeur dans Redis"""
        try:
            client = self.get_client()
            if client is None:
                return False
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if ttl:
                client.setex(key, ttl, value)
            else:
                client.set(key, value)
            
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def get(self, key: str, default: Any = None):
        """Récupérer une valeur depuis Redis"""
        try:
            client = self.get_client()
            if client is None:
                return default
            
            value = client.get(key)
            if value is None:
                return default
            
            # Essayer de parser comme JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return default
    
    def delete(self, key: str):
        """Supprimer une clé Redis"""
        try:
            client = self.get_client()
            if client:
                client.delete(key)
                return True
            return False
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Vérifier si une clé existe"""
        try:
            client = self.get_client()
            if client:
                return client.exists(key) > 0
            return False
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def cache_device(self, device_id: str, device_data: dict, ttl: int = 300):
        """Mettre en cache les données d'un device"""
        cache_key = f"device:{device_id}"
        return self.set(cache_key, device_data, ttl)
    
    def get_cached_device(self, device_id: str) -> Optional[dict]:
        """Récupérer un device du cache"""
        cache_key = f"device:{device_id}"
        return self.get(cache_key)
    
    def invalidate_device_cache(self, device_id: str):
        """Invalider le cache d'un device"""
        cache_key = f"device:{device_id}"
        self.delete(cache_key)

# Instance globale
redis_helper = RedisHelper()