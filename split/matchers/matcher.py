from abc import ABC, abstractmethod

class MatchResult:
    '''
    - success (bool): whether the match is successful or not. If it is False, then the rest elements are garbage values.
    - title (str): the processed title name, if the match is successful.
    - index (int): a unique identifier for the title.
        - For regular titles, the ids should be positive and self-increasing. This is required for duplicate/missing index detection.
        - For special titles, the ids should be negative.
    '''

    def __init__(self, success: bool, index: int, title: str):
        self.success = success
        self.index = index
        self.title = title

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