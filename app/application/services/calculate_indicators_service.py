from typing import Any, Dict

import asyncio
from app.application.strategies.kpi_strategies import IKpiStrategy
from app.domain.repository.analytics_repository import IAnalyticsRepository
from app.domain.repository.audit_client_port import AuditClientPort


class CalculateIndicatorsService:
    """
    CASO DE USO: Orquesta la extracción de datos y el cálculo de KPIs.
    Ahora cumple 100% con Inversión de Dependencias (DIP).
    """

    def __init__(
        self, 
        repository: IAnalyticsRepository, 
        strategies: Dict[str, IKpiStrategy],
        audit_client: AuditClientPort = None
    ):
        #recibimos desde afuera
        self.repository = repository
        self.strategies = strategies
        self.audit_client = audit_client

    async def execute(self, dataset_id: str, trace_id: str = None) -> Dict[str, Any]:
        """Ejecuta todos los cálculos y retorna el JSON final"""
        
        try:
            data = await self.repository.get_territorial_data(dataset_id)
            
            if not data:
                raise ValueError(f"No hay datos sincronizados para el dataset {dataset_id}")

            resultados = {}
            for kpi_name, strategy in self.strategies.items():
                resultados[kpi_name] = strategy.calculate(data)
                
            if self.audit_client:
                asyncio.create_task(
                    self.audit_client.send_operation_event(
                        status="EXITOSO",
                        summary=f"Cálculo de indicadores finalizado para el dataset {dataset_id}"
                    )
                )
                
            return resultados
        except Exception as e:
            if self.audit_client:
                asyncio.create_task(
                    self.audit_client.send_operation_event(
                        status="FALLIDO",
                        summary=f"Fallo en cálculo de indicadores para dataset {dataset_id}: {str(e)}"
                    )
                )
            raise e