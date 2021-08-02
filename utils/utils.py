from importlib import import_module

def snake_to_pascal(s: str):
    return s.replace('_', ' ').title().replace(' ', '')

def import_class(filename: str, base_package: str):
    return getattr(import_module(f'{base_package}.{filename}'), snake_to_pascal(filename))

def import_function(filename: str, base_package: str, func_name: str):
    return getattr(import_module(f'{base_package}.{filename}'), func_name)