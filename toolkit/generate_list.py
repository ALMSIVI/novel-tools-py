import os
from typing import Optional
from framework import Worker
from utils import generate_objects
from .helpers import get_config, default_package


def generate_list(in_dir: str, out_dir: Optional[str], config_filename: str):
    """
    Generates a list from the given directory.
    Usually, after analyzing the novel and splitting it into individual chapter files, one would manually inspect the
    files and make necessary modifications. This process might change the novel structure, and the original list/toc
    files might no longer apply. Therefore, one would need to recreate the list from the directory.

    Args:
        in_dir: The input directory holding the novel files.
        out_dir: The output directory. Defaults to in_dir.
        config_filename: The config filename. If no full path is supplied, it wil use in_dir.
    """
    additional_args = {'in_dir': in_dir}
    if out_dir:
        additional_args['out_dir'] = out_dir

    config = get_config(in_dir, config_filename, os.path.join('config', 'list_config.json'))
    objects = generate_objects(config, default_package, additional_args)
    worker = Worker(objects['readers'], [], objects['writers'])
    worker.work()
