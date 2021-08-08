from abc import ABC, abstractmethod

class Writer(ABC):
    def __init__(self, args):
        pass

    def before(self):
        pass

    def after(self):
        pass
    
    @abstractmethod
    def write(self, data):
        pass