
from typing import Any, Dict, List

from pydantic import BaseModel


# Molde de los pesos que vienen del MS de Configuración
class ConfigWeightsSchema(BaseModel):
    active_weights: Dict[str, float]

# Molde de los datos territoriales que traes de tu DB
class TerritorialDataSchema(BaseModel):
    record_count: int
    payload: List[Dict[str, Any]]

# El molde principal de respuesta del Pipeline
class PipelineContextResponseSchema(BaseModel):
    dataset_id: str
    configuration: ConfigWeightsSchema
    data: TerritorialDataSchema