from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.domain.repository.analytics_repository import IAnalyticsRepository
from app.infrastructure.models import TerritorialDataModel


class PostgresAnalyticsRepository(IAnalyticsRepository):

    def __init__(self, db: Session):
        # inyeccion instancia de la base de datos
        self.db = db

    async def save_territorial_data_batch(
        self, dataset_id: str, records: List[Dict[str, Any]]
    ) -> bool:

        # Toma los diccionarios a objetos
        try:
            # 1. Mapeamos los diccionarios a objetos de SQLAlchemy
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

            # 2. Guardado masivo (bulk insert) para no saturar la base de datos
            self.db.add_all(db_records)
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error fatal guardando en db_analytics: {e}")
            return False
