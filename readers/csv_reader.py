import csv
import os
from typing import Iterator
from framework import Reader
from common import NovelData, Type, ACC, FieldMetadata


class CsvReader(Reader, ACC):
    """
    Recovers the novel structure from the csv list. The csv is required to contain a "content" column, but it does not
    have to contain the other fields from a NovelData.
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
                          description='Encoding of the csv file.'),
            FieldMetadata('types', 'dict', default={'line_num': 'int'},
                          description='Type of each additional field to be fetched. Currently, int and bool are '
                                      'supported.')
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

        if 'content' not in self.list[0]:
            raise ValueError('csv does not contain valid columns.')

        self.types = args['types']

    def read(self) -> Iterator[NovelData]:
        for i in range(len(self.list)):
            data: dict = self.list[i]
            content = data.pop('content')
            data_type = Type[data.pop('type', 'unrecognized').upper()]
            index = data.pop('index', None)
            if index is not None:
                index = int(index)

            for name, field_type in self.types.items():
                if name not in data:
                    continue

                try:
                    if field_type == 'int':
                        data[name] = int(data[name])
                    if field_type == 'bool':
                        data[name] = bool(data[name])
                except ValueError:
                    data[name] = None

            yield NovelData(content, data_type, index, **data)
