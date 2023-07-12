from abc import ABC, abstractmethod
from .data import NovelData


class Writer(ABC):
    @abstractmethod
    def accept(self, data: NovelData) -> None:
        pass

    @abstractmethod
    def write(self) -> None:
        pass
