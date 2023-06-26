from pydantic import BaseModel, Field
from pathlib import Path
from novel_tools.framework import NovelData, Type, Processor
from novel_tools.readers.csv_reader import CsvReader


class Options(BaseModel):
    csv_filename: str = Field(default='list.csv', description='Filename of the csv list file.')
    in_dir: Path | None = Field(
        description='The directory to read the csv file from. Required if the filename does not contain the path.')
    encoding: str = Field(default='utf-8', description='Encoding of the csv file.')
    types: dict[str, str] = Field(default={'line_num': 'int', 'source': 'Path'},
                                  description='Type of each additional field to be fetched. See CsvReader for more '
                                              'details.')
    join_dir: list[str] = Field(default=['source'],
                                description='Specifies fields names that need dir joining. See CsvReader for more '
                                            'details.')
    data_type: str | None = Field(description='If present, specifies the type of all the titles.')


class CsvMatcher(Processor):
    """
    Matches data by a given csv list. This matcher can be used in cases where the titles are irregular or do not have
    an explicit index. Examples include "Volume 12.5" or "Tales of the Wind".

    This csv file does not have to be generated from a CsvWriter; one might copy and paste the list from a website
    without the type of the content. In such cases, it might not contain certain fields, such as `line_num` or `type`.
    Therefore, we will set up some rules to match the content and determine the type of the data:

    To make a successful match, the Matcher will first check the source and line_num. If they don't exist, it will then
    check for raw and/or content.

    To determine the type of the line, the following three checks are done in order:
    - If the csv list contains a "type" field, then it will be used;
    - If a type is specified in the args, then all lines will be set to that specific type;
    - If none of these is in the arguments, then an exception will be raised during construction.
    """

    def __init__(self, args):
        options = Options(**args)
        self.list = list(CsvReader(options.dict()).read())
        for title in self.list:
            if options.data_type is not None:
                title.type = Type[options.data_type.upper()]
            elif title.type == Type.UNRECOGNIZED:
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

        next_title = self.list[self.list_index]

        # First, check for `source` (if it exists). This is usually populated if we use a DirectoryWriter or multiple
        # TextReaders. If we only have one TextReader, there is only one file, so source is not necessary, and we can
        # simply omit this field when we write the results using a CsvWriter. If `source` exist and match, compare
        # `line_num`.
        if next_title.has('source') and data.has('source'):
            if next_title.get('source') != data.get('source') or next_title.get('line_num') != data.get('line_num'):
                return data
            return self.__merge(next_title, data)

        # If we only have one TextReader and don't have `source` in the csv, we simply compare line_num.
        if next_title.has('line_num') and data.has('line_num'):
            if next_title.get('line_num') != data.get('line_num'):
                return data
            return self.__merge(next_title, data)

        # If the csv is not created from a CsvWriter and doesn't have `line_num`, we will use raw and/or content.
        if next_title.get('raw', next_title.content) == data.get('raw', data.content):
            return self.__merge(next_title, data)

        return data

    def __merge(self, title: NovelData, data: NovelData) -> NovelData:
        self.list_index += 1
        # The original csv file may not have an `index` column. If it doesn't exist, an index will be auto
        # generated.
        data_type = title.type
        if data_type not in self.indices:
            self.indices[data_type] = 0
        self.indices[data_type] += 1

        others = data.others | title.others
        return NovelData(title.content, data_type, title.index or self.indices[data_type],
                         list_index=self.list_index, matched=True, **others)
