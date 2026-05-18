from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.domain.repository.analytics_repository import IAnalyticsRepository
from app.infrastructure.models import TerritorialDataModel, ZoneScore


class PostgresAnalyticsRepository(IAnalyticsRepository):

    def __init__(self, db: Session):
        self.db = db

    async def save_territorial_data_batch(
        self, dataset_id: str, records: List[Dict[str, Any]]
    ) -> bool:
        try:
            db_records = [
                TerritorialDataModel(
                    dataset_id=dataset_id,
                    zone_code=record.get("zone_code", "N/A"),
                    zone_name=record.get("zone_name", "UNKNOWN"),
                    region=record.get("region", "N/A"),
                    metrics=record.get("metrics", {}),
                )
                for record in records
            ]
            self.db.add_all(db_records)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error fatal guardando en db_analytics: {e}")
            return False

    async def get_territorial_data(self, dataset_id: str) -> List[Dict[str, Any]]:
        try:
            db_records = (
                self.db.query(TerritorialDataModel)
                .filter(TerritorialDataModel.dataset_id == dataset_id)
                .all()
            )
            result = []
            for record in db_records:
                result.append({
                    "zone_code": record.zone_code,
                    "zone_name": record.zone_name,
                })
            return result
        except Exception as e:
            print(f"Error consultando db_analytics para el dataset {dataset_id}: {e}")
            return []

    async def get_territorial_data_with_metrics(
        self, dataset_id: str
    ) -> List[Dict[str, Any]]:
        try:
            db_records = (
                self.db.query(TerritorialDataModel)
                .filter(TerritorialDataModel.dataset_id == dataset_id)
                .all()
            )

            if not db_records:
                return []

            seen = set()
            result = []

            for record in db_records:
                if record.zone_code in seen:
                    continue
                seen.add(record.zone_code)

                metrics = record.metrics or {}

                result.append({
                    "zone_code": record.zone_code,
                    "zone_name": record.zone_name,
                    "poblacion": float(metrics.get("poblacion", 0.0)),
                    "ingresos": float(metrics.get("ingresos", 0.0)),
                    "competencia": float(metrics.get("competencia", 0.0)),
                })

            return result

        except Exception as e:
            print(f"Error consultando métricas territoriales: {e}")
            return []
#Metodo para devolver zonas y pesos del csv provenientes de ms-transform
    def get_results_with_names(self, execution_id: int) -> List[Dict[str, Any]]:
        zone_scores = (
            self.db.query(ZoneScore)
            .filter(ZoneScore.execution_id == execution_id)
            .order_by(ZoneScore.rank_position)
            .all()
        )

        results = []
        for zs in zone_scores:
            territorial = (
                self.db.query(TerritorialDataModel)
                .filter(TerritorialDataModel.zone_code == zs.zone_code)
                .first()
            )
            results.append({
                "zone_code": zs.zone_code,
                "zone_name": territorial.zone_name if territorial else zs.zone_code,
                "score": zs.score_value,
                "rank": zs.rank_position,
            })

        return results