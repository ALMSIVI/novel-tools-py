import json, os
from importlib import import_module
from split.matchers import Matcher


def import_matchers() -> dict[str, Matcher]:
    module_names = [filename[:-3] for filename in os.listdir('./split/matchers') if filename.endswith('_matcher.py')]
    
    matchers = {}
    for module in module_names:
        matcher_name = module.replace('_', ' ').title().replace(' ', '')
        matchers[matcher_name] = getattr(import_module(f'split.matchers.{module}'), matcher_name)

    return matchers

def generate_matchers(in_dir: str):
    matchers = import_matchers()

    matcher_filename = os.path.join(in_dir, 'matchers.json')
    if not os.path.isfile(matcher_filename):
        matcher_filename = os.path.join(os.curdir, 'default_matchers.json')

    with open(matcher_filename, 'rt') as f:
        configs = json.load(f)

    # Check if we need custom volume matchers
    volumes_filename = os.path.join(in_dir, 'volumes.json')
    if os.path.isfile(volumes_filename):
        with open(volumes_filename, 'rt') as f:
            volumes = json.load(f)
            volume_matchers = [matchers['VolumeMatcher']({'volumes': volumes})]
    else:
        volume_matchers = [matchers[matcher['class']](matcher) for matcher in configs['volumes']]

    chapter_matchers = [matchers[matcher['class']](matcher) for matcher in configs['chapters']]

    return volume_matchers, chapter_matchers
