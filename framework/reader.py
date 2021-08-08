from abc import ABC, abstractmethod


class Reader(ABC):
    def before(self):
        pass

    def after(self):
        pass

    @abstractmethod
    def read(self):
        pass
