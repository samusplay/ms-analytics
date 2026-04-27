from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.domain.repository.score_repository_interface import IScoreRepository
from app.infrastructure.models import ScoreExecution, Trace, ZoneScore


class PostgresScoreRepository(IScoreRepository):

    def __init__(self, db: Session):
        self.db = db

    def save_execution(
        self,
        dataset_id: str,
        configuration_id: int,
    ) -> ScoreExecution:
        execution = ScoreExecution(
            dataset_id=dataset_id,
            configuration_id=configuration_id,
            status="OK",
        )
        self.db.add(execution)
        self.db.flush()
        return execution

    def save_zone_scores(
        self,
        execution_id: int,
        scored_zones: List[Dict[str, Any]],
    ) -> List[ZoneScore]:
        zone_scores = []
        for item in scored_zones:
            zs = ZoneScore(
                execution_id=execution_id,
                zone_code=item["zone_code"],
                score_value=item["score"],
                rank_position=item["rank"],
            )
            self.db.add(zs)
            self.db.flush()
            zone_scores.append(zs)
        return zone_scores

    def save_trace(
        self,
        execution_id: int,
        zone_score_id: int,
        zone_code: str,
        inputs: Dict,
        weights: Dict,
        formula: str,
    ) -> Trace:
        trace = Trace(
            execution_id=execution_id,
            zone_score_id=zone_score_id,
            zone_code=zone_code,
            inputs=inputs,
            weights=weights,
            formula=formula,
        )
        self.db.add(trace)
        return trace

    def get_results(
        self,
        execution_id: int,
    ) -> List[ZoneScore]:
        return (
            self.db.query(ZoneScore)
            .filter(ZoneScore.execution_id == execution_id)
            .order_by(ZoneScore.rank_position)
            .all()
        )

    def get_trace(
        self,
        execution_id: int,
        zone_code: str,
    ) -> Trace:
        return (
            self.db.query(Trace)
            .filter(
                Trace.execution_id == execution_id,
                Trace.zone_code == zone_code,
            )
            .first()
        )

#Guardar en la db
    def commit(self) -> None:
        self.db.commit()
    
    def get_last_execution_by_dataset(
    self,
    dataset_id: str,
      ) -> ScoreExecution:
        return (
        self.db.query(ScoreExecution)
        .filter(ScoreExecution.dataset_id == dataset_id)
        .order_by(ScoreExecution.executed_at.desc())
        .first()
    )