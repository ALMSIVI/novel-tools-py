import json
import os
from importlib import import_module


def snake_to_pascal(s: str):
    return s.replace('_', ' ').title().replace(' ', '')


def import_class(filename: str, base_package: str):
    return getattr(import_module(f'{base_package}.{filename}'), snake_to_pascal(filename))


def import_function(filename: str, base_package: str, func_name: str):
    return getattr(import_module(f'{base_package}.{filename}'), func_name)


class ClassFactory:
    def __init__(self, packages):
        self.classes = {}

        if type(packages) is dict:
            packages = [packages]

        for package in packages:
            self.add_package(package['base'], package['ending'])

    def add_package(self, base: str, ending: str):
        module_dir = os.path.join('..', *base.split('.'))
        module_names = [filename[:-3] for filename in os.listdir(module_dir) if filename.endswith(f'{ending}.py')]
        for module in module_names:
            name = snake_to_pascal(module)
            self.classes[name] = import_class(module, base)

    def get(self, name, args):
        return self.classes[name](args)


def generate_objects(config_filename: str, default_config_filename: str, in_dir: str, additional_args=None):
    """Generates corresponding objects from the config file."""
    if additional_args is None:
        additional_args = {}
    filename = os.path.join(in_dir, config_filename)
    if not os.path.isfile(filename):
        filename = os.path.join(os.curdir, default_config_filename)

    with open(filename, 'rt') as f:
        config = json.load(f)

    factories = {}
    for factory_config in config['packages']:
        factories[factory_config['name']] = ClassFactory(factory_config['list'])

    objects = {}
    for key, object_configs in config['objects'].items():
        if type(object_configs) is dict:
            object_config = object_configs
            factory_name = object_config.get('name', config['default_package'])
            objects[key] = factories[factory_name].get(object_config['class'], object_config | additional_args)
        else:
            object_list = []
            for object_config in object_configs:
                factory_name = object_config.get('name', config['default_package'])
                object_list.append(factories[factory_name].get(object_config['class'], object_config | additional_args))

            objects[key] = object_list

    return objects
