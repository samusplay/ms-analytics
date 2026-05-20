from typing import Any, Dict

from app.domain.config_provider_interface import IConfigProvider
from app.domain.repository.analytics_repository import IAnalyticsRepository


class AnalyticsPipelineService:
    def __init__(
            self,
            repository:IAnalyticsRepository,
            config_provider:IConfigProvider
    ):
        self.repository=repository
        self.config_provider=config_provider
    async def execute_fetch_pipeline(self, dataset_id: str) -> Dict[str, Any]:
        #Orquesta la obtenecion de datos del ms-configuration

        #Pedimos los datos por el puerto
        active_weights = self.config_provider.get_active_weights()

        #obtenemos los datos locales
        raw_data=await self.repository.get_territorial_data(dataset_id)

        #Objeto de de Retorno del Pipline
        return{
            "dataset_id": dataset_id,
            "configuration": {
                "active_weights": active_weights,
                "status": "synchronized"
            },
            "data": {
                "record_count": len(raw_data),
                "payload": raw_data
            }
        }