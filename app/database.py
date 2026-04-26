# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Crear Base para modelos
Base = declarative_base()

class DatabaseConfig:
    def __init__(self):
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/ms_analytics"
        )
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:  # ← Retorna Session, no Generator
        """Obtiene una sesión de BD"""
        return self.SessionLocal()

# Instancia global
db_config = DatabaseConfig()
engine = db_config.engine

def get_db() -> Generator[Session, None, None]:
    """Dependencia para FastAPI que retorna un generador"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()