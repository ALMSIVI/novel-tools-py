from abc import ABC, abstractmethod

class Processor(ABC):
    def before(self):
        pass

    def after(self):
        pass

    @abstractmethod
    def process(self, data):
        pass