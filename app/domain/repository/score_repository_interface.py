from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IScoreRepository(ABC):

    @abstractmethod
    def save_execution(
        self,
        dataset_id: str,
        configuration_id: int,
    ) -> Any:
        pass

    @abstractmethod
    def save_zone_scores(
        self,
        execution_id: int,
        scored_zones: List[Dict[str, Any]],
    ) -> List[Any]:
        pass

    @abstractmethod
    def save_trace(
        self,
        execution_id: int,
        zone_score_id: int,
        zone_code: str,
        inputs: Dict,
        weights: Dict,
        formula: str,
    ) -> Any:
        pass

    @abstractmethod
    def get_results(
        self,
        execution_id: int,
    ) -> List[Any]:
        pass

    @abstractmethod
    def get_trace(
        self,
        execution_id: int,
        zone_code: str,
    ) -> Any:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def get_last_execution_by_dataset(
    self,
    dataset_id: str,
    ) -> Any:
        pass

    @abstractmethod
    def get_results_with_names(
    self,
    execution_id: int,
    ) -> List[dict]:
        pass

    