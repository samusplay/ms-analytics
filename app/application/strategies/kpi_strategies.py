from abc import ABC, abstractmethod
from collections import Counter
from typing import Any, Dict, List


# 1. LA INTERFAZ (El molde de la estrategia)
class IKpiStrategy(ABC):
    """Interfaz para calcular cualquier KPI. (Patrón Strategy)"""
    @abstractmethod
    def calculate(self, data: List[Dict[str, Any]]) -> Any:
        pass

# 2. LAS IMPLEMENTACIONES CONCRETAS (Una clase por cada cálculo)

class TotalVolumeStrategy(IKpiStrategy):
    """Calcula el conteo total de filas (Volumen Total)"""
    def calculate(self, data: List[Dict[str, Any]]) -> int:
        return len(data)

class CoverageStrategy(IKpiStrategy):
    """Calcula la cantidad de zonas únicas (Cobertura Territorial)"""
    def calculate(self, data: List[Dict[str, Any]]) -> int:
        if not data: return 0
        zonas_unicas = set(fila.get("zone_name", "UNKNOWN") for fila in data)
        return len(zonas_unicas)

class TopZoneStrategy(IKpiStrategy):
    """Encuentra la zona con mayor concentración (Top Zona)"""
    def calculate(self, data: List[Dict[str, Any]]) -> str:
        if not data: return "N/A"
        zonas = [fila.get("zone_name", "UNKNOWN") for fila in data]
        contador = Counter(zonas)
        zona_top = contador.most_common(1)[0][0] # Limit 1
        return zona_top

class DensityStrategy(IKpiStrategy):
    """Calcula el promedio de registros por zona (Densidad Promedio)"""
    def calculate(self, data: List[Dict[str, Any]]) -> float:
        if not data: return 0.0
        
        volumen = len(data)
        zonas_unicas = len(set(fila.get("zone_name", "UNKNOWN") for fila in data))
        
        if zonas_unicas == 0: return 0.0
        
        return round(volumen / zonas_unicas, 2)