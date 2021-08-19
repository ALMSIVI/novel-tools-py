import csv
import os
from typing import Optional
from framework import Reader
from common import NovelData, Type


class CsvReader(Reader):
    """
    Recovers the novel structure from the csv list.
    """

    def __init__(self, args):
        """
        Arguments:

        - csv_filename (str, default='list.csv'): Filename of the csv list file. This file should be generated from
          CsvMatcher.
        - types (dict[str, str]): Correspondence between csv types and novel types.
        """
        self.types = {key: Type[value.upper()] for key, value in args['types'].items()}

        with open(os.path.join(args['in_dir'], args.get('csv_filename', 'list.csv')), 'rt') as f:
            self.list = []
            reader = csv.DictReader(f)
            for row in reader:
                self.list.append(row)

            self.index = 0

    def read(self) -> Optional[NovelData]:
        if self.index >= len(self.list):
            return None

        data = self.list[self.index]
        data_type = self.types[data['type']]
        data.pop('type')
        content = data['content']
        data.pop('content')
        index = data['index']
        data.pop('index')

        self.index += 1
        return NovelData(content, data_type, index, **data)
