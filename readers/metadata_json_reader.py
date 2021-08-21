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
        - in_dir (str, optional): The directory to read the metadata file from. Required if the filename does not
          contain the path.
        """
        filename = args.get('metadata_filename', 'metadata.json')
        filename = filename if os.path.isfile(filename) else os.path.join(args['in_dir'], filename)
        with open(filename, 'rt') as f:
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
