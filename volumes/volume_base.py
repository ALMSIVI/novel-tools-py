from abc import ABC, abstractmethod
import os

class VolumeBase(ABC):
    def __init__(self, dir):
        self.dir = dir

    def exists(self):
        return os.path.isfile(self.filename)

    @abstractmethod
    def filename(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, volumes):
        pass