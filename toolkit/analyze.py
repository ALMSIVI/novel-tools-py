import os
from typing import Optional
from framework import Worker
from processors.matchers.__aggregate_matcher__ import AggregateMatcher
from utils import generate_objects


def analyze(filename: str, out_dir: Optional[str], config: str):
    """Analyzes the volume/chapter structure of the novel from a text file."""
    in_dir = os.path.dirname(filename)

    additional_args = {
        'text_filename': filename,
        'in_dir': in_dir,
        'out_dir': out_dir if out_dir is not None else in_dir
    }

    objects = generate_objects(config, os.path.join('config', 'analyze_config.json'), in_dir, additional_args)

    matcher = AggregateMatcher(objects['matchers'])
    processors = [matcher] + objects['validators'] + objects['transformers']

    worker = Worker(objects['readers'], processors, objects['writers'])
    worker.work()
