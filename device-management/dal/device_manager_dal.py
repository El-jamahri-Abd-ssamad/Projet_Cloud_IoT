from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from typing import List, Optional, Tuple
from datetime import datetime
import json

from entities.device_manager_entity import Device
from dto.device_manager_dto import DeviceFilterDTO

class DeviceDAL:
    """Data Access Layer pour les devices"""
    
    @staticmethod
    def create_device(db: Session, device_data: dict) -> Device:
        device = Device(**device_data)
        db.add(device)
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def get_device_by_id(db: Session, device_id: str) -> Optional[Device]:
        return db.query(Device).filter(Device.device_id == device_id).first()
    
    @staticmethod
    def get_device_by_db_id(db: Session, id: int) -> Optional[Device]:
        return db.query(Device).filter(Device.id == id).first()
    
    @staticmethod
    def get_devices(
        db: Session,
        filter_dto: DeviceFilterDTO,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Device], int]:
        query = db.query(Device)
        
        # Appliquer les filtres
        if filter_dto.search:
            search = f"%{filter_dto.search}%"
            query = query.filter(
                or_(
                    Device.name.ilike(search),
                    Device.device_id.ilike(search),
                    Device.location.ilike(search)
                )
            )
        
        if filter_dto.device_type:
            query = query.filter(Device.device_type == filter_dto.device_type)
        
        if filter_dto.status:
            query = query.filter(Device.status == filter_dto.status)
        
        if filter_dto.is_active is not None:
            query = query.filter(Device.is_active == filter_dto.is_active)
        
        if filter_dto.owner_id:
            query = query.filter(Device.owner_id == filter_dto.owner_id)
        
        if filter_dto.min_battery_level is not None:
            query = query.filter(Device.battery_level >= filter_dto.min_battery_level)
        
        if filter_dto.max_battery_level is not None:
            query = query.filter(Device.battery_level <= filter_dto.max_battery_level)
        
        # Compter le total avant pagination
        total = query.count()
        
        # Appliquer le tri
        if hasattr(Device, sort_by):
            column = getattr(Device, sort_by)
            if sort_order == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        
        # Appliquer la pagination
        devices = query.offset(skip).limit(limit).all()
        
        return devices, total
    
    @staticmethod
    def update_device(db: Session, device_id: str, update_data: dict) -> Optional[Device]:
        device = DeviceDAL.get_device_by_id(db, device_id)
        if not device:
            return None
        
        # Ne pas permettre la mise à jour de device_id
        update_data.pop('device_id', None)
        
        for key, value in update_data.items():
            if key == 'config' and isinstance(value, dict):
                device.set_config_dict(value)
            else:
                setattr(device, key, value)
        
        device.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def delete_device(db: Session, device_id: str) -> bool:
        device = DeviceDAL.get_device_by_id(db, device_id)
        if not device:
            return False
        
        db.delete(device)
        db.commit()
        return True
    
    @staticmethod
    def update_device_status(
        db: Session,
        device_id: str,
        status: str,
        battery_level: Optional[float] = None,
        signal_strength: Optional[float] = None
    ) -> Optional[Device]:
        device = DeviceDAL.get_device_by_id(db, device_id)
        if not device:
            return None
        
        device.status = status
        device.last_seen = datetime.utcnow()
        
        if battery_level is not None:
            device.battery_level = battery_level
        
        if signal_strength is not None:
            device.signal_strength = signal_strength
        
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def count_devices(db: Session) -> int:
        return db.query(Device).count()
    
    @staticmethod
    def get_devices_by_status(db: Session, status: str) -> List[Device]:
        return db.query(Device).filter(Device.status == status).all()
    
    @staticmethod
    def get_devices_by_owner(db: Session, owner_id: str) -> List[Device]:
        return db.query(Device).filter(Device.owner_id == owner_id).all()