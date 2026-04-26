# app/application/penalization.py
from typing import Dict
from app.application.interfaces import IPenalizationStrategy

class LinearPenalizationStrategy(IPenalizationStrategy):
    """
    Penalización lineal - La penalización es proporcional al factor
    """
    
    def apply_penalty(self, base_score: float, penalty_factors: Dict[str, float]) -> float:
        """
        Aplica penalización lineal
        
        Args:
            base_score: Score base
            penalty_factors: Factores de penalización (ej: {'competencia': 0.3})
            
        Returns:
            Score penalizado
        """
        total_penalty = sum(penalty_factors.values())
        penalty = base_score * total_penalty
        return max(0.0, base_score - penalty)


class ExponentialPenalizationStrategy(IPenalizationStrategy):
    """
    Penalización exponencial - Penaliza más fuerte valores altos
    """
    
    def __init__(self, exponent: float = 2.0):
        self.exponent = exponent
    
    def apply_penalty(self, base_score: float, penalty_factors: Dict[str, float]) -> float:
        total_penalty = sum(p ** self.exponent for p in penalty_factors.values())
        penalty = base_score * min(1.0, total_penalty)
        return max(0.0, base_score - penalty)


class ThresholdPenalizationStrategy(IPenalizationStrategy):
    """
    Penalización por umbral - Solo penaliza si supera cierto límite
    """
    
    def __init__(self, threshold: float = 0.5, penalty_rate: float = 0.3):
        self.threshold = threshold
        self.penalty_rate = penalty_rate
    
    def apply_penalty(self, base_score: float, penalty_factors: Dict[str, float]) -> float:
        penalty = 0
        for factor in penalty_factors.values():
            if factor > self.threshold:
                penalty += (factor - self.threshold) * self.penalty_rate
        
        return max(0.0, base_score - penalty)