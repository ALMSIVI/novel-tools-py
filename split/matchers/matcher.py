from abc import ABC, abstractmethod
from .match_result import MatchResult

class Matcher(ABC):
    @abstractmethod
    def match(self, line: str) -> MatchResult:
        '''Takes a line of string and attempts a match.'''
        pass

    @abstractmethod
    def format(self, result: MatchResult) -> str:
        '''Takes a match result and returns a formatted name.'''
        pass

    @abstractmethod
    def filename(self, result: MatchResult) -> str:
        '''Takes a match result and returns a valid filename.'''
        pass