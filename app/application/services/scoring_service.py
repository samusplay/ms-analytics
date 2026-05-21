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

        try:
            # CA1 — Obtener pesos activos desde ms-configuration
            weights = self.config_client.get_active_weights()
    
            # CA2 — Normalizar datos por zona (Min-Max)
            normalized = self._normalize(zones_data)
    
            # CA2 — Calcular score por zona con penalización
            scored = []
            for zone in normalized:
                zone_code = zone.get("zone_code", "UNKNOWN")
                norm_values = {
                    "poblacion": float(zone.get("poblacion", 0) or 0),
                    "ingresos": float(zone.get("ingresos", 0) or 0),
                    "competencia": float(zone.get("competencia", 0) or 0),
                }
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
    
            if self.audit_client:
                asyncio.create_task(
                    self.audit_client.send_operation_event(
                        status="EXITOSO",
                        summary=f"Construcción de score de oportunidad generada para el dataset {dataset_id}. {len(scored)} zonas analizadas."
                    )
                )
                asyncio.create_task(
                    self.audit_client.send_operation_event(
                        status="EXITOSO",
                        summary=f"Ranking territorial generado para el dataset {dataset_id}. {len(scored)} zonas analizadas."
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
        except Exception as e:
            if self.audit_client:
                asyncio.create_task(
                    self.audit_client.send_operation_event(
                        status="FALLIDO",
                        summary=f"Fallo en construcción de score o ranking para dataset {dataset_id}: {str(e)}"
                    )
                )
            raise e

    def _normalize(self, data: List[Dict]) -> List[Dict]:
        """Min-Max normalization para poblacion, ingresos, competencia"""
        if not data:
            return []

        numeric_keys = ["poblacion", "ingresos", "competencia"]
        min_max = {}

        for key in numeric_keys:
            values = [
                float(row[key])
                for row in data
                if row.get(key) is not None
            ]
            if values:
                min_max[key] = {"min": min(values), "max": max(values)}

        normalized = []
        for row in data:
            norm_row = dict(row)
            for key in numeric_keys:
                if key in min_max:
                    mn = min_max[key]["min"]
                    mx = min_max[key]["max"]
                    val = float(row.get(key, 0) or 0)
                    norm_row[key] = (
                        0.0 if mx == mn
                        else round((val - mn) / (mx - mn), 4)
                    )
            normalized.append(norm_row)

        return normalized