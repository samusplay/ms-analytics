# app/application/scoring_service.py
from typing import List, Dict, Tuple
import json
from sqlalchemy.orm import Session
from app.application.interfaces import (
    INormalizer, IScoringStrategy, IConfigClient,
    IScoreRepository, ITraceRepository
)


class ScoringService:
    """
    Servicio principal de scoring - SRP: Orquesta el flujo de trabajo
    DIP: Depende de abstracciones, no de implementaciones concretas
    """
    
    def __init__(
        self,
        normalizer: INormalizer,
        strategy: IScoringStrategy,
        config_client: IConfigClient,
        score_repository: IScoreRepository,
        trace_repository: ITraceRepository
    ):
        self.normalizer = normalizer
        self.strategy = strategy
        self.config_client = config_client
        self.score_repository = score_repository
        self.trace_repository = trace_repository
    
    def execute_scoring(self, db: Session, dataset_id: str, zones_data: List[Dict]) -> Tuple[int, List[Dict]]:
        """Ejecuta el flujo completo de scoring"""
        
        # CA1: Consumir configuración
        weights = self.config_client.get_weights()
        config_id = 1  # Se obtendría de la respuesta de configuración
        
        # Extraer métricas para normalización
        metrics = self._extract_metrics(zones_data)
        
        # CA2: Normalizar variables
        normalized_metrics = self.normalizer.normalize_metrics(metrics)
        
        # Crear ejecución en BD
        execution_id = self.score_repository.save_execution(db, dataset_id, config_id)
        
        # Calcular scores y preparar datos
        scores = []
        traces = []
        
        for idx, zone in enumerate(zones_data):
            zone_code = zone.get('zone_code')
            
            # Obtener valores normalizados
            normalized_values = {
                'poblacion': normalized_metrics['poblacion'][idx],
                'ingreso': normalized_metrics['ingreso'][idx],
                'educacion': normalized_metrics['educacion'][idx],
                'competencia': normalized_metrics['competencia'][idx]
            }
            
            # Calcular score usando la estrategia
            score = self.strategy.calculate(normalized_values, weights)
            
            scores.append({
                'zone_code': zone_code,
                'score_value': round(score, 3)
            })
            
            # Preparar trazabilidad (CA4)
            inputs = self._prepare_inputs(zone, normalized_values)
            formula = self._build_formula(normalized_values, weights, score)
            
            traces.append({
                'zone_code': zone_code,
                'inputs': inputs,
                'weights': weights,
                'formula': formula
            })
        
        # Calcular ranking
        rankings = self._calculate_ranking(scores)
        
        # CA3: Persistir resultados
        self.score_repository.save_zone_scores(db, execution_id, scores)
        self.score_repository.update_ranking(db, execution_id, rankings)
        
        # CA4: Guardar trazabilidad
        for trace_data in traces:
            self.trace_repository.save_trace(
                db, execution_id, trace_data['zone_code'],
                trace_data['inputs'], trace_data['weights'], trace_data['formula']
            )
        
        db.commit()
        
        final_results = self._merge_scores_with_rankings(scores, rankings)
        
        return execution_id, final_results
    
    def _extract_metrics(self, zones_data: List[Dict]) -> Dict[str, List[float]]:
        """Extrae las métricas de todas las zonas"""
        metrics = {
            'poblacion': [],
            'ingreso': [],
            'educacion': [],
            'competencia': []
        }
        
        for zone in zones_data:
            zone_metrics = zone.get('metrics', {})
            metrics['poblacion'].append(float(zone_metrics.get('poblacion', 0)))
            metrics['ingreso'].append(float(zone_metrics.get('ingreso', 0)))
            metrics['educacion'].append(float(zone_metrics.get('educacion', 0)))
            metrics['competencia'].append(float(zone_metrics.get('competencia', 0)))
        
        return metrics
    
    def _prepare_inputs(self, zone: Dict, normalized_values: Dict) -> Dict:
        """Prepara los datos de entrada para trazabilidad"""
        original_metrics = zone.get('metrics', {})
        
        return {
            'original': {
                'zone_code': zone.get('zone_code'),
                'zone_name': zone.get('zone_name'),
                'region': zone.get('region'),
                'poblacion': original_metrics.get('poblacion'),
                'ingreso': original_metrics.get('ingreso'),
                'educacion': original_metrics.get('educacion'),
                'competencia': original_metrics.get('competencia')
            },
            'normalized': normalized_values
        }
    
    def _build_formula(self, normalized: Dict, weights: Dict, score: float) -> str:
        """Construye la fórmula aplicada para trazabilidad"""
        terms = []
        
        for var in ['poblacion', 'ingreso', 'educacion']:
            if var in weights and var in normalized:
                terms.append(f"({weights[var]} * {normalized[var]:.3f})")
        
        if 'competencia' in weights and 'competencia' in normalized:
            terms.append(f"- ({weights['competencia']} * {normalized['competencia']:.3f})")
        
        formula = " + ".join(terms)
        return f"Score = {formula} = {score:.3f}"
    
    def _calculate_ranking(self, scores: List[Dict]) -> List[Dict]:
        """Calcula las posiciones de ranking"""
        sorted_scores = sorted(scores, key=lambda x: x['score_value'], reverse=True)
        
        rankings = []
        for position, score_data in enumerate(sorted_scores, 1):
            rankings.append({
                'zone_code': score_data['zone_code'],
                'rank_position': position
            })
        
        return rankings
    
    def _merge_scores_with_rankings(self, scores: List[Dict], rankings: List[Dict]) -> List[Dict]:
        """Combina scores con posiciones de ranking"""
        rank_map = {r['zone_code']: r['rank_position'] for r in rankings}
        
        results = []
        for score in scores:
            results.append({
                'zone_code': score['zone_code'],
                'score_value': score['score_value'],
                'rank_position': rank_map.get(score['zone_code'], 0)
            })
        
        return sorted(results, key=lambda x: x['rank_position'])