import os
from typing import Optional
from framework import Reader
from common import NovelData


class TextReader(Reader):
    """Reads from a plain text file."""

    def __init__(self, args):
        """
        Arguments:

        - text_filename (str, optional, default='text.txt'): The filename of the text.
        - in_dir (str, optional): The directory to read the text file from. Required if the filename does not contain
          the path.
        - encoding (str, optional, default='utf-8'): The encoding of the file.
        - verbose (bool, optional, default=False): If set to True, additional information, including line number and
          raw line info, will be added to the data object.
        """
        filename = args.get('text_filename', 'text.txt')
        filename = filename if os.path.isfile(filename) else os.path.join(args['in_dir'], filename)
        self.file = open(filename, 'rt', encoding=args.get('encoding', 'utf-8'))
        self.verbose = args.get('verbose', False)
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
        return NovelData(content.strip(), **args)
