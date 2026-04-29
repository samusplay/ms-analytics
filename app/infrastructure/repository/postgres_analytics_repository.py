from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.domain.repository.analytics_repository import IAnalyticsRepository
from app.infrastructure.models import TerritorialDataModel, ZoneScore


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
        
    async def get_territorial_data(self, dataset_id: str) -> List[Dict[str, Any]]:
        try:
            # consulta a sql
            db_records = (
                self.db.query(TerritorialDataModel)
                .filter(TerritorialDataModel.dataset_id == dataset_id)
                .all()
            )
            # mapeo de objetos 
            result = []
            for record in db_records:
                result.append({
                    "zone_code": record.zone_code,
                    "zone_name": record.zone_name,
                    # extraemos estartegias
                })
            return result
        except Exception as e:
            print(f"Error consultando db_analytics para el dataset {dataset_id}: {e}")
            return []

    # Implementacion impl 
    async def get_territorial_data_with_metrics(
        self, dataset_id: str
    ) -> List[Dict[str, Any]]:
        try:
            db_records = (
                self.db.query(TerritorialDataModel)
                .filter(TerritorialDataModel.dataset_id == dataset_id)
                .all()
            )
            # Contar registros por zona
            zone_counts: Dict[str, int] = {}
            for record in db_records:
                key = record.zone_code
                zone_counts[key] = zone_counts.get(key, 0) + 1

            # Deduplicar por zone_code
            seen = set()
            result = []
            index = 0
            for record in db_records:
                if record.zone_code not in seen:
                    seen.add(record.zone_code)
                    count = float(zone_counts.get(record.zone_code, 1))
                    result.append({
                        "zone_code": record.zone_code,
                        "zone_name": record.zone_name,
                        "poblacion": count,
                        "ingresos": float(index + 1),
                        "competencia": 0.0,
                    })
                    index += 1
            return result
        except Exception as e:
            print(f"Error consultando métricas territoriales: {e}")
            return []
    
    #Implnetacion Buscar Resultados Con nombre
    def get_results_with_names(self, execution_id: int) -> List[Dict[str, Any]]:
        zone_scores = (
            self.db.query(ZoneScore)
            .filter(ZoneScore.execution_id == execution_id)
            .order_by(ZoneScore.rank_position)
            .all()
        )

        results = []
        for zs in zone_scores:
            # Cruzamos con TerritorialDataModel para sacar el zone_name
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