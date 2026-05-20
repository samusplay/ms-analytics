

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class TerritorialDataModel(Base):
    #modelo de  tabla
    __tablename__="territorial_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(String, index=True, nullable=False) # Para saber de qué corrida son estos datos
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    metrics = Column(JSON, nullable=False) #guardamos la metricas

class ScoreExecution(Base):
    """CA3: Cabecera de cada ejecución de scoring"""
    __tablename__ = "score_execution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, nullable=False)
    configuration_id = Column(Integer, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="OK")

    zone_scores = relationship("ZoneScore", back_populates="execution")
    traces = relationship("Trace", back_populates="execution")


class ZoneScore(Base):
    """CA3: Puntaje calculado por zona"""
    __tablename__ = "zone_score"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("score_execution.id"), nullable=False)
    zone_code = Column(String(20), nullable=False)
    score_value = Column(Float, nullable=False)
    rank_position = Column(Integer, nullable=True)

    execution = relationship("ScoreExecution", back_populates="zone_scores")
    trace = relationship("Trace", back_populates="zone_score", uselist=False)

class Trace(Base):
    """CA4: Trazabilidad completa del cálculo para auditoría"""
    __tablename__ = "trace"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("score_execution.id"), nullable=False)
    zone_score_id = Column(Integer, ForeignKey("zone_score.id"), nullable=True)
    zone_code = Column(String(20), nullable=False)
    inputs = Column(JSON, nullable=False)
    weights = Column(JSON, nullable=False)
    formula = Column(String, nullable=False)

    execution = relationship("ScoreExecution", back_populates="traces")
    zone_score = relationship("ZoneScore", back_populates="trace")