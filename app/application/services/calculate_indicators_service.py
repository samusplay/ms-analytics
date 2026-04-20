from typing import Any, Dict

from app.application.strategies.kpi_strategies import IKpiStrategy
from app.domain.repository.analytics_repository import IAnalyticsRepository


class CalculateIndicatorsService:
    """
    CASO DE USO: Orquesta la extracción de datos y el cálculo de KPIs.
    Ahora cumple 100% con Inversión de Dependencias (DIP).
    """

    def __init__(self, repository: IAnalyticsRepository, strategies: Dict[str, IKpiStrategy]):
        #recibimos desde afuera
        self.repository = repository
        self.strategies = strategies

    async def execute(self, dataset_id: str) -> Dict[str, Any]:
        """Ejecuta todos los cálculos y retorna el JSON final"""
        
        data = await self.repository.get_territorial_data(dataset_id)
        
        if not data:
            raise ValueError(f"No hay datos sincronizados para el dataset {dataset_id}")

        resultados = {}
        for kpi_name, strategy in self.strategies.items():
            resultados[kpi_name] = strategy.calculate(data)
            
        return resultados