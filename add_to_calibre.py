import argparse
import json
import os


def add(directory: str) -> None:
    with open(os.path.join(directory, 'metadata.json'), 'rt') as metadata_f:
        metadata = json.load(metadata_f)
        command = 'calibredb add -a {} -c {} -l {} -T {} -t {} {}'.format(
            metadata['author'],
            os.path.join(directory, 'cover.jpg'),
            ','.join(metadata['languages']),
            ','.join(metadata['tags']),
            metadata['title'],
            os.path.join(directory, metadata['title'] + '.md'))
        os.system(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a book file to Calibre database.')
    parser.add_argument('-d', '--dir', help='Directory for book and metadata files.')
    args = parser.parse_args()

    add(args.dir)
