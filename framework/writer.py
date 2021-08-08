from abc import ABC, abstractmethod


class Writer(ABC):
    def cleanup(self):
        pass

    @abstractmethod
    def write(self, data):
        pass
