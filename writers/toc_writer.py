import os
from framework import Writer
from common import NovelData, Type
from utils import purify_name


class TocWriter(Writer):
    """
    Lists the table of contents without actually splitting the file. Useful for debugging.
    If out_dir is empty, the table will be printed to the terminal.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled.
    """

    def __init__(self, args):
        """
        Arguments:

        - toc_filename (str, optional, default='toc.txt'): Filename of the output toc file.
        - out_dir (str): The directory to write the toc file to.
        - debug (bool, optional, default=False): If set to True, will write error information to the table of contents.
        """
        self.filename = os.path.join(args['out_dir'], purify_name(args.get('out_filename', 'toc.txt')))
        self.debug = args.get('debug', False)

        self.file = None
        self.has_volume = False  # Whether we need to indent chapter titles

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if not data.has('formatted'):  # Normally, should only contain volume and chapter titles
            return

        if not self.file:
            self.file = open(self.filename, 'wt')

        line = ''
        if data.type == Type.CHAPTER_TITLE and self.has_volume:
            line += '\t'
        elif data.type == Type.VOLUME_TITLE:
            self.has_volume = True

        line += data.get('formatted')

        if data.has('line_num'):
            line += '\t' + str(data.get('line_num'))

        if self.debug and data.has('error'):
            line += '\t' + data.get('error')

        self.file.write(line + '\n')
