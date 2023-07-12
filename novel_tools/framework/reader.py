from abc import ABC, abstractmethod
from typing import Iterator
from .data import NovelData


class Reader(ABC):
    @abstractmethod
    def read(self) -> Iterator[NovelData]:
        pass
