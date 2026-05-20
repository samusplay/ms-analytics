import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
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
from app.domain.repository.audit_client_port import AuditClientPort
from app.infrastructure.audit_client_impl import AuditClientImpl

router = APIRouter()

def get_audit_client() -> AuditClientPort:
    return AuditClientImpl()

# La fábrica del servicio — FastAPI la llama automáticamente
def get_indicators_service(
    db: Session = Depends(get_db),
    audit_client: AuditClientPort = Depends(get_audit_client)
) -> CalculateIndicatorsService:
    repository = PostgresAnalyticsRepository(db)
    estrategias_kpi = {
        "volumen_total": TotalVolumeStrategy(),
        "cobertura_territorial": CoverageStrategy(),
        "zona_top": TopZoneStrategy(),
        "densidad_promedio": DensityStrategy()
    }
    
    return CalculateIndicatorsService(repository=repository, strategies=estrategias_kpi, audit_client=audit_client)
#Endpoint de inddicadores (no modificar)
@router.get("/indicators/{dataset_id}")
async def get_indicators(
    dataset_id: str,
    service: CalculateIndicatorsService = Depends(get_indicators_service),
    x_trace_id: str = Header(None, alias="X-Trace-Id")
):
    trace_id = x_trace_id or str(uuid.uuid4())
    try:
        return await service.execute(dataset_id, trace_id=trace_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        print(f"Error calculando indicadores para {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno calculando indicadores")
    
