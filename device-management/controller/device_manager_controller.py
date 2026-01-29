from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from dal.device_manager_dal import DeviceDAL
from dto.device_manager_dto import (
    DeviceCreateDTO,
    DeviceUpdateDTO,
    DeviceResponseDTO,
    DeviceListDTO,
    DeviceFilterDTO,
    DeviceStatusUpdateDTO
)
from entities.database import get_db
from helpers.rabbitmq_helper import rabbitmq_helper
from helpers.redis_helper import redis_helper
from helpers.auth_helper import AuthHelper

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/devices", tags=["devices"])

# Dependency pour vérifier l'authentification
async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        # Format: "Bearer <token>"
        token = authorization.split(" ")[1]
        payload = AuthHelper.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return payload
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format"
        )

@router.post("/", response_model=DeviceResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_dto: DeviceCreateDTO,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Créer un nouveau device"""
    # Vérifier si le device existe déjà
    existing_device = DeviceDAL.get_device_by_id(db, device_dto.device_id)
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with ID {device_dto.device_id} already exists"
        )
    
    # Ajouter l'owner_id depuis le token si non fourni
    device_data = device_dto.model_dump()
    if not device_data.get('owner_id') and 'sub' in token_payload:
        device_data['owner_id'] = token_payload['sub']
    
    # Créer le device
    device = DeviceDAL.create_device(db, device_data)
    
    # Mettre en cache
    redis_helper.cache_device(device.device_id, device.to_dict())
    
    # Publier l'événement
    await rabbitmq_helper.publish_device_event(
        event_type="created",
        device_id=device.device_id,
        data=device.to_dict()
    )
    
    logger.info(f"Device created: {device.device_id}")
    return device

@router.get("/", response_model=DeviceListDTO)
def get_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
    owner_id: Optional[str] = None,
    min_battery: Optional[float] = Query(None, ge=0, le=100),
    max_battery: Optional[float] = Query(None, ge=0, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Récupérer la liste des devices avec pagination et filtres"""
    # Construire le DTO de filtre
    filter_dto = DeviceFilterDTO(
        search=search,
        device_type=device_type,
        status=status,
        is_active=is_active,
        owner_id=owner_id,
        min_battery_level=min_battery,
        max_battery_level=max_battery
    )
    
    # Calculer le skip
    skip = (page - 1) * page_size
    
    # Récupérer les devices
    devices, total = DeviceDAL.get_devices(
        db=db,
        filter_dto=filter_dto,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Calculer le nombre total de pages
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return DeviceListDTO(
        devices=devices,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{device_id}", response_model=DeviceResponseDTO)
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Récupérer un device spécifique"""
    # Vérifier le cache d'abord
    cached_device = redis_helper.get_cached_device(device_id)
    if cached_device:
        return cached_device
    
    # Récupérer depuis la base de données
    device = DeviceDAL.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Mettre en cache
    redis_helper.cache_device(device_id, device.to_dict())
    
    return device

@router.put("/{device_id}", response_model=DeviceResponseDTO)
async def update_device(
    device_id: str,
    device_dto: DeviceUpdateDTO,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Mettre à jour un device"""
    # Vérifier si le device existe
    device = DeviceDAL.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Mettre à jour le device
    updated_device = DeviceDAL.update_device(db, device_id, device_dto.model_dump(exclude_unset=True))
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Mettre à jour le cache
    redis_helper.cache_device(device_id, updated_device.to_dict())
    
    # Publier l'événement
    await rabbitmq_helper.publish_device_event(
        event_type="updated",
        device_id=device_id,
        data=updated_device.to_dict()
    )
    
    logger.info(f"Device updated: {device_id}")
    return updated_device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Supprimer un device"""
    # Vérifier si le device existe
    device = DeviceDAL.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Supprimer le device
    success = DeviceDAL.delete_device(db, device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Supprimer du cache
    redis_helper.invalidate_device_cache(device_id)
    
    # Publier l'événement
    await rabbitmq_helper.publish_device_event(
        event_type="deleted",
        device_id=device_id,
        data={"device_id": device_id}
    )
    
    logger.info(f"Device deleted: {device_id}")

@router.post("/{device_id}/status", response_model=DeviceResponseDTO)
async def update_device_status(
    device_id: str,
    status_dto: DeviceStatusUpdateDTO,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Mettre à jour le statut d'un device"""
    # Mettre à jour le statut
    updated_device = DeviceDAL.update_device_status(
        db=db,
        device_id=device_id,
        status=status_dto.status.value,
        battery_level=status_dto.battery_level,
        signal_strength=status_dto.signal_strength
    )
    
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Mettre à jour le cache
    redis_helper.cache_device(device_id, updated_device.to_dict())
    
    # Publier l'événement
    await rabbitmq_helper.publish_device_event(
        event_type="status_updated",
        device_id=device_id,
        data=updated_device.to_dict()
    )
    
    logger.info(f"Device status updated: {device_id} -> {status_dto.status}")
    return updated_device

@router.get("/health/status")
def get_devices_health_summary(db: Session = Depends(get_db)):
    """Obtenir un résumé de santé des devices"""
    total = DeviceDAL.count_devices(db)
    online_devices = DeviceDAL.get_devices_by_status(db, "online")
    offline_devices = DeviceDAL.get_devices_by_status(db, "offline")
    error_devices = DeviceDAL.get_devices_by_status(db, "error")
    
    return {
        "total_devices": total,
        "online": len(online_devices),
        "offline": len(offline_devices),
        "error": len(error_devices),
        "health_percentage": (len(online_devices) / total * 100) if total > 0 else 0
    }