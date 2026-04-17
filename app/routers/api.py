from fastapi import APIRouter

#enrutador
api_router=APIRouter()

#Registrar Rutas
from app.routers.analysis_router import router as analysis_router

api_router.include_router(analysis_router)