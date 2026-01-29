import pika
import json
import logging
from helpers.config import RABBITMQ_URL
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class RabbitMQHelper:
    """Helper pour la gestion de RabbitMQ"""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self.exchange_name = "device_events"
        self.queue_name = "device_events_queue"
    
    async def connect(self):
        """Établir une connexion à RabbitMQ"""
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                'rabbitmq',
                5672,
                '/',
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Déclarer l'exchange et la queue
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            logger.info("Connected to RabbitMQ successfully")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def close(self):
        """Fermer la connexion à RabbitMQ"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
    
    async def publish_device_event(
        self,
        event_type: str,
        device_id: str,
        data: Dict[str, Any]
    ):
        """Publier un événement de device"""
        try:
            if not self.channel:
                logger.warning("RabbitMQ channel not initialized")
                return
            
            message = {
                "event_type": event_type,
                "device_id": device_id,
                "data": data
            }
            
            routing_key = f"device.{event_type}"
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Device event published: {event_type} - {device_id}")
        except Exception as e:
            logger.error(f"Failed to publish device event: {e}")
    
    def consume_device_events(self, callback):
        """Consommer les événements de device"""
        try:
            if not self.channel:
                logger.warning("RabbitMQ channel not initialized")
                return
            
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("Started consuming device events")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error consuming device events: {e}")

# Instance globale
rabbitmq_helper = RabbitMQHelper()
