import os
from framework import Writer
from common import NovelData, Type, ACC, FieldMetadata
from utils import purify_name


class DirectoryWriter(Writer, ACC):
    """
    Generates volume directories and chapter files. If there is no volume, a default volume will be created.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled. One
    can also use the same transformer to attach a 'filename' field, and the writer will prioritize this field.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('out_dir', 'str',
                          description='The working directory.'),
            FieldMetadata('debug', 'bool', default=False,
                          description='If set to True, will print the error message to the terminal.'),
            FieldMetadata('default_volume', 'str', default='default',
                          description='If the volume doesn\'t have volumes, specify the directory name to place the '
                                      'chapter files.'),
            FieldMetadata('intro_filename', 'str', default='_intro.txt',
                          description='The filename of the book/volume introduction file(s).'),
            FieldMetadata('write_blank', 'bool', default=True,
                          description='If set to True, will write blank lines to the files. Sometimes blank lines '
                                      'serve as separators in novels, and we want to keep them.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.out_dir = args['out_dir']
        self.debug = args['debug']
        self.default_volume = args['default_volume']
        self.intro_filename = args['intro_filename']
        self.write_blank = args['write_blank']

        self.curr_type = Type.UNRECOGNIZED  # Used to indicate what file is currently being written
        self.file = None
        self.curr_dir = os.path.join(self.out_dir, self.default_volume)

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if not data.has('formatted'):  # Normally, only titles should contain this field
            if data.type == Type.BLANK and not self.write_blank:
                return
            elif data.type == Type.BOOK_TITLE or data.type == Type.BOOK_INTRO:
                # Write to book intro file
                if self.curr_type != Type.BOOK_INTRO:
                    if self.file:
                        self.file.close()
                    self.file = open(os.path.join(self.out_dir, self.intro_filename), 'wt')
                    self.curr_type = Type.BOOK_INTRO
            elif data.type == Type.VOLUME_INTRO:
                # Write to _intro.txt in the volume directory
                if self.curr_type != Type.VOLUME_INTRO:
                    if self.file:
                        self.file.close()
                    self.file = open(os.path.join(self.curr_dir, self.intro_filename), 'wt')
                    self.curr_type = Type.VOLUME_INTRO
            elif data.type != Type.BLANK and data.type != Type.CHAPTER_CONTENT:
                print(f'Unrecognized data type: {data.type}')
                return

            if self.file:
                self.file.write(data.content + '\n')
        else:
            self.curr_type = data.type
            title = data.get('formatted')
            filename = purify_name(data.get('filename', title))

            # If there is an error, print on the terminal
            if self.debug and data.has('error'):
                error = data.get('error')
                print(f'{error}\t- Adjusted to {title}')

            if data.type == Type.VOLUME_TITLE:
                # For volumes, create the volume directory
                self.curr_dir = os.path.join(self.out_dir, filename)
                if not os.path.isdir(self.curr_dir):
                    os.mkdir(self.curr_dir)

                if self.file:
                    self.file.close()  # Close current chapter
                    self.file = None
            elif data.type == Type.CHAPTER_TITLE:
                # For chapters, create the chapter file
                # Close previous chapter file
                if self.file:
                    self.file.close()

                if not os.path.isdir(self.curr_dir):
                    os.mkdir(self.curr_dir)

                self.file = open(os.path.join(self.curr_dir, filename + '.txt'), 'wt')
                self.file.write(title + '\n')
