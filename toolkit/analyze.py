import os
from typing import Optional
from framework import Worker
from processors.matchers.__aggregate_matcher__ import AggregateMatcher
from utils import generate_objects


def analyze(filename: str, out_dir: Optional[str]):
    """Analyzes the volume/chapter structure of the novel."""
    in_dir = os.path.dirname(filename)

    additional_args = {
        'text_filename': filename,
        'in_dir': in_dir
    }
    if out_dir:
        additional_args['out_dir'] = out_dir

    objects = generate_objects('./config/analyze_config.json', 'analyze_config.json', in_dir, additional_args)

    matcher = AggregateMatcher(objects['matchers'])
    processors = [matcher] + objects['validators'] + objects['transformers']

    worker = Worker(objects['readers'], processors, objects['writers'])
    worker.work()
