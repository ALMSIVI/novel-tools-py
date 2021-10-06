import os
from typing import Iterator
from framework import Reader
from common import NovelData, ACC, FieldMetadata


class TextReader(Reader, ACC):
    """Reads from a plain text file."""

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('text_filename', 'str', default='text.txt',
                          description='The filename of the text.'),
            FieldMetadata('in_dir', 'str', optional=True,
                          description='The directory to read the text file from. Required if the filename does not '
                                      'contain the path.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='The encoding of the file.'),
            FieldMetadata('verbose', 'bool', default=False,
                          description='If set to True, additional information, including line number and raw line '
                                      'info, will be added to the data object.'),
            FieldMetadata('merge_newlines', 'bool', default=False,
                          description='If set to True, will merge two newline characters into one. Sometimes newline '
                                      'characters carry meanings, and we do not want decorative newlines to mix with '
                                      'those meaningful ones.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.filename = args['text_filename']
        self.in_dir = args['in_dir']
        self.encoding = args['encoding']
        self.verbose = args['verbose']
        self.merge_newlines = args['merge_newlines']

    def read(self) -> Iterator[NovelData]:
        full_filename = self.filename if os.path.isfile(self.filename) else os.path.join(self.in_dir, self.filename)
        source = os.path.basename(self.filename)
        with open(full_filename, 'rt', encoding=self.encoding) as f:
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

                args = {'source': source, 'line_num': line_num, 'raw': line.rstrip()} if self.verbose else {}
                yield NovelData(content, **args)
