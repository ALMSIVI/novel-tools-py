from framework import Reader
from . import NovelData, Type

class TextReader(Reader):
    '''Reads from a plain text file.'''
    def __init__(self, args):
        '''
        Arguments:
        - encoding (optional, str): The encoding of the file. Default is utf-8.
        - verbose (optional, bool): If set to True, additional information, including line number and raw line info, will
        be added to the data object. Default is False.
        '''
        self.filename = args['filename'] # This will be supplied by the program, not the config

        self.encoding = args.get('encoding', 'utf-8')
        self.verbose = args.get('verbose', False)

    def before(self):
        self.file = open(self.filename, 'rt', encoding=self.encoding)
        self.line_num = 0

    def read(self) -> NovelData:
        self.line_num += 1
        content = self.file.readline()
        if not content:
            return None

        content = content.strip()
        args = { 'line_num': self.line_num, 'raw': content } if self.verbose else {}
        return NovelData(Type.UNRECOGNIZED, content.strip(), **args)

    def after(self):
        self.file.close()