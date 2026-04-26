# app/infrastructure/trace_repository.py
import json
from typing import Dict
from sqlalchemy.orm import Session
from app.models import Trace
from app.application.interfaces import ITraceRepository

class TraceRepository(ITraceRepository):
    def save_trace(self, db: Session, execution_id: int, zone_code: str,
                   inputs: Dict, weights: Dict, formula: str) -> None:
        """Guarda la trazabilidad - inputs y weights como JSONB"""
        trace = Trace(
            execution_id=execution_id,
            zone_code=zone_code,
            inputs=inputs,      # ← PostgreSQL JSONB acepta dict directamente
            weights=weights,    # ← PostgreSQL JSONB acepta dict directamente
            formula=formula
        )
        db.add(trace)