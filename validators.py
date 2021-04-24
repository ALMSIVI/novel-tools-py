from abc import ABC, abstractmethod
from matchers import Matcher, MatchResult


class Validator(ABC):
    indices = set()
    curr_index = 0

    def clear(self):
        self.indices = set()
        self.curr_index = 0

    def validate(self, matcher: Matcher, result: MatchResult, correct: bool) -> MatchResult:
        '''
        Validates the index, and tries to fix any errors if the correct flag is set to true.
        Returns a copy of the original result if correct is false, or a fixed result if true.
        '''
        new_result = MatchResult(result.status, result.index, result.title)

        # Do not validate special titles (those with negative index values)
        if result.index < 0:
            self.indices.add(new_result.index)
            return new_result

        # Duplicate detection
        if result.index in self.indices:
            print(self.duplicate_message(matcher, result))
            # Auto fix by trying attempting to increase the index (positive only)
            if correct:
                while new_result.index in self.indices:
                    new_result.index += 1

                print(f'    - Adjusted to {matcher.format(new_result)}')

        # Missing detection
        if self.curr_index != 0 and self.curr_index + 1 != new_result.index:
            print(self.missing_message(matcher, result))
            if correct:
                new_result.index = self.curr_index + 1
                print(f'    - Adjusted to {matcher.format(new_result)}')

        self.indices.add(new_result.index)
        self.curr_index = new_result.index
        return new_result

    @abstractmethod
    def duplicate_message(self, matcher: Matcher, result: MatchResult) -> str:
        pass

    @abstractmethod
    def missing_message(self, matcher: Matcher, result: MatchResult) -> str:
        pass


class VolumeValidator(Validator):
    def duplicate_message(self, matcher: Matcher, result: MatchResult) -> str:
        return f'Potential duplicate volume: {matcher.format(result)}'

    def missing_message(self, matcher: Matcher, result: MatchResult) -> str:
        return f'Potential missing volume: {self.curr_index + 1}'


class ChapterValidator(Validator):
    curr_volume = '正文'

    def duplicate_message(self, matcher: Matcher, result: MatchResult) -> str:
        return f'Potential duplicate chapter in volume {self.curr_volume}: {matcher.format(result)}'

    def missing_message(self, matcher: Matcher, result: MatchResult) -> str:
        return f'Potential missing chapter in volume {self.curr_volume}: {self.curr_index + 1} (current chapter: {matcher.format(result)})'
