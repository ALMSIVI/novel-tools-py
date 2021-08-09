import os
from typing import Optional
from framework import Reader
from common import NovelData, Type


class TextReader(Reader):
    """Reads from a plain text file."""

    def __init__(self, args):
        """
        Arguments:
        - encoding (optional, str): The encoding of the file. Default is utf-8.
        - verbose (optional, bool): If set to True, additional information, including line number and raw line info,
          will be added to the data object. Default is False.
        """
        # Both will be supplied by the program, not the config
        self.filename = args['filename'] if os.path.isfile(args['filename']) else os.path.join(args['in_dir'],
                                                                                               args['filename'])

        self.encoding = args.get('encoding', 'utf-8')
        self.verbose = args.get('verbose', False)
        self.file = open(self.filename, 'rt', encoding=self.encoding)
        self.line_num = 0

    def cleanup(self):
        self.file.close()

    def read(self) -> Optional[NovelData]:
        self.line_num += 1
        content = self.file.readline()
        if not content:
            return None

        content = content.strip()
        args = {'line_num': self.line_num, 'raw': content} if self.verbose else {}
        return NovelData(Type.UNRECOGNIZED, content.strip(), **args)
