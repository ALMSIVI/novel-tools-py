import os
from natsort import natsorted

def read(dir: str):
    return [{'name': name, 'volume': name} for name in natsorted(os.listdir(dir)) if os.path.isdir(os.path.join(dir, name))]