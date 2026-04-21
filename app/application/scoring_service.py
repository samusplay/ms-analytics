# application/scoring_service.py
from datetime import datetime

class ScoringService:

    def __init__(self, config_client, repository, trace_repository, strategy):
        self.config_client = config_client
        self.repository = repository
        self.trace_repository = trace_repository
        self.strategy = strategy

    def execute(self, zones, transformation_run_id):

        # CA1: consumir configuración
        config = self.config_client.get_active_configuration()

        # cálculo
        results = self.strategy.calculate(zones, config)

        # ranking
        results_sorted = sorted(results, key=lambda x: x["score"], reverse=True)

        # CA3: persistencia
        execution = {
            "transformation_run_id": transformation_run_id,
            "configuration_id": config["id"],
            "executed_at": datetime.utcnow(),
            "formula_version": "v1",
            "status": "SUCCESS"
        }

        execution_id = self.repository.save_execution(execution)

        zone_scores = []
        for rank, r in enumerate(results_sorted, start=1):
            zone_scores.append({
                "score_execution_id": execution_id,
                "zone_code": r["zone_code"],
                "score_value": r["score"],
                "rank_position": rank
            })

            # CA4: trazabilidad
            self.trace_repository.save_trace({
                "execution_id": execution_id,
                "zone_code": r["zone_code"],
                "inputs": r["trace"],
                "weights": config,
                "formula": "w1*p + w2*i + w3*e - w4*c"
            })

        self.repository.save_zone_scores(zone_scores)

        return {
            "execution_id": execution_id,
            "results": zone_scores
        }