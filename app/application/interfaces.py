# app/application/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session


class INormalizer(ABC):
    @abstractmethod
    def normalize(self, values: List[float]) -> List[float]:
        pass
    
    @abstractmethod
    def normalize_single(self, value: float, min_val: float, max_val: float) -> float:
        pass
    
    @abstractmethod
    def normalize_metrics(self, metrics: Dict[str, List[float]]) -> Dict[str, List[float]]:
        pass


class IScoringStrategy(ABC):
    @abstractmethod
    def calculate(self, normalized_values: Dict[str, float], weights: Dict[str, float]) -> float:
        pass


class IConfigClient(ABC):
    @abstractmethod
    def get_weights(self) -> Dict[str, float]:
        pass
    
    @abstractmethod
    def get_active_configuration(self) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        pass


class IScoreRepository(ABC):
    @abstractmethod
    def save_execution(self, db: Session, dataset_id: str, config_id: int) -> int:
        pass
    
    @abstractmethod
    def save_zone_scores(self, db: Session, execution_id: int, scores: List[Dict]) -> None:
        pass
    
    @abstractmethod
    def update_ranking(self, db: Session, execution_id: int, rankings: List[Dict]) -> None:
        pass


class ITraceRepository(ABC):
    @abstractmethod
    def save_trace(self, db: Session, execution_id: int, zone_code: str,
                   inputs: Dict, weights: Dict, formula: str) -> None:
        pass