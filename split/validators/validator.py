from abc import ABC, abstractmethod
from split.matchers import *

class ValidateResult:
    '''
    - status (str): If there is no error in validation, this will be None. If there is an error (duplicate/missing), this will be the error message.
    - title (str): the processed title name, if the match is successful.
    - index (int): a unique identifier for the title.
        - For regular titles, the ids should be positive and self-increasing. This is required for duplicate/missing index detection.
        - For special titles, the ids should be negative.
    '''

    def __init__(self, error: str, index: int, title: str):
        self.error = error
        self.index = index
        self.title = title


class Validator(ABC):
    def __init__(self):
        self.indices = set()
        self.curr_index = 0

    def validate(self, matcher: Matcher, match_result: MatchResult, correct: bool) -> ValidateResult:
        '''
        Validates the index, and tries to fix any errors if the correct flag is set to true.
        Returns a copy of the original result if correct is false, or a fixed result if true.
        '''
        val_result = ValidateResult(None, match_result.index, match_result.title)

        # Do not validate special titles (those with negative index values)
        if match_result.index < 0:
            self.indices.add(val_result.index)
            return val_result

        # Duplicate detection
        if match_result.index in self.indices:
            # Auto fix by trying attempting to increase the index (positive only)
            if correct:
                while val_result.index in self.indices:
                    val_result.index += 1

            val_result.status = self.duplicate_message(matcher, match_result)

        # Missing detection
        if self.curr_index != 0 and self.curr_index + 1 != val_result.index:
            if correct:
                val_result.index = self.curr_index + 1

            val_result.status = self.missing_message(matcher, match_result)

        self.indices.add(val_result.index)
        self.curr_index = val_result.index
        return val_result

    @abstractmethod
    def duplicate_message(self, matcher: Matcher, result: MatchResult) -> str:
        pass

    @abstractmethod
    def missing_message(self, matcher: Matcher, result: MatchResult) -> str:
        pass