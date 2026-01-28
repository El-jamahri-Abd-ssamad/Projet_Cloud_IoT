import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import os
import subprocess
import sys

try:
    from .config import session_factory, DATABASE_URL, DEBUG
except ImportError:
    from helpers.config import session_factory, DATABASE_URL, DEBUG

# Install aio_pika if not already installed
try:
    import aio_pika
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'aio_pika'])
    import aio_pika

logger = logging.getLogger(__name__)

class RabbitMQHelper:
    """Helper pour la communication avec RabbitMQ"""
    
    _instance = None
    _connection = None
    _channel = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RabbitMQHelper, cls).__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Établir la connexion à RabbitMQ"""
        if self._connection is None or self._connection.is_closed:
            try:
                rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
                rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
                rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
                rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
                
                self._connection = await aio_pika.connect_robust(
                    host=rabbitmq_host,
                    port=rabbitmq_port,
                    login=rabbitmq_user,
                    password=rabbitmq_password,
                    heartbeat=600
                )
                self._channel = await self._connection.channel()
                
                # Déclarer l'exchange pour les événements de device
                await self._channel.declare_exchange(
                    "device_events",
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )
                
                # Déclarer l'exchange pour les logs
                await self._channel.declare_exchange(
                    "application_logs",
                    aio_pika.ExchangeType.FANOUT,
                    durable=True
                )
                
                logger.info("Connected to RabbitMQ successfully")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
    
    async def publish_device_event(
        self,
        event_type: str,
        device_id: str,
        data: Dict[str, Any],
        routing_key: Optional[str] = None
    ):
        """Publier un événement de device"""
        if self._channel is None:
            await self.connect()
        
        message_body = {
            "event_type": event_type,
            "device_id": device_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "device-management"
        }
        
        message = aio_pika.Message(
            body=json.dumps(message_body).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        if routing_key is None:
            routing_key = f"device.{event_type}.{device_id}"
        
        try:
            await self._channel.default_exchange.publish(
                message,
                routing_key=routing_key
            )
            logger.debug(f"Event published: {routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    async def publish_log(self, log_data: Dict[str, Any]):
        """Publier un log dans l'exchange de logs"""
        if self._channel is None:
            await self.connect()
        
        message_body = {
            **log_data,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "device-management"
        }
        
        message = aio_pika.Message(
            body=json.dumps(message_body).encode(),
            content_type="application/json"
        )
        
        try:
            await self._channel.default_exchange.publish(
                message,
                routing_key="log"
            )
        except Exception as e:
            logger.error(f"Failed to publish log: {e}")
    
    async def close(self):
        """Fermer la connexion RabbitMQ"""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ connection closed")

# Instance globale
rabbitmq_helper = RabbitMQHelper()