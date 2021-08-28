import os
from framework import Writer
from common import NovelData, Type, ACC, FieldMetadata
from utils import purify_name


class TocWriter(Writer, ACC):
    """
    Lists the table of contents without actually splitting the file. Useful for debugging.
    If out_dir is empty, the table will be printed to the terminal.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('toc_filename', 'str', default='toc.txt',
                          description='Filename of the output toc file.'),
            FieldMetadata('out_dir', 'str',
                          description='The directory to write the toc file to.'),
            FieldMetadata('debug', 'bool', default=False,
                          description='If set to True, will write error information to the table of contents.'),
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.filename = os.path.join(args['out_dir'], purify_name(args['toc_filename']))
        self.debug = args['debug']

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
