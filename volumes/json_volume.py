import json, os
from .volume_base import VolumeBase

class JsonVolume(VolumeBase):
    def filename(self):
        return os.path.join(self.dir, 'volumes.json')

    def read(self):
        with open(self.filename(), 'rt') as f:
            return json.load(f)

    def write(self, volumes):
        with open(self.filename(), 'wt') as f:
            json.dump(volumes, f, indent=2, ensure_ascii=False)