from fastapi import APIRouter

from app.routers import indicators_router, sync_config, sync_router

#enrutador
api_router=APIRouter()

#Registrar Rutas

#pipline de consumo de transformacion
api_router.include_router(
    sync_router.router,
    tags=["Internal Pipeline"]
)

api_router.include_router(
    indicators_router.router,
    tags=["Analytics Indicators"]
)
#Pipline de consumo de configuration
# app/routers/api.py
api_router.include_router(
    sync_config.router,
    tags=["Pipeline Configuration"]
)