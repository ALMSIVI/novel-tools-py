import csv
import os
import re

from common import NovelData, Type
from framework import Processor


class CsvMatcher(Processor):
    """
    Accepts a line and matches titles by a given csv list.
    Arguments must include filename for the titles, and may include type string or regex dict.

    To determine the type of the line, the following three checks are done in order:
    - If the csv list contains a "type" field, then it will be used;
    - If a regex is specified in the args, then the title will be matched against the regexes;
    - If a type is specified in the args, then all lines will be set to that specific type;
    - If none of these is in the arguments, then an exception will be raised during construction.

    An object in the list consists of 3 fields:
    - type (optional): Type of the title,
    - raw: Raw title (to be matched against),
    - formatted (optional): Formatted title. If it is not present, the raw title will be used.
    """

    def __init__(self, args):
        """
        Arguments:
        - csv_filename (optional, str): Filename of the csv list file. Default is list.csv.
          This does not have to be the list file generated from a CsvWriter; one might copy and paste the list from a
          website without the type. Therefore, the following two fields are needed to determine the type of each list
          element.
        - type (optional, str): If present, specifies the type of all the matches.
        - regex (optional, dict[str, str]): If present, specifies the regexes for each type.
        """
        # in_dir will be plugged in by the splitter
        with open(os.path.join(args['in_dir'], args.get('csv_filename', 'list.csv')), 'rt') as f:
            self.list = []
            reader = csv.DictReader(f)
            for row in reader:
                self.list.append(row)

        # If list object doesn't contain type, then look at type and regex
        if not self.list[0]['type']:
            if args['type']:
                self.type = Type[args['type'].upper()]
            if args['regex']:
                self.regex = {Type[key.upper()]: re.compile(val) for key, val in args['regex'].items()}

            if not self.type and not self.regex:
                raise ValueError('Type of title is not specified in file or arguments.')

        # We assume that the list is in order, and can only be matched from the beginning.
        # Therefore, we will keep track of the number of objects that have already been matched.
        # If it exceeds the length of the list we stop matching.
        self.index = 0

    def process(self, data: NovelData) -> NovelData:
        # When the list is exhausted, stop matching
        if self.index >= len(self.list):
            return data

        to_match = self.list[self.index]
        if data.content == to_match['raw']:
            self.index += 1
            title = to_match.get('formatted', to_match['raw'])

            title_type = Type.UNRECOGNIZED
            if to_match['type']:
                title_type = to_match['type']
            elif self.type:
                title_type = self.type
            else:
                for data_type, regex in self.regex.items():
                    if regex.match(data.content):
                        title_type = data_type
                        break

            return NovelData(title_type, title, self.index, data.error, **data.others)

        return data
