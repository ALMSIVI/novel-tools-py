from abc import ABC, abstractmethod

class Reader(ABC):
    def __init__(self, args):
        pass

    def before(self):
        pass

    def after(self):
        pass

    @abstractmethod
    def read(self):
        pass