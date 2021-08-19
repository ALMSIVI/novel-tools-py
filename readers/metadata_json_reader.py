import json
import os
from typing import Optional
from framework import Reader
from common import NovelData, Type


class MetadataJsonReader(Reader):
    """
    Reads a json that contains the metadata of the book file. Will only generate a BOOK_TITLE, with the others field
    populated with the other metadata.
    """

    def __init__(self, args):
        """
        Arguments:

        - metadata_filename (str, optional, default='metadata.json'): Filename of the metadata json file. The metadata
          MUST contain a "title" field.
        """
        with open(os.path.join(args['in_dir'], args.get('metadata_filename', 'metadata.json')), 'rt') as f:
            self.metadata = json.load(f)

        if 'title' not in self.metadata:
            raise ValueError('Metadata does not contain "title" field.')

        self.consumed = False

    def read(self) -> Optional[NovelData]:
        if self.consumed:
            return None

        self.consumed = True
        title = self.metadata['title']
        self.metadata.pop('title')
        return NovelData(title, Type.BOOK_TITLE, **self.metadata)
