import csv
import os
from typing import Optional
from framework import Reader
from common import NovelData, Type, ACC, FieldMetadata


class CsvReader(Reader, ACC):
    """
    Recovers the novel structure from the csv list.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('csv_filename', 'str', default='list.csv',
                          description='Filename of the csv list file. This file should be generated from `CsvWriter`, '
                                      'i.e., it must contain at least type, index and content.'),
            FieldMetadata('in_dir', 'str', optional=True,
                          description='The directory to read the csv file from. Required if the filename does not '
                                      'contain the path.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the csv file.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        filename = args['csv_filename']
        filename = filename if os.path.isfile(filename) else os.path.join(args['in_dir'], filename)
        with open(filename, 'rt', encoding=args['encoding']) as f:
            self.list = []
            reader = csv.DictReader(f)
            for row in reader:
                self.list.append(row)

            self.index = 0

        first = self.list[0]
        if 'content' not in first or 'type' not in first or 'index' not in first:
            raise ValueError('csv does not contain valid columns.')

    def read(self) -> Optional[NovelData]:
        if self.index >= len(self.list):
            return None

        data = self.list[self.index]
        data_type = Type[data['type'].upper()]
        data.pop('type')
        content = data['content']
        data.pop('content')
        index = int(data['index'])
        data.pop('index')

        self.index += 1
        return NovelData(content, data_type, index, **data)
