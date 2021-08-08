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
            - title: Format string that contains {index} and {title} to be formatted. Will be written to the top of the file.
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
        self.chapter = None
        self.curr_dir = os.path.join(self.out_dir, self.default_volume)

    def after(self):
        if self.chapter:
            self.chapter.close()

    def write(self, data: NovelData):
        if data.type not in self.formats: # Normally, should only contain volume and chapter titles
            if self.chapter:
                self.chapter.write(data.content)
                if data.content != '':
                    self.chapter.write('\n')
        else:
            index = data.get('original_index') if self.correct and data.has('original_index') else data.index
            filename = purify_name(self.formats[data.type]['filename'].format(index=index, title=data.content))
            title = self.formats[data.type]['title'].format(index=data.index, title=data.content)

            # If there is a validation error, print on the terminal
            if self.debug and data.error:
                print(data.error)
                if self.correct:
                    print(f'\t- Adjusted to {title}')

            if data.type == Type.VOLUME_TITLE:
                self.curr_dir = os.path.join(self.out_dir, filename)
                if not os.path.isdir(self.curr_dir):
                    os.mkdir(self.curr_dir)

                if self.chapter:
                    self.chapter.close()  # Close current chapter
                    self.chapter = None
            elif data.type == Type.CHAPTER_TITLE:
                # Close previous chapter file
                if self.chapter:
                    self.chapter.close()

                if not os.path.isdir(self.curr_dir):
                    os.mkdir(self.curr_dir)

                self.chapter = open(os.path.join(self.curr_dir, filename + '.txt'), 'wt')
                self.chapter.write(title + '\n') 
