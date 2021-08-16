import argparse
import os
from typing import Optional

from framework import Worker
from utils import generate_objects


def create(filename: Optional[str], in_dir: str, out_dir: str):
    """
    Recreates the novel from the cleaned up data.
    """
    additional_args = {'in_dir': in_dir}
    if filename:
        additional_args['filename'] = filename
    if out_dir:
        additional_args['out_dir'] = out_dir
    objects = generate_objects('create_config.json', 'create_config.json', in_dir, additional_args)
    worker = Worker(objects['readers'], [], objects['writers'])
    worker.work()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recreates the novel from the cleaned up data.')
    parser.add_argument('-f', '--filename', help='Directory or filename of the novel.')
    parser.add_argument('-o', '--out_dir', default=None, help='Directory of the output file.')

    args = parser.parse_args()
    if os.path.isdir(args.filename):
        create(None, args.filename, args.out_dir)
    else:
        create(args.filename, os.path.dirname(args.filename), args.out_dir)
