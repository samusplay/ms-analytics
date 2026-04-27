
from typing import List

from pydantic import BaseModel


#Lo que esepra recibir el ednpoint
class ZoneDataInput(BaseModel):
    zone_code: str
    zone_name: str
    poblacion: float = 0.0
    ingresos: float = 0.0
    competencia: float = 0.0


class ScoringRequestSchema(BaseModel):
    data: List[ZoneDataInput]