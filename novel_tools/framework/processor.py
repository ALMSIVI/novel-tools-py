from abc import ABC, abstractmethod
from .data import NovelData


class Processor(ABC):
    @abstractmethod
    def process(self, data: NovelData) -> NovelData:
        pass
