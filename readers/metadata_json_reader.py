import json
import os
from typing import Iterator
from framework import Reader
from common import NovelData, Type, ACC, FieldMetadata


class MetadataJsonReader(Reader, ACC):
    """
    Reads a json that contains the metadata of the book file. Will only generate a BOOK_TITLE, with the others field
    populated with the other metadata.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('metadata_filename', 'str', default='metadata.json',
                          description='Filename of the metadata json file. The metadata MUST contain a \'title\' '
                                      'field.'),
            FieldMetadata('in_dir', 'str', optional=True,
                          description='The directory to read the metadata file from. Required if the filename does '
                                      'not contain the path.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the json file.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        filename = args['metadata_filename']
        filename = filename if os.path.isfile(filename) else os.path.join(args['in_dir'], filename)
        with open(filename, 'rt', encoding=args['encoding']) as f:
            self.metadata = json.load(f)

        if 'title' not in self.metadata:
            raise ValueError('Metadata does not contain "title" field.')

    def read(self) -> Iterator[NovelData]:
        title = self.metadata['title']
        self.metadata.pop('title')
        yield NovelData(title, Type.BOOK_TITLE, **self.metadata)
