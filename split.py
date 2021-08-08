import argparse
import os
from framework import Worker
from processors.matchers.__aggregate_matcher__ import AggregateMatcher
from utils import generate_objects


def split(filename: str, out_dir: str):
    in_dir = os.path.dirname(filename)

    additional_args = {
        'filename': filename,
        'in_dir': in_dir
    }
    if out_dir:
        additional_args['out_dir'] = out_dir

    objects = generate_objects(in_dir, 'split_config.json', 'split_config.json', additional_args)

    matcher = AggregateMatcher(objects['matchers'])
    processors = [matcher] + objects['validators'] + objects['transformers']

    worker = Worker(objects['readers'], processors, objects['writers'])  # There is only one reader
    worker.work()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split ebook file into individual chapters.')
    parser.add_argument('-t', '--tool', default='list_generator',
                        help='Select which tool you want to use. Default is to generate a csv file.')
    parser.add_argument('-f', '--filename', help='Filename of the book file.')
    parser.add_argument('-o', '--out_dir', default=None, help='Directory of the output files.')

    args = parser.parse_args()
    split(args.filename, args.out_dir)
