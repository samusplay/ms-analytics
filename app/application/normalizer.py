# app/application/normalizer.py
from typing import List, Dict
from app.application.interfaces import INormalizer


class MinMaxNormalizer(INormalizer):
    """
    Normalizador Min-Max - SRP: Solo se encarga de normalizar datos
    LSP: Puede ser sustituido por cualquier otro normalizador
    """
    
    def __init__(self, epsilon: float = 1e-10):
        self.epsilon = epsilon
    
    def normalize(self, values: List[float]) -> List[float]:
        """Normaliza una lista completa de valores al rango [0, 1]"""
        if not values:
            return []
        
        if len(values) == 1:
            return [0.5]
        
        min_val = min(values)
        max_val = max(values)
        
        if abs(max_val - min_val) < self.epsilon:
            return [0.5 for _ in values]
        
        normalized = [(v - min_val) / (max_val - min_val) for v in values]
        
        # Asegurar rango [0, 1]
        return [max(0.0, min(1.0, n)) for n in normalized]
    
    def normalize_single(self, value: float, min_val: float, max_val: float) -> float:
        """Normaliza un valor individual"""
        if abs(max_val - min_val) < self.epsilon:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    def normalize_metrics(self, metrics: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """Normaliza todas las métricas de todas las zonas"""
        normalized = {}
        
        for metric_name, values in metrics.items():
            normalized[metric_name] = self.normalize(values)
            if values:
                print(f"📊 Normalizando {metric_name}: min={min(values):.2f}, max={max(values):.2f}")
        
        return normalized


class ZScoreNormalizer(INormalizer):
    """
    Normalizador Z-Score - Centra los datos en media 0 y desviación 1
    Implementación alternativa - OCP: extensión sin modificar código existente
    """
    
    def __init__(self, epsilon: float = 1e-10):
        self.epsilon = epsilon
    
    def normalize(self, values: List[float]) -> List[float]:
        if not values:
            return []
        
        if len(values) == 1:
            return [0.5]
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        if std_dev < self.epsilon:
            return [0.5 for _ in values]
        
        # Z-Score
        normalized = [(x - mean) / std_dev for x in values]
        
        # Mapear a [0, 1] usando sigmoide
        import math
        normalized = [1 / (1 + math.exp(-n)) for n in normalized]
        
        return normalized
    
    def normalize_single(self, value: float, min_val: float, max_val: float) -> float:
        # Para Z-Score, necesitamos la media y desviación del conjunto
        # Este método no es adecuado para Z-Score
        raise NotImplementedError("normalize_single no implementado para Z-Score")
    
    def normalize_metrics(self, metrics: Dict[str, List[float]]) -> Dict[str, List[float]]:
        normalized = {}
        for metric_name, values in metrics.items():
            normalized[metric_name] = self.normalize(values)
        return normalized