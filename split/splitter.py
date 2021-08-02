import os
from split.matchers import *
from split.validators import *
from split.split_base import SplitBase

class Splitter(SplitBase):
    '''
    Splits a whole txt file into individual chapters, with possible volume subdirectories.
    The input file is default to utf8 encoding. If it is encoded in GB2312 you need to convert it first.
    Ensure that the file starts directly with a volume/chapter name, without anything else.
    '''
    def before(self, in_dir: str):
        self.out_dir = in_dir if self.out_dir is None else self.out_dir
        self.chapter = None
        self.curr_dir = os.path.join(self.out_dir, '正文')  # Default volume name

    def after(self):
        pass

    def volume_match(self, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        self.curr_dir = os.path.join(self.out_dir, matcher.filename(val_result))
        if not os.path.isdir(self.curr_dir):
            os.mkdir(self.curr_dir)

        if self.chapter is not None:
            self.chapter.close()  # Close current chapter
            self.chapter = None

         # If there is a validation error, print on the terminal
        if self.debug and val_result.error is not None:
            print(val_result.error)
            if self.correct:
                print(f'\t- Adjusted to {matcher.format(val_result)}')


    def chapter_match(self, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        # Close previous chapter file
        if self.chapter is not None:
            self.chapter.close()
        if not os.path.isdir(self.curr_dir):
            os.mkdir(self.curr_dir)
        self.chapter = open(os.path.join(self.curr_dir, matcher.filename(val_result) + '.md'), 'w', encoding='utf8')
        self.chapter.write('# ' + matcher.format(val_result) + '\n') 

        # If there is a validation error, print on the terminal
        if self.debug and val_result.error is not None:
            print(val_result.error)
            if self.correct:
                print(f'\t- Adjusted to {matcher.format(val_result)}')


    def regular_line(self, line: str, line_num: int):
        if self.chapter is not None:
            self.chapter.write(line)
            if line != '':
                self.chapter.write('\n')

    def after(self):
        if self.chapter is not None:
            self.chapter.close()
