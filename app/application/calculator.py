# app/application/calculator.py
from typing import Dict, List
from decimal import Decimal
from app.application.interfaces import IScoringStrategy


class WeightedScoringStrategy(IScoringStrategy):
    """
    Estrategia de scoring ponderado - SRP: Solo calcula scores
    OCP: Se pueden agregar nuevas estrategias sin modificar código existente
    """
    
    def __init__(self, decimal_places: int = 3):
        self.decimal_places = decimal_places
        self.positive_vars = ['poblacion', 'ingreso', 'educacion']
        self.penalty_vars = ['competencia']
    
    def calculate(self, normalized_values: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calcula el score con penalización
        
        Fórmula: Score = (w1*pob) + (w2*ing) + (w3*edu) - (w4*comp)
        
        CA2: Asegura que exista penalización (resta)
        """
        # Validar valores normalizados
        for var, value in normalized_values.items():
            if value < 0 or value > 1:
                raise ValueError(f"Variable '{var}' no normalizada: {value}")
        
        # Suma de términos positivos
        positive_sum = Decimal('0')
        for var in self.positive_vars:
            if var in normalized_values and var in weights:
                positive_sum += Decimal(str(weights[var])) * Decimal(str(normalized_values[var]))
        
        # Penalización (resta)
        penalty = Decimal('0')
        for var in self.penalty_vars:
            if var in normalized_values and var in weights:
                penalty += Decimal(str(weights[var])) * Decimal(str(normalized_values[var]))
        
        # Score final
        score = float(positive_sum - penalty)
        
        # Clampear al rango [0, 1]
        score = max(0.0, min(1.0, score))
        
        return round(score, self.decimal_places)


class ExponentialScoringStrategy(IScoringStrategy):
    """
    Estrategia exponencial - OCP: Nueva estrategia sin modificar el código base
    """
    
    def __init__(self, exponent: float = 1.5):
        self.exponent = exponent
    
    def calculate(self, normalized_values: Dict[str, float], weights: Dict[str, float]) -> float:
        score = 0.0
        
        for var, weight in weights.items():
            value = normalized_values.get(var, 0)
            if var == 'competencia':
                score -= weight * (value ** self.exponent)
            else:
                score += weight * (value ** self.exponent)
        
        return max(0.0, min(1.0, score))