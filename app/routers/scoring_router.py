# routers/scoring_router.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/scoring/execute")
def execute_scoring():

    zones = load_zones()  # viene de transformación

    service = build_service()  # inyección de dependencias

    result = service.execute(zones, transformation_run_id=1)

    return {
        "success": True,
        "data": result,
        "error": None
    }