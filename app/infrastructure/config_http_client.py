import logging
import os
from typing import Dict

from fastapi import requests

from app.domain.config_provider_interface import IConfigProvider


class ConfigHttpClient(IConfigProvider):
    # Implementacion de la firma del puerto
    def __init__(self):
        self.base_url = os.getenv(
            "CONFIG_SERVICE_URL", "http://ms-configuration:8000/api/v1"
        )
        self.timeout = int(os.getenv("CONFIG_SERVICE_TIMEOUT", 5))

    # Obtenemos los pesos del de configuracion
    def get_active_weights(self) -> Dict[str, float]:
        endpoint = f"{self.base_url}/profiles"

        try:
            response = requests.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            profiles = response.json()

            active_profile = next((p for p in profiles if p.get("is_active")), None)

            if active_profile:
                return {
                    "peso_poblacion": active_profile.get("peso_poblacion"),
                    "peso_ingresos": active_profile.get("peso_ingresos"),
                    "peso_competencia": active_profile.get("peso_competencia"),
                }

            return self._fallback_weights()
        except Exception as e:
            logging.error(f"Error consultando perfiles en {endpoint}: {e}")
            return self._fallback_weights()

    #
    def _fallback_weights(self) -> Dict[str, float]:
        return {"peso_poblacion": 0.34, "peso_ingresos": 0.33, "peso_competencia": 0.33}
