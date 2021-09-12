from abc import ABC, abstractmethod
from typing import NoReturn


class Writer(ABC):
    def cleanup(self):
        pass

    @abstractmethod
    def write(self, data) -> NoReturn:
        pass
