import argparse
from utils import import_function, import_class
from volumes import VolumeBase

# Some novels might have irregular volume names. To properly recognize and/or sort these volumes, a custom file will be used.
# This file will generate a template of this file. Once generated, manually sort them to the desired order.
# When this volume file is present, split.py will automatically match the specified volumes, and concatenate.py will follow the order in the file.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a custom order file for volume sorting.')
    parser.add_argument('-d', '--dir',  required=True, help='Parent directory for all the volumes.')
    parser.add_argument('-r', '--reader', default='list', help='Select the mode of volume collection: from volume directories or from csv list.')
    parser.add_argument('-w', '--writer', default='csv', help='Format of the volume order file.')

    args = parser.parse_args()
    
    read = import_function(f'{args.reader}_reader', 'volumes', 'read')
    volumes = read(args.dir)
    
    volume_class = import_class(f'{args.writer}_volume', 'volumes')
    writer: VolumeBase = volume_class(args.dir)
    writer.write(volumes)
