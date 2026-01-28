from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    device_type = Column(String(50), nullable=False)  # sensor, actuator, gateway
    status = Column(String(20), default="offline")  # online, offline, error, maintenance
    location = Column(String(200))
    firmware_version = Column(String(50), default="1.0.0")
    last_seen = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Configuration
    config = Column(Text, default="{}")
    
    # Métriques
    battery_level = Column(Float, nullable=True)
    signal_strength = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Propriétaire (pour multi-tenant)
    owner_id = Column(String(100), nullable=True)
    
    def get_config_dict(self):
        """Retourne la configuration sous forme de dictionnaire"""
        try:
            return json.loads(self.config) if self.config else {}
        except json.JSONDecodeError:
            return {}
    
    def set_config_dict(self, config_dict):
        """Définit la configuration à partir d'un dictionnaire"""
        self.config = json.dumps(config_dict) if config_dict else "{}"
    
    def to_dict(self):
        """Convertit l'entité en dictionnaire"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "status": self.status,
            "location": self.location,
            "firmware_version": self.firmware_version,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "config": self.get_config_dict(),
            "battery_level": self.battery_level,
            "signal_strength": self.signal_strength,
            "is_active": self.is_active,
            "owner_id": self.owner_id
        }