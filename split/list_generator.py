import csv, os
from .matchers import *
from .validators import *
from .split_base import SplitBase

class ListGenerator(SplitBase):
    '''
    Generates a volume/chapter list as a csv file, without splitting the chapters into their respective text files.
    '''
    def before(self, in_dir: str):
        out_dir = in_dir if self.out_dir is None else self.out_dir
        self.out_file = open(os.path.join(out_dir, 'list.csv'), 'wt')

        field_names = ['type', 'text', 'index', 'name', 'formatted']
        if self.correct:
            field_names += ['c_index', 'c_name', 'c_formatted']
        if self.debug:
            field_names += ['line', 'error']

        self.writer = csv.writer(self.out_file)
        self.writer.writerow(field_names)

    def after(self):
        self.out_file.close() 
    
    def match(self, type: str, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        # Write result to out_file
        self.writer.writerow([
            type, # type
            line, # text
            match_result.index, # index
            match_result.title, # name
            matcher.format(match_result), # formatted
            val_result.index, # c_index
            val_result.title, # c_name,
            matcher.format(val_result), # c_formatted
            line_num, # line_num
            val_result.error if val_result.error is not None else '' # status
        ])

    def volume_match(self, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        self.match('volume', line, line_num, matcher, match_result, val_result)

    def chapter_match(self, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        self.match('chapter', line, line_num, matcher, match_result, val_result)

    def regular_line(self, line: str, line_num: int):
        pass