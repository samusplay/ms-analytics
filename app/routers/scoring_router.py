from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.services.scoring_service import ScoringService
from app.infrastructure.config_http_client import ConfigHttpClient
from app.infrastructure.database import get_db
from app.infrastructure.repository.postgres_analytics_repository import (
    PostgresAnalyticsRepository,
)
from app.infrastructure.repository.score_repository import PostgresScoreRepository
from app.schemas.scoring import ScoringRequestSchema

router = APIRouter()


def get_scoring_service(db: Session = Depends(get_db)) -> ScoringService:
    """Fábrica de dependencias — ensambla las capas"""
    return ScoringService(
        score_repository=PostgresScoreRepository(db),
        config_client=ConfigHttpClient(),
    )


# CA1, CA2, CA3, CA4
@router.post("/scoring/execute/{dataset_id}")
async def execute_scoring(
    dataset_id: str,
    request: ScoringRequestSchema,
    service: ScoringService = Depends(get_scoring_service),
):
    try:
        zones_data = [zone.model_dump() for zone in request.data]

        if not zones_data:
            raise HTTPException(
                status_code=400,
                detail="No hay datos de zonas para procesar"
            )

        result = service.execute(
            dataset_id=dataset_id,
            zones_data=zones_data,
        )
        return {"success": True, "data": result, "error": None}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en scoring: {e}")
        raise HTTPException(status_code=500, detail="Error interno en scoring")


# CA1 — Verificar pesos activos consumidos desde ms-configuration
@router.get("/config/status")
def get_config_status():
    try:
        client = ConfigHttpClient()
        weights = client.get_active_weights()
        return {"success": True, "weights_active": weights}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# CA3 — Resultados de una ejecución
@router.get("/results/{execution_id}")
def get_results(
    execution_id: int,
    db: Session = Depends(get_db),
):
    repo = PostgresScoreRepository(db)
    results = repo.get_results(execution_id)
    if not results:
        raise HTTPException(status_code=404, detail="Ejecución no encontrada")
    return {
        "success": True,
        "execution_id": execution_id,
        "zones": [
            {
                "zone_code": r.zone_code,
                "score": r.score_value,
                "rank": r.rank_position,
            }
            for r in results
        ],
    }


# CA4 — Trazabilidad por zona
@router.get("/trace/{execution_id}/{zone_code}")
def get_trace(
    execution_id: int,
    zone_code: str,
    db: Session = Depends(get_db),
):
    repo = PostgresScoreRepository(db)
    trace = repo.get_trace(execution_id, zone_code)
    if not trace:
        raise HTTPException(
            status_code=404,
            detail=f"Traza no encontrada para ejecución {execution_id} zona {zone_code}",
        )
    return {
        "success": True,
        "zone_code": zone_code,
        "inputs": trace.inputs,
        "weights": trace.weights,
        "formula": trace.formula,
    }

# CA1 ranking — último resultado por dataset
@router.get("/ranking/{dataset_id}")
def get_ranking(dataset_id: str, db: Session = Depends(get_db)):
    repo = PostgresScoreRepository(db)
    execution = repo.get_last_execution_by_dataset(dataset_id)

    if not execution:
        raise HTTPException(
            status_code=404,
            detail="No hay scoring calculado para este dataset"
        )

    results = repo.get_results_with_names(execution.id)  # ← cambiar esto

    return {
        "success": True,
        "dataset_id": dataset_id,
        "execution_id": execution.id,
        "executed_at": execution.executed_at,
        "zones": results,  # ← ya viene con zone_name
    }

#Datos territorailes para alimentar el scoring
@router.get("/zones/metrics/{dataset_id}")
async def get_zones_with_metrics(
    dataset_id: str,
    db: Session = Depends(get_db),
):
    try:
        repository = PostgresAnalyticsRepository(db)
        data = await repository.get_territorial_data_with_metrics(dataset_id)
        if not data:
            raise HTTPException(
                status_code=404,
                detail="No hay datos territoriales para este dataset"
            )
        return {"success": True, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error obteniendo métricas: {e}")
        raise HTTPException(status_code=500, detail="Error interno")