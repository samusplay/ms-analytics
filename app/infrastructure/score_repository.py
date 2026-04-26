# app/infrastructure/score_repository.py
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import ScoreExecution, ZoneScore
from app.application.interfaces import IScoreRepository

class ScoreRepository(IScoreRepository):
    def save_execution(self, db: Session, dataset_id: str, config_id: int) -> int:
        """Guarda una nueva ejecución y retorna el ID"""
        execution = ScoreExecution(
            dataset_id=dataset_id,
            configuration_id=config_id,
            status="COMPLETED"
        )
        db.add(execution)
        db.flush()  # Para obtener el ID sin commit
        return execution.id
    
    def save_zone_scores(self, db: Session, execution_id: int, scores: List[Dict]) -> None:
        """Guarda los puntajes individuales de cada zona"""
        for score_data in scores:
            zone_score = ZoneScore(
                execution_id=execution_id,
                zone_code=score_data['zone_code'],
                score_value=score_data['score_value'],
                rank_position=0
            )
            db.add(zone_score)
        db.flush()
    
    def update_ranking(self, db: Session, execution_id: int, rankings: List[Dict]) -> None:
        """Actualiza las posiciones de ranking"""
        for rank_data in rankings:
            db.query(ZoneScore).filter(
                ZoneScore.execution_id == execution_id,
                ZoneScore.zone_code == rank_data['zone_code']
            ).update({"rank_position": rank_data['rank_position']})