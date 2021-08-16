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
        module_dir = os.path.join('.', *base.split('.'))
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
    if not os.path.exists(filename):
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


num_dict = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
            "十": 10, "廿": 20, "卅": 30, "卌": 40, "百": 100, "千": 1000}


def to_num(num: str) -> int:
    """
    Converts a chinese string to a number.
    """
    num = num.strip()
    try:
        value = 0
        digit = 1

        for i in range(len(num)):
            v = num_dict[num[i]]
            if v >= 10:
                digit *= v
                value += digit
            elif i == len(num) - 1:
                value += v
            else:
                digit = v
    except KeyError:
        value = int(num)

    return value


valid_filenames = dict((ord(char), None) for char in '\\/*?:"<>|\n')


def purify_name(filename: str) -> str:
    return filename.translate(valid_filenames).strip()
