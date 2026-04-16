
from typing import Any, Dict, List

from pydantic import BaseModel


#molde cada fila 
class TransformedRecordSchema(BaseModel):
    zone_code: str
    zone_name: str
    region: str
    metrics: Dict[str, Any]

#el molde completo
class SyncPayloadSchema(BaseModel):
    data: List[TransformedRecordSchema]