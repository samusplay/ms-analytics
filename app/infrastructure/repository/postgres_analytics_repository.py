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
                extracted = self._extract_metrics(metrics)

                result.append({
                    "zone_code": record.zone_code,
                    "zone_name": record.zone_name,
                    "poblacion": extracted["poblacion"],
                    "ingresos": extracted["ingresos"],
                    "competencia": extracted["competencia"],
                })

            return result

        except Exception as e:
            print(f"Error consultando métricas territoriales: {e}")
            return []

    @staticmethod
    def _extract_metrics(metrics: dict) -> dict:
        """Extrae poblacion, ingresos y competencia de forma inteligente, 
        buscando sinónimos cuando las claves exactas no existen."""
        
        # Intento directo con claves estándar
        direct = {
            "poblacion": metrics.get("poblacion", 0.0),
            "ingresos": metrics.get("ingresos", metrics.get("ingreso", 0.0)),
            "competencia": metrics.get("competencia", 0.0),
        }
        if any(float(v) > 0 for v in direct.values()):
            return {k: float(v) for k, v in direct.items()}

        # Búsqueda flexible por sinónimos
        search_patterns = [
            ("ingresos", ["INGRESOS", "GANANCIAS", "REVENUE", "VENTAS", "MONTO", "VALOR", "INGRESO"]),
            ("poblacion", ["POBLACION", "HABITANTES", "PERSONAS", "CANTIDAD", "VIVIENDAS", "TOTAL", "TERMINADAS"]),
            ("competencia", ["COMPETENCIA", "EMPRESAS", "RIVALES", "STORES", "NEGOCIOS"]),
        ]

        result = {"poblacion": 0.0, "ingresos": 0.0, "competencia": 0.0}
        used_keys = set()

        def clean_val(v):
            s = str(v).replace('"', '').replace(" ", "").strip()
            if "," in s and "." not in s: s = s.replace(",", "")
            elif "." in s and "," in s: s = s.replace(".", "").replace(",", ".")
            return float(s)

        for metric_name, synonyms in search_patterns:
            for syn in synonyms:
                for k, v in metrics.items():
                    if syn in str(k).upper() and k not in used_keys:
                        try:
                            result[metric_name] = clean_val(v)
                            used_keys.add(k)
                            break
                        except:
                            pass
                if result[metric_name] > 0:
                    break

        # Rellenar con cualquier columna numérica sobrante
        for k, v in metrics.items():
            if k not in used_keys:
                try:
                    val = clean_val(v)
                    if val > 0 and 1900 <= val <= 2100:
                        continue  # ignorar años
                    if result["ingresos"] == 0.0: result["ingresos"] = val
                    elif result["poblacion"] == 0.0: result["poblacion"] = val
                    elif result["competencia"] == 0.0: result["competencia"] = val
                    used_keys.add(k)
                except:
                    pass

        return result
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