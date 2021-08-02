import os, sys
from split.matchers import *
from split.validators import *
from split.split_base import SplitBase

class TocLister(SplitBase):
    '''
    Lists the table of contents without actually splitting the file. Useful for debugging.
    If out_dir is empty, the table will be printed to the terminal.
    '''

    def before(self, in_dir: str):
        if self.out_dir is None:
            self.out_file = sys.stdout
        elif os.path.isdir(self.out_dir):
            self.out_file = open(os.path.join(self.out_dir, 'toc.txt'), 'wt')
        else:
            self.out_file = open(self.out_dir, 'wt')

        self.volume = None  # Default volume name

    def after(self):
        if self.out_dir != '':
            self.out_file.close()

    def volume_match(self, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        self.volume = matcher.format(val_result)
        self.out_file.write(self.volume)
        if self.debug and val_result.error is not None:
            self.out_file.write('\t' + val_result.error)
        self.out_file.write('\n')


    def chapter_match(self, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        if self.volume is not None:
            self.out_file.write('\t')
        self.out_file.write(matcher.format(val_result))
        if self.debug and val_result.error is not None:
            self.out_file.write('\t' + val_result.error)
        self.out_file.write('\n')

    def regular_line(self, line: str, line_num: int):
        pass