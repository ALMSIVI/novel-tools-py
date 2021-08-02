import csv, os
from volumes.volume_base import VolumeBase

class CsvVolume(VolumeBase):
    def filename(self):
        return os.path.join(self.dir, 'volumes.csv')

    def read(self):
        with open(self.filename(), 'rt') as f:
            reader = csv.DictReader(f)
            volumes = []
            for row in reader:
                volumes.append(row)

        return volumes

    def write(self, volumes):
        with open(self.filename(), 'wt') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'volume'])
            writer.writeheader()
            writer.writerows(volumes)