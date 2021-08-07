from . import Type

class NovelData:
    '''
    Represents an intermediate object of the worker.
    - type: indicates the type of the match.
    - content: if the type is not a title, then the content will be the matcher's input. If a title is matched, then content will be the title name.
    - index: a unique identifier for the title (if matched).
        - For regular titles, the id should be positive and self-increasing. This is required for duplicate/missing index detection.
        - For special titles, the id should be negative.
    - error: If there is an error during processing, this field will be populated with the error message.
    - order: Internal order of the split result.
    '''

    def __init__(self, type: Type, content: str, index: int = None, error: str = None, order: int = None):
        self.type = type
        self.content = content
        self.index = index
        self.error = error
        self.order = index