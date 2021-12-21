import json
from importlib import import_module
from pathlib import Path
from typing import Optional


def snake_to_pascal(s: str):
    return s.replace('_', ' ').title().replace(' ', '')


def import_class(filename: str, base_package: str):
    return getattr(import_module(f'novel_tools.{base_package}.{filename}'), snake_to_pascal(filename))


def import_function(filename: str, base_package: str, func_name: str):
    return getattr(import_module(f'novel_tools.{base_package}.{filename}'), func_name)


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


def get_config(config_filename: str, in_dir: Optional[Path] = None):
    path = Path(config_filename)

    if not path.is_file():
        path = in_dir / config_filename
    if not path.is_file():
        path = Path('config', config_filename)

    with path.open('rt') as f:
        config = json.load(f)

    return config


class ClassFactory:
    def __init__(self, packages):
        self.classes = {}

        if type(packages) is dict:
            packages = [packages]

        for package in packages:
            self.add_package(package['base'], package['ending'])

    def add_package(self, base: str, ending: str):
        module_dir = Path('novel_tools', *base.split('.'))
        module_names = [path.stem for path in module_dir.iterdir() if str(path).endswith(f'{ending}.py')]
        for module in module_names:
            name = snake_to_pascal(module)
            self.classes[name] = import_class(module, base)

    def get(self, name, args):
        return self.classes[name](args)


def generate_objects(config: dict, default_package=None, additional_args=None):
    """Generates corresponding objects from the config."""
    if additional_args is None:
        additional_args = {}

    factories = {}
    packages = [] if default_package is None else default_package
    packages += config.get('packages', [])
    for factory_config in packages:
        factories[factory_config['name']] = ClassFactory(factory_config['list'])

    objects = {}
    for key, object_configs in config['objects'].items():
        if type(object_configs) is dict:
            object_config = object_configs
            factory_name = object_config.get('name', '__default__')
            objects[key] = factories[factory_name].get(object_config['class'], object_config | additional_args)
        else:
            object_list = []
            for object_config in object_configs:
                factory_name = object_config.get('name', '__default__')
                object_list.append(factories[factory_name].get(object_config['class'], object_config | additional_args))

            objects[key] = object_list

    return objects


def generate_classes(config: dict, default_package=None):
    """Generates corresponding classes from the config. Useful for extracting required fields."""

    classes = {}
    packages = [] if default_package is None else default_package
    packages += config.get('packages', [])
    for factory_config in packages:
        classes[factory_config['name']] = ClassFactory(factory_config['list']).classes

    return classes
