# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB  # ← Importar JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ScoreExecution(Base):
    __tablename__ = "score_execution"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(String(50), nullable=False)
    configuration_id = Column(Integer, nullable=False)
    executed_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default="COMPLETED")


class ZoneScore(Base):
    __tablename__ = "zone_score"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("score_execution.id"), nullable=False)
    zone_code = Column(String(20), nullable=False)
    score_value = Column(Float, nullable=False)
    rank_position = Column(Integer, nullable=False)


class Trace(Base):
    __tablename__ = "trace"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("score_execution.id"), nullable=False)
    zone_code = Column(String(20), nullable=False)
    inputs = Column(JSONB, nullable=False)   # ← Cambiado a JSONB
    weights = Column(JSONB, nullable=False)  # ← Cambiado a JSONB
    formula = Column(String(500), nullable=False)  # ← Texto plano