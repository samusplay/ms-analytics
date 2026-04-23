from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.application.analytics_pipeline_service import AnalyticsPipelineService
from app.infrastructure.config_http_client import ConfigHttpClient
from app.infrastructure.database import get_db
from app.infrastructure.repository.postgres_analytics_repository import (
    PostgresAnalyticsRepository,
)

router=APIRouter()
#Provedor
def get_pipeline_service(
    db: Session = Depends(get_db),
) -> AnalyticsPipelineService:
    repo = PostgresAnalyticsRepository(db)
    config_client = ConfigHttpClient()
    return AnalyticsPipelineService(repo, config_client)

#Endpoint traer datos de de Confguracion
@router.get("/pipeline/fetch-context/{dataset_id}")
async def get_pipeline_context(
    dataset_id: str,
    service: AnalyticsPipelineService = Depends(get_pipeline_service),
):
    try:
        result = await service.execute_fetch_pipeline(dataset_id)
        return result

    except ValueError as e:
        # Error controlado (ej: dataset no existe)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Error interno
        raise HTTPException(
            status_code=500,
            detail="Error interno en el pipeline",
        )