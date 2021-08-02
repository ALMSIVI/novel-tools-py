from split.validators.validator import Validator
from split.matchers import *

class ChapterValidator(Validator):
    curr_volume = '正文'

    def duplicate_message(self, matcher: Matcher, result: MatchResult) -> str:
        return f'Potential duplicate chapter in volume {self.curr_volume}: {matcher.format(result)}'

    def missing_message(self, matcher: Matcher, result: MatchResult) -> str:
        return f'Potential missing chapter in volume {self.curr_volume}: {self.curr_index + 1} (original chapter: {matcher.format(result)})'
