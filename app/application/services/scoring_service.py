import asyncio
from typing import Any, Dict, List

from app.application.calculator import WeightedScoringCalculator
from app.domain.repository.score_repository_interface import IScoreRepository
from app.infrastructure.config_http_client import ConfigHttpClient
from app.domain.repository.audit_client_port import AuditClientPort


class ScoringService:
    """
    Orquesta CA1 → CA2 → CA3 → CA4.
    No conoce detalles de PostgreSQL ni de HTTP — solo trabaja con interfaces.
    """

    def __init__(
        self,
        score_repository: IScoreRepository,
        config_client: ConfigHttpClient,
        audit_client: AuditClientPort = None,
    ):
        self.score_repository = score_repository
        self.config_client = config_client
        self.audit_client = audit_client
        self.calculator = WeightedScoringCalculator()

    def execute(
        self,
        dataset_id: str,
        zones_data: List[Dict[str, Any]],
        trace_id: str = None,
    ) -> Dict[str, Any]:

        # CA1 — Obtener pesos activos desde ms-configuration
        weights = self.config_client.get_active_weights()

        # CA2 — Normalizar datos por zona (Min-Max)
        normalized = self._normalize(zones_data)

        # CA2 — Calcular score por zona con penalización
        scored = []
        for zone in normalized:
            zone_code = zone.get("zone_code", "UNKNOWN")
            
            # --- NUEVO: Extracción inteligente de métricas ---
            # Buscar en todo el dict de la zona para extraer las variables necesarias.
            norm_values = {"poblacion": 0.0, "ingresos": 0.0, "competencia": 0.0}
            used_keys = set()
            
            # 1. Búsqueda por sinónimos
            search_patterns = [
                ("ingresos", ["INGRESOS", "GANANCIAS", "REVENUE", "VENTAS", "MONTO", "VALOR"]),
                ("poblacion", ["POBLACION", "HABITANTES", "PERSONAS", "CANTIDAD", "VIVIENDAS", "TOTAL", "TERMINADAS"]),
                ("competencia", ["COMPETENCIA", "EMPRESAS", "RIVALES", "STORES", "NEGOCIOS"])
            ]
            
            for metric_name, synonyms in search_patterns:
                for s in synonyms:
                    for k, v in zone.items():
                        if k not in ["zone_code", "zone_name"] and s in str(k).upper() and k not in used_keys:
                            try:
                                norm_values[metric_name] = float(v)
                                used_keys.add(k)
                                break
                            except: pass
                    if norm_values[metric_name] > 0: break
            
            # 2. Si no encontró sinónimos, usar cualquier valor numérico sobrante
            for k, v in zone.items():
                if k not in ["zone_code", "zone_name"] and k not in used_keys:
                    try:
                        val = float(v)
                        if norm_values["ingresos"] == 0.0: norm_values["ingresos"] = val
                        elif norm_values["poblacion"] == 0.0: norm_values["poblacion"] = val
                        elif norm_values["competencia"] == 0.0: norm_values["competencia"] = val
                        used_keys.add(k)
                    except: pass
            score = self.calculator.calculate(norm_values, weights)
            scored.append({
                "zone_code": zone_code,
                "score": score,
                "normalized": norm_values,
            })

        # Ranking descendente por score
        scored.sort(key=lambda x: x["score"], reverse=True)
        for i, item in enumerate(scored, start=1):
            item["rank"] = i

        # CA3 — Persistir ejecución y puntajes
        execution = self.score_repository.save_execution(
            dataset_id=dataset_id,
            configuration_id=0,
        )
        zone_scores = self.score_repository.save_zone_scores(
            execution_id=execution.id,
            scored_zones=scored,
        )

        # CA4 — Guardar trazas para auditoría
        formula = (
            "Score = (peso_poblacion * pob) "
            "+ (peso_ingresos * ing) "
            "- (peso_competencia * comp)"
        )
        for i, item in enumerate(scored):
            self.score_repository.save_trace(
                execution_id=execution.id,
                zone_score_id=zone_scores[i].id,
                zone_code=item["zone_code"],
                inputs={"normalized": item["normalized"]},
                weights=weights,
                formula=formula,
            )

        # Persistir todo en una sola transacción
        self.score_repository.commit()

        if self.audit_client and trace_id:
            asyncio.create_task(
                self.audit_client.send_calculation_event(
                    trace_id=trace_id,
                    estado="SUCCESS",
                    summary=f"Construcción de score generada para el dataset {dataset_id}. {len(scored)} zonas analizadas."
                )
            )

        return {
            "execution_id": execution.id,
            "dataset_id": dataset_id,
            "total_zones": len(scored),
            "weights_used": weights,
            "results": [
                {
                    "zone_code": s["zone_code"],
                    "score": s["score"],
                    "rank": s["rank"],
                }
                for s in scored
            ],
        }

    def _normalize(self, data: List[Dict]) -> List[Dict]:
        """Min-Max normalization para todas las variables numéricas encontradas"""
        if not data:
            return []

        # Detectar todas las claves numéricas posibles
        numeric_keys = set()
        for row in data:
            for k, v in row.items():
                if k not in ["zone_code", "zone_name", "id"]:
                    try:
                        float(v)
                        numeric_keys.add(k)
                    except: pass
                    
        min_max = {}
        for key in numeric_keys:
            values = []
            for row in data:
                try: values.append(float(row.get(key, 0) or 0))
                except: pass
            if values:
                min_max[key] = {"min": min(values), "max": max(values)}

        normalized = []
        for row in data:
            norm_row = dict(row)
            for key in numeric_keys:
                if key in min_max:
                    mn = min_max[key]["min"]
                    mx = min_max[key]["max"]
                    try:
                        val = float(row.get(key, 0) or 0)
                        norm_row[key] = (
                            0.0 if mx == mn
                            else round((val - mn) / (mx - mn), 4)
                        )
                    except: pass
            normalized.append(norm_row)

        return normalized