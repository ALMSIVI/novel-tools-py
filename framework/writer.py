from abc import ABC, abstractmethod

class Writer(ABC):
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
    def write(self, data):
        pass