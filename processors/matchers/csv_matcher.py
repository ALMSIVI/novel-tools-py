import csv
import os
import re
from common import NovelData, Type, ACC, FieldMetadata
from framework import Processor


class CsvMatcher(Processor, ACC):
    """
    Accepts a line and matches titles by a given csv list. This matcher can be used in cases where the titles are
    irregular or do not have an explicit index. Examples include "Volume 12.5" or "Tales of the Wind".
    This does not have to be the list file generated from a CsvWriter; one might copy and paste the list from a website
    without the type of the content. Therefore, one of the following fields is required to determine the type.

    To determine the type of the line, the following three checks are done in order:
    - If the csv list contains a "type" field, then it will be used;
    - If a type is specified in the args, then all lines will be set to that specific type;
    - If a regex is specified in the args, then the title will be matched against the regexes;
    - If none of these is in the arguments, then an exception will be raised during construction.

    An object in the list consists of 3 fields:
    - type (optional): Type of the title,
    - raw: Raw title (to be matched against),
    - formatted (optional): Formatted title. If it is not present, the raw title will be used.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('csv_filename', 'str', default='list.csv',
                          description='Filename of the csv list file.'),
            FieldMetadata('in_dir', 'str', optional=True,
                          description='The directory to read the csv file from. Required if the filename does not '
                                      'contain the path.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the csv list file.'),
            FieldMetadata('type', 'str', optional=True,
                          description='If present, specifies the type of all the matches.'),
            FieldMetadata('regex', 'dict[str, str]', optional=True,
                          description='If present, specifies the regexes for each type.')
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

        # If list object doesn't contain type, then look at type and regex
        if 'type' in self.list[0]:
            self.get_type = self.get_type_list
        elif 'type' in args:
            self.type = Type[args['type'].upper()]
            self.get_type = self.get_type_type
        elif 'regex' in args:
            self.regex = {Type[key.upper()]: re.compile(val) for key, val in args['regex'].items()}
            self.get_type = self.get_type_regex
        else:
            raise ValueError('Type of title is not specified in file or arguments.')

        # We assume that the list is in order, and can only be matched from the beginning.
        # Therefore, we will keep track of the number of objects that have already been matched.
        # If it exceeds the length of the list we stop matching.
        self.list_index = 0
        self.indices = {}

    def process(self, data: NovelData) -> NovelData:
        # When the list is exhausted, stop matching
        if self.list_index >= len(self.list):
            return data

        to_match = self.list[self.list_index]
        if data.content == to_match['raw']:
            self.list_index += 1
            title = to_match.get('formatted', to_match['raw'])
            title_type = self.get_type(to_match, data) or Type.UNRECOGNIZED
            if title_type not in self.indices:
                self.indices[title_type] = 0
            self.indices[title_type] += 1
            return NovelData(title, title_type, self.indices[title_type], list_index=self.list_index, **data.others)

        return data

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_type_list(self, to_match, data):
        return Type[to_match['type'].upper()]

    # noinspection PyUnusedLocal
    def get_type_type(self, to_match, data):
        return self.type

    # noinspection PyUnusedLocal
    def get_type_regex(self, to_match, data):
        for data_type, regex in self.regex.items():
            if regex.match(data.content):
                return data_type
