from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DeviceHelper:
    """Helper pour la logique métier des devices"""
    
    @staticmethod
    def validate_device_data(device_data: Dict[str, Any]) -> tuple[bool, str]:
        """Valider les données d'un device"""
        if not device_data.get('device_id'):
            return False, "device_id is required"
        
        if not device_data.get('name'):
            return False, "name is required"
        
        if not device_data.get('device_type'):
            return False, "device_type is required"
        
        if device_data.get('battery_level') is not None:
            battery = device_data['battery_level']
            if not (0 <= battery <= 100):
                return False, "battery_level must be between 0 and 100"
        
        if device_data.get('signal_strength') is not None:
            signal = device_data['signal_strength']
            if not (-100 <= signal <= 0):
                return False, "signal_strength must be between -100 and 0"
        
        return True, ""
    
    @staticmethod
    def is_device_online(last_seen: datetime, timeout: int = 300) -> bool:
        """Déterminer si un device est en ligne basé sur last_seen"""
        if not last_seen:
            return False
        
        elapsed = (datetime.utcnow() - last_seen).total_seconds()
        return elapsed < timeout
    
    @staticmethod
    def calculate_device_health(device: Dict[str, Any]) -> float:
        """Calculer un score de santé du device (0-100)"""
        score = 100.0
        
        # Pénaliser si offline
        if device.get('status') == 'offline':
            score -= 50
        elif device.get('status') == 'error':
            score -= 75
        elif device.get('status') == 'maintenance':
            score -= 25
        
        # Pénaliser selon la batterie
        battery = device.get('battery_level')
        if battery is not None:
            if battery < 20:
                score -= 30
            elif battery < 50:
                score -= 15
        
        # Pénaliser selon le signal
        signal = device.get('signal_strength')
        if signal is not None:
            if signal < -80:  # signal faible
                score -= 20
        
        return max(0, min(100, score))
    
    @staticmethod
    def format_device_response(device: Any) -> Dict[str, Any]:
        """Formater un device pour la réponse"""
        data = device.to_dict() if hasattr(device, 'to_dict') else device
        
        # Ajouter des champs calculés
        if isinstance(data, dict):
            data['health_score'] = DeviceHelper.calculate_device_health(data)
        
        return data
    
    @staticmethod
    def get_device_summary_stats(devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculer les statistiques résumées d'une liste de devices"""
        if not devices:
            return {
                "total": 0,
                "online": 0,
                "offline": 0,
                "error": 0,
                "avg_battery": 0,
                "low_battery": 0
            }
        
        total = len(devices)
        online = sum(1 for d in devices if d.get('status') == 'online')
        offline = sum(1 for d in devices if d.get('status') == 'offline')
        error = sum(1 for d in devices if d.get('status') == 'error')
        
        batteries = [d.get('battery_level') for d in devices if d.get('battery_level') is not None]
        avg_battery = sum(batteries) / len(batteries) if batteries else 0
        low_battery = sum(1 for b in batteries if b < 20)
        
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "error": error,
            "avg_battery": round(avg_battery, 2),
            "low_battery": low_battery,
            "health_percentage": round((online / total * 100) if total > 0 else 0, 2)
        }
