

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IAnalyticsRepository(ABC):
    #contrato para la persistencia de datos
    #garantizamos el dip
    @abstractmethod
    async def save_territorial_data_batch(self, dataset_id: str, records: List[Dict[str, Any]]) -> bool:
        pass