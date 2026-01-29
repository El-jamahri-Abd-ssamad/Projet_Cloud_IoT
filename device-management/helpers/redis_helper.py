import redis
import json
import logging
from helpers.config import REDIS_URL, CACHE_TTL
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class RedisHelper:
    """Helper pour la gestion de Redis"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.ttl = CACHE_TTL
    
    def connect(self):
        """Établir une connexion à Redis"""
        try:
            self.client = redis.from_url(REDIS_URL, decode_responses=True)
            self.client.ping()
            logger.info("Connected to Redis successfully")
            return self.client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None
    
    def get_client(self) -> Optional[redis.Redis]:
        """Obtenir le client Redis"""
        if not self.client:
            self.connect()
        return self.client
    
    def close(self):
        """Fermer la connexion à Redis"""
        try:
            if self.client:
                self.client.close()
                logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    
    def cache_device(self, device_id: str, device_data: Dict[str, Any]) -> bool:
        """Mettre en cache les données d'un device"""
        try:
            client = self.get_client()
            if not client:
                return False
            
            key = f"device:{device_id}"
            client.setex(
                key,
                self.ttl,
                json.dumps(device_data)
            )
            return True
        except Exception as e:
            logger.error(f"Error caching device {device_id}: {e}")
            return False
    
    def get_cached_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer un device du cache"""
        try:
            client = self.get_client()
            if not client:
                return None
            
            key = f"device:{device_id}"
            data = client.get(key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached device {device_id}: {e}")
            return None
    
    def invalidate_device_cache(self, device_id: str) -> bool:
        """Invalider le cache d'un device"""
        try:
            client = self.get_client()
            if not client:
                return False
            
            key = f"device:{device_id}"
            client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache for device {device_id}: {e}")
            return False
    
    def cache_device_list(self, cache_key: str, devices_data: list, ttl: int = None) -> bool:
        """Mettre en cache une liste de devices"""
        try:
            client = self.get_client()
            if not client:
                return False
            
            ttl = ttl or self.ttl
            client.setex(
                cache_key,
                ttl,
                json.dumps(devices_data)
            )
            return True
        except Exception as e:
            logger.error(f"Error caching device list: {e}")
            return False
    
    def get_cached_device_list(self, cache_key: str) -> Optional[list]:
        """Récupérer une liste de devices du cache"""
        try:
            client = self.get_client()
            if not client:
                return None
            
            data = client.get(cache_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached device list: {e}")
            return None

# Instance globale
redis_helper = RedisHelper()
