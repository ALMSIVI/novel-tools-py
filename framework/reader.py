from abc import ABC, abstractmethod
from typing import Iterator


class Reader(ABC):
    @abstractmethod
    def read(self) -> Iterator:
        pass
