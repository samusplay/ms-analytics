# app/infrastructure/models_config.py
from typing import Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel

class WeightConfig(BaseModel):
    """Modelo para un peso individual"""
    variable_name: str
    weight_value: float
    is_active: bool = True
    updated_at: Optional[datetime] = None


class ScoringConfig(BaseModel):
    """Modelo completo de configuración de scoring"""
    config_id: str
    name: str
    description: Optional[str] = None
    weights: Dict[str, float]
    version: str = "1.0"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConfigurationResponse(BaseModel):
    """Respuesta del ms-configuration"""
    success: bool
    data: Optional[ScoringConfig] = None
    error: Optional[str] = None