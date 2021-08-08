import os
from framework import Worker
from utils import generate_objects
from .matchers.__aggregate_matcher__ import __AggregateMatcher__

def split(filename: str, out_dir: str):
    in_dir = os.path.dirname(filename)

    additional_args = {
        'filename': filename,
        'in_dir': in_dir
    }
    if out_dir:
        additional_args['out_dir'] = out_dir

    objects = generate_objects(in_dir, 'split_config.json', 'split_config.json', additional_args)

    matcher = __AggregateMatcher__(objects['matchers'])
    validators = objects['validators']
    processors = [matcher] + validators

    worker = Worker(objects['readers'][0], processors, objects['writers']) # There is only one reader
    worker.work()