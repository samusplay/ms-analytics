# app/routers/scoring_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.application.scoring_service import ScoringService
from app.application.normalizer import MinMaxNormalizer
from app.application.calculator import WeightedScoringStrategy
from app.infrastructure.config_client import ConfigurationClient
from app.infrastructure.score_repository import ScoreRepository
from app.infrastructure.trace_repository import TraceRepository
from app.models import ZoneScore, ScoreExecution, Trace

router = APIRouter()

def get_scoring_service():
    return ScoringService(
        normalizer=MinMaxNormalizer(),
        strategy=WeightedScoringStrategy(),
        config_client=ConfigurationClient(),
        score_repository=ScoreRepository(),
        trace_repository=TraceRepository()
    )

@router.post("/api/v1/analytics/internal/sync/{dataset_id}")
async def sync_scoring(
    dataset_id: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db),  # ← Esto ya es Session, no generador
    scoring_service: ScoringService = Depends(get_scoring_service)
):
    try:
        zones_data = request.get("data", [])
        
        if not zones_data:
            return {
                "success": False, 
                "data": None, 
                "error": "No se proporcionaron zonas para procesar"
            }
        
        # Validar datos
        for zone in zones_data:
            if not zone.get("zone_code"):
                return {
                    "success": False, 
                    "data": None, 
                    "error": "Todas las zonas deben tener zone_code"
                }
            
            metrics = zone.get("metrics", {})
            required_metrics = ['poblacion', 'ingreso', 'educacion', 'competencia']
            for metric in required_metrics:
                if metric not in metrics:
                    return {
                        "success": False, 
                        "data": None, 
                        "error": f"Zona {zone.get('zone_code')} falta métrica: {metric}"
                    }
        
        # Ejecutar scoring
        execution_id, results = scoring_service.execute_scoring(db, dataset_id, zones_data)
        
        return {
            "success": True,
            "data": {
                "dataset_id": dataset_id,
                "execution_id": execution_id,
                "records_processed": len(zones_data),
                "status": "synchronized",
                "results": results
            },
            "error": None
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }


@router.get("/api/v1/analytics/scoring/results/{execution_id}")
async def get_scoring_results(execution_id: int, db: Session = Depends(get_db)):
    try:
        execution = db.query(ScoreExecution).filter(ScoreExecution.id == execution_id).first()
        
        if not execution:
            return {
                "success": False,
                "data": None,
                "error": f"Ejecución {execution_id} no encontrada"
            }
        
        results = db.query(ZoneScore).filter(
            ZoneScore.execution_id == execution_id
        ).order_by(ZoneScore.rank_position).all()
        
        return {
            "success": True,
            "data": {
                "execution_id": execution_id,
                "dataset_id": execution.dataset_id,
                "executed_at": execution.executed_at.isoformat() if execution.executed_at else None,
                "status": execution.status,
                "results": [
                    {
                        "zone_code": r.zone_code,
                        "score_value": r.score_value,
                        "rank_position": r.rank_position
                    }
                    for r in results
                ]
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }


@router.get("/api/v1/analytics/scoring/trace/{execution_id}/{zone_code}")
async def get_scoring_trace(execution_id: int, zone_code: str, db: Session = Depends(get_db)):
    try:
        trace = db.query(Trace).filter(
            Trace.execution_id == execution_id,
            Trace.zone_code == zone_code
        ).first()
        
        if not trace:
            return {
                "success": False,
                "data": None,
                "error": f"Trazabilidad no encontrada para ejecución {execution_id} zona {zone_code}"
            }
        
        return {
            "success": True,
            "data": {
                "execution_id": execution_id,
                "zone_code": zone_code,
                "inputs": trace.inputs,
                "weights": trace.weights,
                "formula": trace.formula
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }