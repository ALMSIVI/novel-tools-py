import os
from typing import Optional
from framework import Worker
from processors.matchers.__aggregate_matcher__ import AggregateMatcher
from utils import generate_objects
from .helpers import get_config, default_packages


def analyze(filename: str, out_dir: Optional[str], config_filename: str):
    """
    Analyzes the volume/chapter structure of the novel from a text file.

    Args:
        filename: The novel's filename, including the full path. It will be supplied as an input to TextReader.
        out_dir: The output directory. Defaults to the same directory as the novel file.
        config_filename: The config filename. If no full path is supplied, it will use the novel file's path.
    """
    in_dir = os.path.dirname(filename)

    additional_args = {
        'text_filename': filename,
        'in_dir': in_dir,
        'out_dir': out_dir or in_dir
    }

    config_filename = get_config(in_dir, config_filename, os.path.join('config', 'analyze_config.json'))
    objects = generate_objects(config_filename, default_packages, additional_args)

    matcher = AggregateMatcher(objects['matchers'])
    processors = [matcher] + objects['validators'] + objects['transformers']

    worker = Worker(objects['readers'], processors, objects['writers'])
    worker.work()
