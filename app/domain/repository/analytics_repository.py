

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IAnalyticsRepository(ABC):
    #contrato para la persistencia de datos
    #garantizamos el dip
    @abstractmethod
    async def save_territorial_data_batch(self, dataset_id: str, records: List[Dict[str, Any]]) -> bool:
        pass

    # metodo para extarer la data haciendo uso del Dip
    @abstractmethod
    async def get_territorial_data(self, dataset_id: str) -> List[Dict[str, Any]]:
        pass

    #Metodo par trarse toda la info
    @abstractmethod
    async def get_territorial_data_with_metrics(
    self, dataset_id: str
    ) -> List[Dict[str, Any]]:
      pass
    #Traerse Resultados con el nombre
    @abstractmethod
    def get_results_with_names(self, execution_id: int) -> List[Dict[str, Any]]:
        """Contrato para obtener resultados cruzados con los nombres de las zonas"""
        pass