from fastapi import APIRouter
from app.infrastructure.clients.configuration_client import get_active_profile

router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"]
)

# ==========================
# TEST ANALYSIS
# ==========================
@router.get("/test")
def test_analysis():

    profile = get_active_profile()

    if not profile:
        return {"error": "No se pudo obtener configuración"}

    # datos simulados
    data = {
        "poblacion": 100,
        "ingresos": 50,
        "competencia": 30
    }

    score = (
        data["poblacion"] * profile["peso_poblacion"] +
        data["ingresos"] * profile["peso_ingresos"] +
        data["competencia"] * profile["peso_competencia"]
    )

    return {
        "profile": profile,
        "score": score
    }


# ==========================
# ENDPOINT PARA ML
# ==========================
@router.get("/zones/metrics/{dataset_id}")
async def get_zone_metrics(dataset_id: int):

    return [
        {
            "zone_code": "ZONA-1",
            "zone_name": "ZONA-1",
            "poblacion": 1000,
            "ingresos": 500,
            "competencia": 200
        },
        {
            "zone_code": "ZONA-2",
            "zone_name": "ZONA-2",
            "poblacion": 1500,
            "ingresos": 700,
            "competencia": 300
        }
    ]