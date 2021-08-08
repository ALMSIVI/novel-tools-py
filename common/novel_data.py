from copy import deepcopy
from .type import Type

class NovelData:
    '''
    Represents an intermediate object of the worker.
    - type: Indicates the type of the match.
    - content: If the type is not a title, then the content will be the matcher's input. If a title is matched, then content will be the title name.
    - index: A unique identifier for the title (if matched).
        - For regular titles, the id should be positive and self-increasing. This is required for duplicate/missing index detection.
        - For special titles, the id should be negative.
    - error: If there is an error during processing, this field will be populated with the error message.
    - order: Internal order of the split result.
    - others: Contains additional data needed for processers/writers here.
    '''

    def __init__(self, type: Type, content: str, index: int = None, error: str = None, order: int = None, **kwargs):
        self.type = type
        self.content = content
        self.index = index
        self.error = error
        self.order = order
        self.others = kwargs

    def has(self, key: str) -> bool:
        return key in self.others

    def get(self, key: str):
        return self.others.get(key)

    def set(self, **kwargs):
        self.others |= kwargs

    def copy(self):
        return deepcopy(self)