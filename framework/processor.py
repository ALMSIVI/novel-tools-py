from abc import ABC, abstractmethod


class Processor(ABC):
    def cleanup(self):
        pass

    @abstractmethod
    def process(self, data):
        pass
