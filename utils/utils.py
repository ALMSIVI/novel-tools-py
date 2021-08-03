import os
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