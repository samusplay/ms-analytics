from abc import ABC, abstractmethod
from typing import Dict


#Puerto para obtener la configuracion
class IConfigProvider(ABC):

    @abstractmethod
    #Retorna un diccionario con los pesos activos del ms-configuration
    def get_active_weights(self) -> Dict[str, float]:
        pass