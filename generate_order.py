from natsort import natsorted
import os
import json
import argparse


# Some novels might have irregular volume names. To properly sort these volumes, a custom file called order.json will be used.
# This file will generate a template of this file. Once generated, manually sort them to the desired order.
# concatenate_volume.py will then detect this json and sort the volumes as specified.
if __name__ == '__main__':
    default_dir = os.curdir

    parser = argparse.ArgumentParser(description = 'Generate a custom order file for volume sorting.')
    parser.add_argument('-i', '--indir',  default = default_dir, help = 'Parent directory for all the volumes..')

    args = parser.parse_args()
    

    with open('order.json', 'wt') as f:
        json.dump([{'name': name, 'volume': name} for name in natsorted(os.listdir(args.indir)) if os.path.isdir(name)], f, indent = 2, ensure_ascii = False)