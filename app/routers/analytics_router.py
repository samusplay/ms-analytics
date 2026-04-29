from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List

from app.application.analytics_service import AnalyticsService
from app.database import get_db

analytics_router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analítica y Scoring"]
)

@analytics_router.get("/compare")
async def compare_zones(
    dataset_id: str,
    zones: str,
    db: Session = Depends(get_db)
):
    """
    HU18 (CA 3): Recibe una lista de códigos de zona por URL (GET), 
    busca sus métricas, consulta la BD y devuelve los datos estandarizados.
    """
    zone_codes = [z.strip() for z in zones.split(",") if z.strip()]
    
    if len(zone_codes) < 2:
        raise HTTPException(status_code=400, detail="Se requieren al menos 2 zonas para comparar.")
    if len(zone_codes) > 4:
        raise HTTPException(status_code=400, detail="Máximo 4 zonas permitidas para comparación.")
        
    service = AnalyticsService()
    try:
        results = await service.calculate_comparison_scores(dataset_id, zone_codes, db)
        return {
            "success": True,
            "data": results,
            "message": "Zonas comparadas exitosamente"
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail="Error interno al calcular los scores.")
