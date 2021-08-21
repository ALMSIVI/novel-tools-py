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

        - use_title (bool): If set to True, will use the book title (if specified) as the Markdown filename.
        - md_filename (str, optional, default='text.md'): Filename of the output Markdown file, if use_title is False.
        - out_dir (str): The directory to write the markdown file to.
        - levels (dict[str, int]): Specifies what level the header should be for each type.
        - write_blank (bool, optional, default=True): If set to True, will write blank lines to the files. Sometimes
          blank lines serve as separators in novels, and we want to keep them.
        """
        self.use_title = args['use_title']
        self.filename = args.get('csv_filename', 'text.md')
        self.out_dir = args['out_dir']
        self.levels = {Type[key.upper()]: '#' * value + ' ' for key, value in args['levels'].items()}
        self.write_blank = args.get('write_blank', True)

        self.file = None

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if data.data_type == Type.BLANK and not self.write_blank:
            return

        if not self.file:
            filename = data.content + '.md' if self.use_title and data.data_type == Type.BOOK_TITLE else self.filename
            self.file = open(os.path.join(self.out_dir, filename), 'wt')

        self.file.write(self.levels.get(data.data_type, ''))
        self.file.write(data.content + '\n')
