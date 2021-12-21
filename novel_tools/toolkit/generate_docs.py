from pathlib import Path
from typing import Optional
from novel_tools.common import ACC
from novel_tools.utils import get_config, class_packages, generate_classes, format_text


def docgen(config_filename: Optional[str], doc_filename: Optional[str] = None):
    """
    Generates documentation for all specified ACCs.

    Args:
        config_filename: The config filename. If no full path is supplied, it wil use the current directory.
        doc_filename: The output doc filename. Default is 'docs.md' under the config's directory if config_filename is
                      specified, or the current directory if not.
    """
    config = get_config(config_filename, Path()) if config_filename is not None else {}
    class_dict = generate_classes(config, class_packages)

    if doc_filename is None:
        doc_filename = (Path(config_filename).parent if config_filename is not None else Path()) / 'docs.md'
    else:
        doc_filename = Path(doc_filename)

    with doc_filename.open('wt') as f:
        for package_name, classes in class_dict.items():
            f.write(f'## {package_name}\n\n')
            for name, cls in classes.items():
                if ACC in cls.__mro__:
                    f.write(f'### {name}\n\n')
                    f.write('**Description:**\n\n')
                    if cls.__doc__ is not None:
                        f.write(format_text(cls.__doc__))
                        f.write('\n')
                    docstring = cls.docstring()
                    if docstring != '':
                        f.write('\n**Arguments:**\n\n')
                        f.write(cls.docstring())
                        f.write('\n')
                    f.write('\n')
