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
        module_dir = os.path.join(os.curdir, *base.split('.'))
        module_names = [filename[:-3] for filename in os.listdir(module_dir) if filename.endswith(f'{ending}.py')]
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
    packages = [] if default_package is None else [default_package]
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
    packages = [] if default_package is None else [default_package]
    packages += config.get('packages', [])
    for factory_config in packages:
        classes[factory_config['name']] = ClassFactory(factory_config['list']).classes

    return classes
