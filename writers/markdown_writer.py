import os
from framework import Writer
from common import NovelData, Type
from utils import purify_name


class MarkdownWriter(Writer):
    """
    Writes the entire novel to a Markdown file.
    If a title field has been passed from a TitleTransformer and has the 'formatted' field filled, then the field will
    be prioritized.
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
        - debug (bool, optional, default=False): If set to True, will print the error message to the terminal.
        """
        self.use_title = args['use_title']
        self.filename = args.get('md_filename', 'text.md')
        self.out_dir = args['out_dir']
        self.levels = {Type[key.upper()]: '#' * value + ' ' for key, value in args['levels'].items()}
        self.write_blank = args.get('write_blank', True)
        self.debug = args.get('Debug', True)

        self.file = None

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if self.debug and data.has('error'):
            print(data.get('error'))

        if data.type == Type.BLANK and not self.write_blank:
            return

        if not self.file:
            filename = data.content + '.md' if self.use_title and data.type == Type.BOOK_TITLE else self.filename
            self.file = open(os.path.join(self.out_dir, purify_name(filename)), 'wt')

        self.file.write(self.levels.get(data.type, '') + data.get('formatted', data.content) + '\n')
