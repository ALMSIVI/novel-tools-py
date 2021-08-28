import os
from framework import Writer
from common import NovelData, Type, ACC, FieldMetadata
from utils import purify_name


class MarkdownWriter(Writer, ACC):
    """
    Writes the entire novel to a Markdown file.
    If a title field has been passed from a TitleTransformer and has the 'formatted' field filled, then the field will
    be prioritized.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('md_filename', 'str', default='text.md',
                          description='Filename of the output Markdown file, if use_title is False.'),
            FieldMetadata('out_dir', 'str',
                          description='The directory to write the markdown file to.'),
            FieldMetadata('use_title', 'bool',
                          description='If set to True, will use the book title (if specified) as the Markdown '
                                      'filename.'),
            FieldMetadata('levels', 'dict[str, int]', default={'book_title': 1, 'volume_title': 2, 'chapter_title': 3},
                          description='Specifies what level the header should be for each type.'),
            FieldMetadata('write_blank', 'bool', default=True,
                          description='If set to True, will write blank lines to the files. Sometimes blank lines '
                                      'serve as separators in novels, and we want to keep them.'),
            FieldMetadata('debug', 'bool', default=False,
                          description='If set to True, will print the error message to the terminal.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.use_title = args['use_title']
        self.filename = args['md_filename']
        self.out_dir = args['out_dir']
        self.levels = {Type[key.upper()]: '#' * value + ' ' for key, value in args['levels'].items()}
        self.write_blank = args['write_blank']
        self.debug = args['debug']

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
