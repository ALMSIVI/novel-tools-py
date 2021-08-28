import os
from typing import Optional
from textwrap import dedent
from common import ACC
from utils import generate_classes
from .helpers import get_config, class_packages


def generate_docs(config_filename: Optional[str], doc_filename: Optional[str] = None):
    """
    Generates documentation for all specified ACCs.

    Args:
        config_filename: The config filename. If no full path is supplied, it wil use the current directory.
        doc_filename: The output doc filename. Default is 'docs.md' under the config's directory if config_filename is
                      specified, or the current directory if not.
    """
    config = get_config(os.curdir, config_filename) if config_filename is not None else {}
    class_dict = generate_classes(config, class_packages)

    if doc_filename is None:
        doc_filename = os.path.join(os.path.dirname(config_filename) if config_filename is not None else os.curdir,
                                    'docs.md')

    with open(doc_filename, 'wt') as f:
        for package_name, classes in class_dict.items():
            f.write(f'## {package_name}\n\n')
            for name, cls in classes.items():
                if ACC in cls.__bases__:
                    f.write(f'### {name}\n\n')
                    f.write('**Description:**\n')
                    f.write(dedent(cls.__doc__))
                    f.write('\n**Arguments:**\n')
                    f.write(cls.docstring())
                    f.write('\n\n')
