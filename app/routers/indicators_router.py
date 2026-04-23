from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.services.calculate_indicators_service import (
    CalculateIndicatorsService,
)
from app.application.strategies.kpi_strategies import (
    CoverageStrategy,
    DensityStrategy,
    TopZoneStrategy,
    TotalVolumeStrategy,
)
from app.infrastructure.database import get_db
from app.infrastructure.repository.postgres_analytics_repository import (
    PostgresAnalyticsRepository,
)

router = APIRouter()

# La fábrica del servicio — FastAPI la llama automáticamente
def get_indicators_service(db: Session = Depends(get_db)) -> CalculateIndicatorsService:
    repository = PostgresAnalyticsRepository(db)
    estrategias_kpi = {
        "volumen_total": TotalVolumeStrategy(),
        "cobertura_territorial": CoverageStrategy(),
        "zona_top": TopZoneStrategy(),
        "densidad_promedio": DensityStrategy()
    }
    
    return CalculateIndicatorsService(repository=repository, strategies=estrategias_kpi)
#Endpoint de inddicadores (no modificar)
@router.get("/indicators/{dataset_id}")
async def get_indicators(

    dataset_id: str,
    service: CalculateIndicatorsService = Depends(get_indicators_service)
):
    try:
        return await service.execute(dataset_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        print(f"Error calculando indicadores para {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno calculando indicadores")
    
