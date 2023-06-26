from pydantic import BaseModel, Field
from pathlib import Path
from typing import Iterator
from novel_tools.framework import NovelData, Reader


class Options(BaseModel):
    text_filename: str = Field(default='text.txt', description='The filename of the text.')
    in_dir: Path | None = Field(description='The directory to read the text file from. Required if the filename does '
                                            'not contain the path.')
    encoding: str = Field(default='utf-8', description='The encoding of the file.')
    verbose: bool = Field(default=False,
                          description='If set to True, additional information, including line number and raw line '
                                      'info, will be added to the data object.')
    merge_newlines: bool = Field(default=False,
                                 description='If set to True, will merge two newline characters into one. Sometimes '
                                             'newline characters carry meanings, and we do not want decorative '
                                             'newlines to mix with those meaningful ones.')


class TextReader(Reader):
    """Reads from a plain text file."""

    def __init__(self, args):
        options = Options(**args)
        self.filename = Path(options.text_filename)
        self.in_dir = options.in_dir
        self.encoding = options.encoding
        self.verbose = options.verbose
        self.merge_newlines = options.merge_newlines

    def read(self) -> Iterator[NovelData]:
        text_path = self.filename if self.filename.is_file() else self.in_dir / self.filename
        with text_path.open('rt', encoding=self.encoding) as f:
            line_num = 0
            prev_newline = False
            for line in f:
                line_num += 1
                content = line.strip()
                if content == '' and self.merge_newlines:
                    prev_newline = not prev_newline
                    if prev_newline:
                        continue
                else:
                    prev_newline = False

                args = {'source': text_path, 'line_num': line_num, 'raw': line.rstrip()} if self.verbose else {}
                yield NovelData(content, **args)
