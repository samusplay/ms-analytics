# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import scoring_router
from app.routers.analytics_router import analytics_router
from app.database import engine, Base

# Crear tablas SOLO si no existen
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas/verificadas correctamente")
except Exception as e:
    print(f"⚠️ Error creando tablas: {e}")

app = FastAPI(
    title="HU-12 Scoring Territorial",
    description="Microservicio para cálculo de scoring territorial con principios SOLID",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scoring_router.router)
app.include_router(analytics_router)

@app.get("/")
async def root():
    return {"service": "HU-12 Scoring Territorial", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}