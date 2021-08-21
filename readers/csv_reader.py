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
        - in_dir (str, optional): The directory to read the csv file from. Required if the filename does not contain the
          path.
        - types (dict[str, str]): Correspondence between csv types and novel types.
        """
        self.types = {key: Type[value.upper()] for key, value in args['types'].items()}

        filename = args.get('csv_filename', 'list.csv')
        filename = filename if os.path.isfile(filename) else os.path.join(args['in_dir'], filename)
        with open(filename, 'rt', encoding=args.get('encoding', 'utf-8')) as f:
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
