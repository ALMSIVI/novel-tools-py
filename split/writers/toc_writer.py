import os
from framework import Writer
from common import NovelData, Type

class TocWriter(Writer):
    '''
    Lists the table of contents without actually splitting the file. Useful for debugging.
    If out_dir is empty, the table will be printed to the terminal.
    '''
    def __init__(self, args):
        '''
        Arguments:
        - formats (dict[str, str]): Key is Type representations, and the value is the format string that contains {index} and {title} to be formatted.
        - debug (bool): If set to True, will write error information to the table of contents.
        '''
        out_dir = args.get('out_dir', args['in_dir']) # Both will be supplied by the program, not the config
        self.filename = os.path.join(out_dir, 'toc.txt') if os.path.isdir(out_dir) else out_dir

        self.formats = {Type[key.upper()]: value for key, value in args['formats'].items()}
        self.debug = args['debug']

    def before(self):
        self.file = open(self.filename, 'wt')
        self.has_volume = False # Whether we need to indent chapter titles

    def after(self):
        self.file.close()

    def write(self, data: NovelData):
        if data.type not in self.formats: # Normally, should only contain volume and chapter titles
            return

        if data.type == Type.CHAPTER_TITLE and self.has_volume:
            self.file.write('\t')
        elif data.type == Type.VOLUME_TITLE:
            self.has_volume = True

        title = self.formats[data.type].format(index=data.index, title=data.content)
        self.file.write(title)

        if data.has('line_num'):
            self.file.write('\t' + str(data.get('line_num')))

        if self.debug and data.error is not None:
            self.file.write('\t' + data.error)
        
        self.file.write('\n')