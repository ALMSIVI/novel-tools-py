from abc import ABC, abstractmethod


class Writer(ABC):
    @abstractmethod
    def accept(self, data) -> None:
        pass

    @abstractmethod
    def write(self) -> None:
        pass
