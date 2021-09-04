from common import NovelData, Type, ACC, FieldMetadata
from framework import Processor
from readers.csv_reader import CsvReader


class CsvMatcher(Processor, ACC):
    """
    Matches data by a given csv list. This matcher can be used in cases where the titles are irregular or do not have
    an explicit index. Examples include "Volume 12.5" or "Tales of the Wind".

    This csv file does not have to be generated from a CsvWriter; one might copy and paste the list from a website
    without the type of the content. In such cases, it might not contain certain fields, such as `line_num` or `type`.
    Therefore, we will set up some rules to match the content and determine the type of the data:

    To make a successful match, the user will specify a list of fields to compare. The Matcher will return True if one
    of the fields matches.

    To determine the type of the line, the following three checks are done in order:
    - If the csv list contains a "type" field, then it will be used;
    - If a type is specified in the args, then all lines will be set to that specific type;
    - If none of these is in the arguments, then an exception will be raised during construction.
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
            FieldMetadata('types', 'dict', default={'line_num': 'int'},
                          description='Type of each additional field to be fetched. Currently, str, int and bool are '
                                      'supported.'),
            FieldMetadata('data_type', 'str', optional=True,
                          description='If present, specifies the type of all the titles.'),
            FieldMetadata('fields', 'list[str]', default=['line_num', 'formatted', 'raw', 'content'],
                          description='The fields to compare to when matching.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.list = []
        reader = CsvReader(args)
        while title := reader.read():
            if 'data_type' in args:
                title.type = Type[args['data_type'].upper()]
            elif title.type == Type.UNRECOGNIZED:
                raise ValueError('Type of title is not specified in file or arguments.')

            self.list.append(title)
        reader.cleanup()

        self.fields = args['fields']

        # We assume that the list is in order, and can only be matched from the beginning.
        # Therefore, we will keep track of the number of objects that have already been matched.
        # If it exceeds the length of the list we stop matching.
        self.list_index = 0
        self.indices = {}

    def process(self, data: NovelData) -> NovelData:
        # When the list is exhausted, stop matching
        if self.list_index >= len(self.list):
            return data

        next_title = self.list[self.list_index]
        data_dict = data.flat_dict()
        next_title_dict = next_title.flat_dict()
        for field in self.fields:
            if field in next_title_dict and field in data_dict and next_title_dict[field] == data_dict[field]:
                self.list_index += 1
                # The original csv file may not have an `index` column. If it doesn't exist, an index will be auto
                # generated.
                data_type = next_title.type
                if data_type not in self.indices:
                    self.indices[data_type] = 0
                self.indices[data_type] += 1

                others = data.others | next_title.others
                return NovelData(next_title.content, data_type, next_title.index or self.indices[data_type],
                                 list_index=self.list_index, matched=True, **others)

        return data
