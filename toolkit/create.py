from typing import Optional
from framework import Worker
from utils import generate_objects


def create(filename: Optional[str], in_dir: str, out_dir: Optional[str]):
    """
    Recreates the novel from the cleaned up data.
    """
    additional_args = {'in_dir': in_dir}
    if filename:
        additional_args['filename'] = filename
    if out_dir:
        additional_args['out_dir'] = out_dir
    objects = generate_objects('./config/create_config.json', 'create_config.json', in_dir, additional_args)
    worker = Worker(objects['readers'], [], objects['writers'])
    worker.work()
