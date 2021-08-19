import os
from framework import Writer
from common import NovelData, Type


class MarkdownWriter(Writer):
    """
    Writes the entire novel to a Markdown file.
    """

    def __init__(self, args):
        """
        Arguments:

        - levels (dict[str, int]): Specifies what level the header should be for each type.
        - write_blank (bool, optional, default=True): If set to True, will write blank lines to the files. Sometimes
          blank lines serve as separators in novels, and we want to keep them.
        """
        self.out_dir = args.get('out_dir', args['in_dir'])  # Both will be supplied by the program, not the config
        self.levels = {Type[key.upper()]: '#' * value + ' ' for key, value in args['levels'].items()}
        self.write_blank = args.get('write_blank', True)

        self.file = None

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        # The first data should be of type BOOK_TITLE. If this is not the case, the name will be extracted from the
        # directory name.
        if not self.file:
            filename = data.content if data.data_type == Type.BOOK_TITLE else os.path.basename(os.getcwd())
            self.file = open(os.path.join(self.out_dir, filename + '.md'), 'wt')
            return

        if data.data_type == Type.BLANK and not self.write_blank:
            return

        self.file.write(self.levels.get(data.data_type, ''))
        self.file.write(data.content + '\n')
