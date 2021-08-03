from utils import ClassFactory
from .volume_base import VolumeBase

def get_volumes():
    '''
    Gets a list of volume classes.
    '''
    factory = ClassFactory('volumes', '_volume')
    return list(factory.classes.values())


def read_volumes(dir: str):
    for volume_class in get_volumes():
        volume_obj: VolumeBase = volume_class(dir)
        if volume_obj.exists():
            return volume_obj.read()