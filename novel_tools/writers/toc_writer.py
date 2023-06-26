from pydantic import BaseModel, Field
from pathlib import Path
from novel_tools.framework import Writer
from novel_tools.common import NovelData, Type
from novel_tools.utils import purify_name


class Options(BaseModel):
    toc_filename: str = Field(default='toc.txt', description='Filename of the output toc file.')
    out_dir: Path = Field(description='The directory to write the toc file to.')
    write_line_num: bool = Field(default=True, description='If set to True, will write line number to the toc.')
    debug: bool = Field(default=False,
                        description='If set to True, will write error information to the table of contents.')


class TocWriter(Writer):
    """
    Lists the table of contents without actually splitting the file. Useful for debugging.
    If out_dir is empty, the table will be printed to the terminal.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled.
    """

    def __init__(self, args):
        options = Options(**args)
        self.toc_path = options.out_dir / purify_name(options.toc_filename)
        self.write_line_num = options.write_line_num
        self.debug = options.debug

        self.list = []
        self.has_volume = False  # Whether we need to indent chapter titles

    def accept(self, data: NovelData) -> None:
        if not data.has('formatted'):  # Normally, only titles should contain this field
            return

        if data.type == Type.VOLUME_TITLE:
            self.has_volume = True
        self.list.append(data)

    def write(self) -> None:
        with self.toc_path.open('wt') as f:
            for data in self.list:
                line = ''
                if data.type == Type.CHAPTER_TITLE and self.has_volume:
                    line += '\t'

                line += data.get('formatted')

                if self.write_line_num and data.has('line_num'):
                    line += '\t' + str(data.get('line_num'))

                if self.debug and data.has('error'):
                    line += '\t' + data.get('error')

                f.write(line + '\n')
