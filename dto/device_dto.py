from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DeviceType(str, Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

# DTOs pour les requêtes
class DeviceCreateDTO(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=100, description="Unique device identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Device name")
    device_type: DeviceType = Field(..., description="Type of device")
    location: Optional[str] = Field(None, max_length=200)
    firmware_version: Optional[str] = Field("1.0.0", max_length=50)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    owner_id: Optional[str] = Field(None, max_length=100)

class DeviceUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    device_type: Optional[DeviceType] = None
    status: Optional[DeviceStatus] = None
    location: Optional[str] = Field(None, max_length=200)
    firmware_version: Optional[str] = Field(None, max_length=50)
    config: Optional[Dict[str, Any]] = None
    battery_level: Optional[float] = Field(None, ge=0, le=100)
    signal_strength: Optional[float] = Field(None, ge=-100, le=0)
    is_active: Optional[bool] = None
    owner_id: Optional[str] = Field(None, max_length=100)

class DeviceStatusUpdateDTO(BaseModel):
    status: DeviceStatus
    battery_level: Optional[float] = Field(None, ge=0, le=100)
    signal_strength: Optional[float] = Field(None, ge=-100, le=0)

# DTOs pour les réponses
class DeviceResponseDTO(BaseModel):
    id: int
    device_id: str
    name: str
    device_type: str
    status: str
    location: Optional[str]
    firmware_version: str
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    config: Dict[str, Any]
    battery_level: Optional[float]
    signal_strength: Optional[float]
    is_active: bool
    owner_id: Optional[str]
    
    class Config:
        from_attributes = True

class DeviceListDTO(BaseModel):
    devices: list[DeviceResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int

# Filtres
class DeviceFilterDTO(BaseModel):
    search: Optional[str] = None
    device_type: Optional[DeviceType] = None
    status: Optional[DeviceStatus] = None
    is_active: Optional[bool] = None
    owner_id: Optional[str] = None
    min_battery_level: Optional[float] = Field(None, ge=0, le=100)
    max_battery_level: Optional[float] = Field(None, ge=0, le=100)
    