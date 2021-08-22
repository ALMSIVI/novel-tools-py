import json
import os


def add(directory: str) -> None:
    with open(os.path.join(directory, 'metadata.json'), 'rt') as metadata_f:
        metadata = json.load(metadata_f)
        # noinspection SpellCheckingInspection
        command = 'calibredb add -a {} -c {} -l {} -T {} -t {} {}'.format(
            metadata['author'],
            os.path.join(directory, 'cover.jpg'),
            ','.join(metadata['languages']),
            ','.join(metadata['tags']),
            metadata['title'],
            os.path.join(directory, metadata['title'] + '.md'))
        os.system(command)
