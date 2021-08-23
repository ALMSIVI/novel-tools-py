import os
from framework import Writer
from common import NovelData, Type
from utils import purify_name


class DirectoryWriter(Writer):
    """
    Generates volume directories and chapter files. If there is no volume, a default volume will be created.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled. One
    can also use the same transformer to attach a 'filename' field, and the writer will prioritize this field.
    """

    def __init__(self, args):
        """
        Arguments:

        - out_dir (str): The working directory.
        - debug (bool, optional, default=False): If set to True, will print the error message to the terminal.
        - default_volume (str, optional, default='default'): If the volume doesn't have volumes, specify the directory
          name to place the chapter files.
        - intro_filename (str, optional, default='_intro.txt'): The filename of the book/volume introduction file(s).
        - write_blank (bool, optional, default=True): If set to True, will write blank lines to the files. Sometimes
          blank lines serve as separators in novels, and we want to keep them.
        """
        self.out_dir = args['out_dir']
        self.debug = args.get('debug', False)
        self.default_volume = args.get('default_volume', 'default')
        self.intro_filename = args.get('intro_filename', '_intro.txt')
        self.write_blank = args.get('write_blank', True)

        self.curr_type = Type.UNRECOGNIZED  # Used to indicate what file is currently being written
        self.file = None
        self.curr_dir = os.path.join(self.out_dir, self.default_volume)

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if not data.has('formatted'):  # Normally, should only contain volume and chapter titles
            if data.data_type == Type.BLANK and not self.write_blank:
                return
            elif data.data_type == Type.BOOK_TITLE or data.data_type == Type.BOOK_INTRO:
                # Write to book intro file
                if self.curr_type != Type.BOOK_INTRO:
                    if self.file:
                        self.file.close()
                    self.file = open(os.path.join(self.out_dir, self.intro_filename), 'wt')
                    self.curr_type = Type.BOOK_INTRO
            elif data.data_type == Type.VOLUME_INTRO:
                # Write to _intro.txt in the volume directory
                if self.curr_type != Type.VOLUME_INTRO:
                    if self.file:
                        self.file.close()
                    self.file = open(os.path.join(self.curr_dir, self.intro_filename), 'wt')
                    self.curr_type = Type.VOLUME_INTRO
            elif data.data_type != Type.BLANK and data.data_type != Type.CHAPTER_CONTENT:
                print(f'Unrecognized data type: {data.data_type}')
                return

            if self.file:
                self.file.write(data.content + '\n')
        else:
            title = data.get('formatted')
            filename = purify_name(data.get('filename', title))

            # If there is an error, print on the terminal
            if self.debug and data.has('error'):
                error = data.get('error')
                print(f'{error}\t- Adjusted to {title}')

            if data.data_type == Type.VOLUME_TITLE:
                # For volumes, create the volume directory
                self.curr_dir = os.path.join(self.out_dir, filename)
                if not os.path.isdir(self.curr_dir):
                    os.mkdir(self.curr_dir)

                if self.file:
                    self.file.close()  # Close current chapter
                    self.file = None
            elif data.data_type == Type.CHAPTER_TITLE:
                # For chapters, create the chapter file
                # Close previous chapter file
                if self.file:
                    self.file.close()

                if not os.path.isdir(self.curr_dir):
                    os.mkdir(self.curr_dir)

                self.file = open(os.path.join(self.curr_dir, filename + '.txt'), 'wt')
                self.file.write(title + '\n')
