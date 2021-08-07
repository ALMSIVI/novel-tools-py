from abc import ABC, abstractmethod

class Reader(ABC):
    @abstractmethod
    def __init__(self, args):
        pass

    @abstractmethod
    def before(self):
        pass

    @abstractmethod
    def after(self):
        pass

    @abstractmethod
    def read(self):
        pass