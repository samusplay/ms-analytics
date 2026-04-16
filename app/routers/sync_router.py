
#instaciamos router

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.analytics_service import SyncAnalyticsDataService
from app.infrastructure.database import get_db
from app.infrastructure.repository.postgres_analytics_repository import (
    PostgresAnalyticsRepository,
)
from app.schemas.sync import SyncPayloadSchema

router=APIRouter()

@router.post("/internal/sync/{dataset_id}")
async def sync_data(
        dataset_id: str,
        payload:SyncPayloadSchema,
        db:Session=Depends(get_db)
):
    try:
        repository = PostgresAnalyticsRepository(db)
        service = SyncAnalyticsDataService(repository=repository)
        
        # Pydantic v2 usa model_dump(), si usas v1 usa .dict()
        records = [item.model_dump() for item in payload.data] 
        
        result = await service.execute(dataset_id, records)
        
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error crítico en recepción de datos: {e}")
        raise HTTPException(status_code=500, detail="Fallo interno en ms-analytics guardando datos")