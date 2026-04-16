

from typing import Any, Dict, List

from app.domain.repository.analytics_repository import IAnalyticsRepository


class SyncAnalyticsDataService:

#inyeccion del repo
    def __init__(self,repository:IAnalyticsRepository):
        self.repository=repository
    
    async def execute(self, dataset_id: str, records: List[Dict[str, Any]]) -> dict:
        #ejecutamos reglas de negocio
        if not records:
            raise ValueError("El lote de datos recibido está vacío. No hay nada que sincronizar.")
        
        #delegamos la persistencia de la infrastructura
        success = await self.repository.save_territorial_data_batch(dataset_id, records)

        #si fallo
        if not success:
            raise RuntimeError("Fallo interno al intentar guardar los datos en db_analytics.")
        
        #Retornamos un resumen
        return {
            "dataset_id": dataset_id,
            "records_processed": len(records),
            "status": "synchronized"
        }
