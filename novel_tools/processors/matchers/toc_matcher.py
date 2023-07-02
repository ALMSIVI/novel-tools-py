from pydantic import BaseModel, DirectoryPath, Field
from novel_tools.framework import NovelData, Processor
from novel_tools.readers.toc_reader import TocReader


class Options(BaseModel):
    toc_filename: str = Field(default='toc.txt', description='Filename of the toc file. This file should be generated '
                                                             'from `TocWriter`.')
    in_dir: DirectoryPath | None = Field(default=None, description='The directory to read the toc file from. Required '
                                                                   'if the filename does not contain the path.')
    encoding: str = Field(default='utf-8', description='Encoding of the toc file.')
    has_volume: bool = Field(description='Specifies whether the toc contains volumes.')
    discard_chapters: bool = Field(description='If set to True, will start from chapter 1 again when entering a new '
                                               'volume.')


class TocMatcher(Processor):
    """
    Matches data by a given Table of Contents (TOC) file. It is not advised to use toc files as a matcher; while the
    file is better human-readable, it contains less information than csv files and will not provide as many options as
    a csv file does.
    """

    def __init__(self, args):
        options = Options(**args)
        self.list = list(TocReader(options.model_dump()).read())
        self.list_index = 0

    def process(self, data: NovelData) -> NovelData:
        if self.list_index >= len(self.list):
            return data

        next_title = self.list[self.list_index]
        # Use different default values to avoid field being absent from both dicts
        if next_title.get('line_num', -1) == data.get('line_num', 1) or next_title.content == data.content:
            self.list_index += 1
            others = data.others | next_title.others
            return NovelData(next_title.content, next_title.type, next_title.index, list_index=self.list_index,
                             matched=True, **others)

        return data
