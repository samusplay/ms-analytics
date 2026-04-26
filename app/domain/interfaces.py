# domain/interfaces.py
from abc import ABC, abstractmethod

class IConfigClient(ABC):
    @abstractmethod
    def get_active_configuration(self): pass


class IScoreRepository(ABC):
    @abstractmethod
    def save_execution(self, execution): pass

    @abstractmethod
    def save_zone_scores(self, scores): pass


class ITraceRepository(ABC):
    @abstractmethod
    def save_trace(self, trace): pass


class IScoringStrategy(ABC):
    @abstractmethod
    def calculate(self, data, config): pass