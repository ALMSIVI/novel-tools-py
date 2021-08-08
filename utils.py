import os, json
from importlib import import_module

def snake_to_pascal(s: str):
    return s.replace('_', ' ').title().replace(' ', '')

def import_class(filename: str, base_package: str):
    return getattr(import_module(f'{base_package}.{filename}'), snake_to_pascal(filename))

def import_function(filename: str, base_package: str, func_name: str):
    return getattr(import_module(f'{base_package}.{filename}'), func_name)

class ClassFactory:
    def __init__(self, package_base: str, ending: str):
        module_dir = os.path.join('.', *package_base.split('.'))
        module_names = [filename[:-3] for filename in os.listdir(module_dir) if filename.endswith(f'{ending}.py')]
        
        self.classes = {}
        for module in module_names:
            name = snake_to_pascal(module)
            self.classes[name] = import_class(module, package_base)

    def get(self, name, args):
        return self.classes[name](args)


def generate_objects(in_dir: str, config_filename: str, default_config_filename: str, additional_args: dict = {}):
    '''Generates corresponding objects from config files.'''
    filename = os.path.join(in_dir, config_filename)
    if not os.path.isfile(filename):
        filename = os.path.join(os.curdir, default_config_filename)

    with open(filename, 'rt') as f:
        config_map = json.load(f)

    objects = {}
    for key, configs in config_map.items():
        object_list = []
        for config in configs:
            factory = ClassFactory(config['package_base'], config['ending'])
            object_list += [factory.get(args['class'], args | additional_args) for args in config['list']]

        objects[key] = object_list

    return objects


num_dict = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
            "十": 10, "廿": 20, "卅": 30, "卌": 40, "百": 100, "千": 1000}


def to_num(num: str) -> int:
    '''
    Converts a chinese string to a number.
    '''
    num = num.strip()
    try:
        value = int(num)
    except:
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

    return value


valid_filenames = dict((ord(char), None) for char in '\/*?:"<>|\n')


def purify_name(filename: str) -> str:
    return filename.translate(valid_filenames).strip()