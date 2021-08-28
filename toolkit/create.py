import os
from typing import Optional
from framework import Worker
from utils import generate_objects
from .helpers import get_config, default_package


def create(filename: Optional[str], in_dir: str, out_dir: Optional[str], config_filename: str):
    """
    Recreates the novel from the cleaned up data.

    Arguments:
        filename: The novel's filename, which doesn't need to include the full path. Required if using a Reader that
                  involves a text file.
        in_dir: The input directory holding the novel and structure files.
        out_dir: THe output directory. Defaults to in_dir.
        config_filename: The config filename. If no full path is supplied, it wil use in_dir.
    """
    additional_args = {'in_dir': in_dir}
    if filename:
        additional_args['filename'] = filename
    if out_dir:
        additional_args['out_dir'] = out_dir

    config = get_config(in_dir, config_filename, os.path.join('config', 'create_config.json'))
    objects = generate_objects(config, default_package, additional_args)
    worker = Worker(objects['readers'], [], objects['writers'])
    worker.work()
