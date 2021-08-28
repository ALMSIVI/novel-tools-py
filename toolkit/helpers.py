import json
import os
from typing import Optional

default_packages = [{
    'name': '__default__',
    'list': [
        {'base': 'readers', 'ending': 'reader'},
        {'base': 'processors.matchers', 'ending': 'matcher'},
        {'base': 'processors.validators', 'ending': 'validator'},
        {'base': 'processors.transformers', 'ending': 'transformer'},
        {'base': 'writers', 'ending': 'writer'}
    ]
}]

class_packages = [
    {'name': 'Readers', 'list': [{'base': 'readers', 'ending': 'reader'}]},
    {'name': 'Matchers', 'list': [{'base': 'processors.matchers', 'ending': 'matcher'}]},
    {'name': 'Validators', 'list': [{'base': 'processors.validators', 'ending': 'validator'}]},
    {'name': 'Transformers', 'list': [{'base': 'processors.transformers', 'ending': 'transformer'}]},
    {'name': 'Writers', 'list': [{'base': 'writers', 'ending': 'writer'}]}
]


def get_config(in_dir: str, config_filename: str, default_config_filename: Optional[str] = None):
    filename = config_filename
    if not os.path.isfile(filename):
        filename = os.path.join(in_dir, config_filename)
    if not os.path.isfile(filename):
        if default_config_filename is None:
            raise ValueError('Config filename is invalid.')
        filename = os.path.join(os.curdir, default_config_filename)

    with open(filename, 'rt') as f:
        config = json.load(f)

    return config
