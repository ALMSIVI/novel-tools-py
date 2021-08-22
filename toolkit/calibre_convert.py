import json
import os


def convert(directory: str) -> None:
    with open(os.path.join(directory, 'metadata.json'), 'rt') as metadata_f:
        metadata = json.load(metadata_f)
        command = 'ebook-convert {} {} --level1-toc //h:h1 --level2-toc //h:h2 --level3-toc //h:h3 --authors {} ' \
                  '--cover {} --language {} --publisher {} --tags {} --title {}'
        command = command.format(
            os.path.join(directory, metadata['title'] + '.md'),
            os.path.join(directory, metadata['title'] + '.epub'),
            metadata['author'],
            os.path.join(directory, 'cover.jpg'),
            ','.join(metadata['languages']),
            metadata['publisher'],
            ','.join(metadata['tags']),
            metadata['title'],
        )
        os.system(command)
