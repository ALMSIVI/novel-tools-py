import csv, json, os
from split.matchers import Matcher
from utils import snake_to_pascal, import_class

class MatcherFactory:
    def __init__(self):
        module_names = [filename[:-3] for filename in os.listdir('./split/matchers') if filename.endswith('_matcher.py')]
        
        self.matchers: dict[str, Matcher] = {}
        for module in module_names:
            matcher_name = snake_to_pascal(module)
            self.matchers[matcher_name] = import_class(module, 'split.matchers')

    def get(self, name, args):
        return self.matchers[name](args)


def check_volume_matchers(in_dir: str, factory: MatcherFactory):
    # Check csv first.
    csv_volumes = os.path.join(in_dir, 'volumes.csv')
    json_volumes = os.path.join(in_dir, 'volumes.json')
    volumes = None

    if os.path.isfile(csv_volumes):
        volumes = []
        with open(csv_volumes, 'rt') as f:
            reader = csv.DictReader(f, fieldnames=['name, volume'])
            for row in reader:
                volumes.append(row)
        
    elif os.path.isfile(json_volumes):
        with open(json_volumes, 'rt') as f:
            volumes = json.load(f)
    
    if volumes is None:
        return None
    else:
        return [factory.get('VolumeMatcher', {'volumes': volumes})]

    
def generate_matchers(in_dir: str):
    factory = MatcherFactory()

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
