import json, os
from .matcher import Matcher
from utils import ClassFactory
from volumes import read_volumes

def check_volume_matchers(in_dir: str, factory: ClassFactory):
    # Check csv first.
    volumes = read_volumes(in_dir)
    if volumes is None:
        return None
    else:
        return [factory.get('VolumeMatcher', {'volumes': volumes})]

    
def generate_matchers(in_dir: str) -> tuple[list[Matcher], list[Matcher]]:
    factory = ClassFactory('split.matchers', '_matcher')

    matcher_filename = os.path.join(in_dir, 'matchers.json')
    if not os.path.isfile(matcher_filename):
        matcher_filename = os.path.join(os.curdir, 'default_matchers.json')

    with open(matcher_filename, 'rt') as f:
        configs = json.load(f)

    # Check if we need custom volume matchers. There are two formats: csv and json.
    volume_matchers = check_volume_matchers(in_dir, factory)
    if volume_matchers is None:
        volume_matchers = [factory.get(matcher['class'], matcher) for matcher in configs['volumes']]

    chapter_matchers = [factory.get(matcher['class'], matcher) for matcher in configs['chapters']]

    return volume_matchers, chapter_matchers
