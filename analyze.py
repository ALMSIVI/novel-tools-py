import argparse
import os
from framework import Worker
from processors.matchers.__aggregate_matcher__ import AggregateMatcher
from utils import generate_objects


def analyze(filename: str, out_dir: str):
    """Analyzes the volume/chapter structure of the novel."""
    in_dir = os.path.dirname(filename)

    additional_args = {
        'filename': filename,
        'in_dir': in_dir
    }
    if out_dir:
        additional_args['out_dir'] = out_dir

    objects = generate_objects('analyze_config.json', 'analyze_config.json', in_dir, additional_args)

    matcher = AggregateMatcher(objects['matchers'])
    processors = [matcher] + objects['validators'] + objects['transformers']

    worker = Worker(objects['readers'], processors, objects['writers'])  # There is only one reader
    worker.work()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyzes the volume/chapter structure of the novel.')
    parser.add_argument('-f', '--filename', help='Filename of the book file.')
    parser.add_argument('-o', '--out_dir', default=None, help='Directory of the output file(s).')

    args = parser.parse_args()
    analyze(args.filename, args.out_dir)
