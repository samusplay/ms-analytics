from fastapi import APIRouter

from app.routers import indicators_router, sync_router

#enrutador
api_router=APIRouter()

#Registrar Rutas

api_router.include_router(
    sync_router.router,
    tags=["Internal Pipeline"]
)

api_router.include_router(
    indicators_router.router,
    tags=["Analytics Indicators"]
)