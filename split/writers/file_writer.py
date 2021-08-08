import os
from framework import Writer
from common import NovelData, Type
from utils import purify_name

class FileWriter(Writer):
    '''
    Generates volume directories and chapter files. If there is no volume, a default volume will be created.
    '''
    def __init__(self, args):
        '''
        Arguments:
        - formats (dict[str, dict[str, str]] | dict[str, str]): Key is Type representations, and the value can either consist of the following two fields:
            - title: Format string that can use any NovelData field. Will be written to the top of the file.
            - filename: Same as above, except that it will be used as a filename (after purification).
        Or it can simply be one format string, in which case both the title and filename will use it.
        - correct (bool): If set to False and the original_index field exists, will use the original index.
        - debug (bool): If set to True, will print the error message to the terminal.
        - default_volume: If the volume doesn't have volumes, specify the directory name to place the chapter files.
        '''
        self.out_dir = args.get('out_dir', args['in_dir']) # Both will be supplied by the program, not the config

        self.formats = {Type[key.upper()]: {'title': value, 'filename': value} if type(value) is str else value for key, value in args['formats'].items()}
        self.correct = args['correct']
        self.debug = args['debug']
        self.default_volume = args['default_volume']

    def before(self):
        self.file = None
        self.curr_dir = os.path.join(self.out_dir, self.default_volume)

    def after(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if data.type not in self.formats: # Normally, should only contain volume and chapter titles
            if data.type == Type.BLANK:
                return
            elif data.type == Type.BOOK_TITLE or data.type == Type.BOOK_INTRO:
                # Write to _intro.txt in the book directory
                if self.file:
                    self.file.close()
                self.file = open(os.path.join(self.out_dir, '_intro.txt'), 'wt')

            elif data.type == Type.VOLUME_INTRO:
                # Write to _intro.txt in the volume directory
                if self.file:
                    self.file.close()
                self.file = open(os.path.join(self.curr_dir, '_intro.txt'), 'wt')
            elif data.type != Type.CHAPTER_CONTENT:
                print(f'Unrecognized data type: {data.type}')
                return

            self.file.write(data.content + '\n')
        else:
            index = data.get('original_index') if not self.correct and data.has('original_index') else data.index
            filename = purify_name(data.format(self.formats[data.type]['filename'], index=index))
            title = data.format(self.formats[data.type]['title'], index=index)

            # If there is a validation error, print on the terminal
            if self.debug and data.error:
                print(data.error)
                if self.correct:
                    print(f'\t- Adjusted to {title}')

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