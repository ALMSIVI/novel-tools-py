import csv
from pathlib import Path
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
            FieldMetadata('in_dir', 'Path', optional=True,
                          description='The directory to read the csv file from. Required if the filename does not '
                                      'contain the path.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the csv file.'),
            FieldMetadata('types', 'dict', default={'line_num': 'int', 'source': 'Path'},
                          description='Type of each additional field to be fetched. Currently, int, bool and Path are '
                                      'supported.'),
            FieldMetadata('join_dir', 'list[str]', default=['source'],
                          description='If the data corresponding to the given field names is type Path, it will be '
                                      'treated as a relative path and will be joined by `in_dir`.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.in_dir = args['in_dir']
        csv_file = Path(args['csv_filename'])
        csv_file = csv_file if csv_file.is_file() else Path(self.in_dir, csv_file)
        with csv_file.open('rt', encoding=args['encoding']) as f:
            self.list = []
            reader = csv.DictReader(f)
            for row in reader:
                self.list.append(row)

        if 'content' not in self.list[0]:
            raise ValueError('csv does not contain valid columns.')

        self.types = args['types']
        self.join_dir = args['join_dir']

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
                    if field_type == 'Path':
                        data[name] = Path(data[name])
                except ValueError:
                    data[name] = None

            for name in self.join_dir:
                if isinstance(data.get(name, None), Path):
                    data[name] = self.in_dir / data[name]

            yield NovelData(content, data_type, index, **data)
