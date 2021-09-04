import os
from typing import Optional
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
                                      'info, will be added to the data object.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        filename = args['text_filename']
        full_filename = filename if os.path.isfile(filename) else os.path.join(args['in_dir'], filename)
        self.filename = filename
        self.file = open(full_filename, 'rt', encoding=args['encoding'])
        self.verbose = args['verbose']
        self.line_num = 0

    def cleanup(self):
        self.file.close()

    def read(self) -> Optional[NovelData]:
        self.line_num += 1
        content = self.file.readline()
        if not content:
            return None

        content = content.strip()
        args = {'source': self.filename, 'line_num': self.line_num, 'raw': content} if self.verbose else {}
        return NovelData(content.strip(), **args)
