from fastapi import APIRouter
from app.infrastructure.clients.configuration_client import get_active_profile

router = APIRouter(prefix="/api/v1/analysis", tags=["Analysis"])

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