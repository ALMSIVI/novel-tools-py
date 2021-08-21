import os
from framework import Writer
from common import NovelData, Type


class TocWriter(Writer):
    """
    Lists the table of contents without actually splitting the file. Useful for debugging.
    If out_dir is empty, the table will be printed to the terminal.
    """

    def __init__(self, args):
        """
        Arguments:

        - toc_filename (str, optional, default='toc.txt'): Filename of the output toc file.
        - out_dir (str): The directory to write the toc file to.
        - formats (dict[str, str]): Key is Type representations, and the value is the format string that can use any
          NovelData field.
        - debug (bool): If set to True, will write error information to the table of contents.
        """
        self.filename = os.path.join(args.get('out_dir', args['in_dir']), args.get('out_filename', 'toc.txt'))

        self.formats = {Type[key.upper()]: value for key, value in args['formats'].items()}
        self.debug = args['debug']

        self.file = None
        self.has_volume = False  # Whether we need to indent chapter titles

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if data.data_type not in self.formats:  # Normally, should only contain volume and chapter titles
            return

        if not self.file:
            self.file = open(self.filename, 'wt')

        if data.data_type == Type.CHAPTER_TITLE and self.has_volume:
            self.file.write('\t')
        elif data.data_type == Type.VOLUME_TITLE:
            self.has_volume = True

        title = data.format(self.formats[data.data_type])
        self.file.write(title)

        if data.has('line_num'):
            self.file.write('\t' + str(data.get('line_num')))

        if self.debug and data.has('error'):
            self.file.write('\t' + data.get('error'))

        self.file.write('\n')
