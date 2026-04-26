# app/infrastructure/config_client.py
import requests
from typing import Dict
from app.application.interfaces import IConfigClient

class ConfigurationClient(IConfigClient):
    def __init__(self, config_url: str = None):
        # Si no hay servicio de configuración, usamos pesos por defecto
        self.config_url = config_url or "http://localhost:8081/api/config/weights"
        self._cache = None
        self._use_mock = True  # ← Usar mock porque el servicio no está disponible
    
    def get_weights(self) -> Dict[str, float]:
        """Obtiene los pesos desde ms-configuration o usa valores por defecto"""
        
        # Si ya tenemos caché, usarlo
        if self._cache:
            return self._cache
        
        # Si estamos en modo mock, usar pesos por defecto
        if self._use_mock:
            weights = {
                "poblacion": 0.35,
                "ingreso": 0.35,
                "educacion": 0.20,
                "competencia": 0.10
            }
            self._cache = weights
            print("⚠️ Usando pesos por defecto (ms-configuration no disponible)")
            return weights
        
        # Intentar consumir servicio real
        try:
            response = requests.get(self.config_url, timeout=2)
            response.raise_for_status()
            data = response.json()
            weights = data.get("weights", {})
            
            # Validar que todos los pesos existen
            required = ['poblacion', 'ingreso', 'educacion', 'competencia']
            for req in required:
                if req not in weights:
                    weights[req] = 0.25
            
            self._cache = weights
            return weights
            
        except requests.RequestException as e:
            print(f"⚠️ Error obteniendo configuración: {e}")
            print("⚠️ Usando pesos por defecto")
            return {
                "poblacion": 0.35,
                "ingreso": 0.35,
                "educacion": 0.20,
                "competencia": 0.10
            }
    
    def clear_cache(self):
        """Limpia la caché de configuración"""
        self._cache = None