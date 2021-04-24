from abc import ABC, abstractmethod
from matchers import Matcher, MatchResult


class Validator(ABC):
    indices = set()
    curr_index = 0

    def clear(self):
        self.indices = set()
        self.curr_index = 0

    def validate(self, matcher: Matcher, result: MatchResult):
        # Duplicate detection
        if result.index in self.indices:
            print(self.duplicate_message(matcher, result))

        self.indices.add(result.index)

        # Do not validate special titles (those with negative index values)
        if result.index < 0:
            return

        # Missing detection
        if self.curr_index != 0 and self.curr_index + 1 != result.index:
            print(self.missing_message(matcher, result))

        self.curr_index = result.index

    @abstractmethod
    def duplicate_message(self, matcher: Matcher, result: MatchResult):
        pass

    @abstractmethod
    def missing_message(self, matcher: Matcher, result: MatchResult):
        pass


class VolumeValidator(Validator):
    def duplicate_message(self, matcher: Matcher, result: MatchResult):
        return f'Potential duplicate volume: {matcher.format(result)}'

    def missing_message(self, matcher: Matcher, result: MatchResult):
        return f'Potential missing volume: {self.curr_index + 1}'


class ChapterValidator(Validator):
    curr_volume = '正文'

    def duplicate_message(self, matcher: Matcher, result: MatchResult):
        return f'Potential duplicate chapter in volume {self.curr_volume}: {matcher.format(result)}'

    def missing_message(self, matcher: Matcher, result: MatchResult):
        return f'Potential missing chapter in volume {self.curr_volume}: {self.curr_index + 1}'
