from ..matchers import *
from .validator import Validator

class VolumeValidator(Validator):
    def duplicate_message(self, matcher: Matcher, result: MatchResult) -> str:
        return f'Potential duplicate volume: {matcher.format(result)}'

    def missing_message(self, matcher: Matcher, result: MatchResult) -> str:
        return f'Potential missing volume: {self.curr_index + 1}'