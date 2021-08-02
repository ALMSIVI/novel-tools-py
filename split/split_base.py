import os
from abc import ABC, abstractmethod
from split.matchers import *
from split.validators import *

class SplitBase(ABC):
    def __init__(self, filename, out_dir, discard_chapters, correct, debug):
        self.filename = filename
        self.out_dir = out_dir
        self.discard_chapters = discard_chapters
        self.correct = correct
        self.debug = debug
        
    def split(self) -> None:
        '''
        Generates a volume/chapter list.
        '''
        in_dir = os.path.dirname(self.filename)
        volume_matchers, chapter_matchers = generate_matchers(in_dir)
        volume_validator = VolumeValidator()
        chapter_validator = ChapterValidator()
        line_num = 0

        self.before(in_dir)

        with open(self.filename, 'rt', encoding='utf8') as file:
            for line in file:
                line_num += 1
                line = line.strip()
                matched = False

                # First check volume name
                for matcher in volume_matchers:
                    match_result = matcher.match(line)
                    if not match_result.success:
                        continue

                    val_result = volume_validator.validate(matcher, match_result, self.correct)

                    # Discard chapter ids between volumes
                    if self.discard_chapters:
                        chapter_validator = ChapterValidator()

                    chapter_validator.curr_volume = matcher.format(val_result)
                    matched = True

                    self.volume_match(line, line_num, matcher, match_result, val_result)
                    break

                if matched: # Volume matched, go to next line
                    continue
                
                # Then check for chapter name
                for matcher in chapter_matchers:
                    match_result = matcher.match(line)
                    if not match_result.success:
                        continue

                    val_result = chapter_validator.validate(matcher, match_result, self.correct)
                    matched = True

                    self.chapter_match(line, line_num, matcher, match_result, val_result)
                    break

                if not matched:
                    self.regular_line(line, line_num)

        self.after()

    @abstractmethod
    def before(self, in_dir: str):
        pass
    
    @abstractmethod
    def after(self):
        pass

    @abstractmethod
    def volume_match(self, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        pass

    @abstractmethod
    def chapter_match(self, line: str, line_num: int, matcher: Matcher, match_result: MatchResult, val_result: ValidateResult):
        pass

    @abstractmethod
    def regular_line(self, line: str, line_num: int):
        pass