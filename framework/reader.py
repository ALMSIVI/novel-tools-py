from abc import ABC, abstractmethod


class Reader(ABC):
    def cleanup(self):
        pass

    @abstractmethod
    def read(self):
        pass
