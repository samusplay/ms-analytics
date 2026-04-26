# app/core/math_engine.py
"""
Motor Matemático de Scoring - Capa Core
Contiene la lógica matemática pura sin dependencias externas
"""

from typing import List, Tuple, Dict
from decimal import Decimal, ROUND_HALF_UP
import math


class MathEngine:
    """
    Motor matemático para cálculos de scoring
    Contiene funciones puras para normalización y cálculo de scores
    """
    
    @staticmethod
    def min_max_normalize(values: List[float]) -> List[float]:
        """
        Normalización Min-Max al rango [0, 1]
        
        Fórmula: x_norm = (x - min) / (max - min)
        
        Args:
            values: Lista de valores a normalizar
            
        Returns:
            Lista de valores normalizados
        """
        if not values:
            return []
        
        if len(values) == 1:
            return [0.5]
        
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return [0.5 for _ in values]
        
        return [(x - min_val) / (max_val - min_val) for x in values]
    
    @staticmethod
    def calculate_weighted_score(
        poblacion_norm: float,
        ingreso_norm: float,
        educacion_norm: float,
        competencia_norm: float,
        w_pob: float,
        w_ing: float,
        w_edu: float,
        w_comp: float
    ) -> float:
        """
        Calcula el score ponderado con penalización
        
        Fórmula: Score = (w_pob * pob) + (w_ing * ing) + (w_edu * edu) - (w_comp * comp)
        
        Args:
            poblacion_norm: Población normalizada [0, 1]
            ingreso_norm: Ingreso normalizado [0, 1]
            educacion_norm: Educación normalizada [0, 1]
            competencia_norm: Competencia normalizada [0, 1]
            w_pob: Peso de población
            w_ing: Peso de ingreso
            w_edu: Peso de educación
            w_comp: Peso de competencia
            
        Returns:
            Score calculado (entre 0 y 1)
        """
        # Validar valores normalizados
        for val, name in [
            (poblacion_norm, 'población'),
            (ingreso_norm, 'ingreso'),
            (educacion_norm, 'educación'),
            (competencia_norm, 'competencia')
        ]:
            if not (0 <= val <= 1):
                raise ValueError(f"❌ {name} no normalizada: {val}")
        
        # Cálculo con Decimal para precisión
        score = (Decimal(str(w_pob)) * Decimal(str(poblacion_norm)) +
                 Decimal(str(w_ing)) * Decimal(str(ingreso_norm)) +
                 Decimal(str(w_edu)) * Decimal(str(educacion_norm)) -
                 Decimal(str(w_comp)) * Decimal(str(competencia_norm)))
        
        # Clampear al rango [0, 1]
        score = max(Decimal('0'), min(Decimal('1'), score))
        
        # Redondear a 3 decimales
        score = score.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        
        return float(score)
    
    @staticmethod
    def calculate_ranking(scores: List[Tuple[str, float]]) -> List[Tuple[str, int]]:
        """
        Calcula el ranking basado en scores
        
        Args:
            scores: Lista de tuplas (zone_code, score_value)
            
        Returns:
            Lista de tuplas (zone_code, rank_position)
        """
        # Ordenar por score descendente
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        
        # Asignar posiciones
        rankings = []
        for position, (zone_code, _) in enumerate(sorted_scores, 1):
            rankings.append((zone_code, position))
        
        return rankings
    
    @staticmethod
    def calculate_percentile_rank(scores: List[float], target_score: float) -> float:
        """
        Calcula el rango percentil de un score
        
        Args:
            scores: Lista de todos los scores
            target_score: Score a evaluar
            
        Returns:
            Percentil (0-100)
        """
        if not scores:
            return 0.0
        
        count_less = sum(1 for s in scores if s < target_score)
        percentile = (count_less / len(scores)) * 100
        
        return round(percentile, 2)
    
    @staticmethod
    def calculate_statistics(scores: List[float]) -> Dict[str, float]:
        """
        Calcula estadísticas de los scores
        
        Args:
            scores: Lista de scores
            
        Returns:
            Diccionario con estadísticas
        """
        if not scores:
            return {
                'mean': 0, 'median': 0, 'std_dev': 0,
                'min': 0, 'max': 0, 'range': 0
            }
        
        n = len(scores)
        mean = sum(scores) / n
        sorted_scores = sorted(scores)
        
        # Mediana
        if n % 2 == 0:
            median = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        else:
            median = sorted_scores[n // 2]
        
        # Desviación estándar
        variance = sum((x - mean) ** 2 for x in scores) / n
        std_dev = math.sqrt(variance)
        
        return {
            'mean': round(mean, 3),
            'median': round(median, 3),
            'std_dev': round(std_dev, 3),
            'min': round(min(scores), 3),
            'max': round(max(scores), 3),
            'range': round(max(scores) - min(scores), 3)
        }