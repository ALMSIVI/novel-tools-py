from copy import deepcopy
from enum import Enum, auto


class Type(Enum):
    BOOK_TITLE = auto()
    BOOK_INTRO = auto()
    VOLUME_TITLE = auto()
    VOLUME_INTRO = auto()
    CHAPTER_TITLE = auto()
    CHAPTER_CONTENT = auto()
    UNRECOGNIZED = auto()
    BLANK = auto()

    def __str__(self):
        return self.name


class NovelData:
    """
    Represents an intermediate object of the worker.
    - type: Indicates the type of the match.
    - content: If the type is not a title, then the content will be the matcher's input. If a title is matched, then
      content will be the title name.
    - index: A unique identifier for the title (if matched).
        - For regular titles, the id should be positive and self-increasing. This is required for duplicate/missing
          index detection.
        - For special titles, the id should be negative.
    - error: If there is an error during processing, this field will be populated with the error message.
    - others: Contains additional data needed for processors/writers here.
    """

    def __init__(self, content: str, data_type: Type = Type.UNRECOGNIZED, index: int = None, **kwargs):
        self.content = content
        self.type = data_type
        self.index = index
        self.others = kwargs

    def has(self, key: str) -> bool:
        return self.others and key in self.others

    def get(self, key: str, default=None):
        return self.others.get(key, default)

    def set(self, **kwargs):
        self.others |= kwargs

    def pop(self, key: str):
        return self.others.pop(key)

    def format(self, format_str: str, **kwargs):
        """Formats the novel data by a given format string. Use kw to overwrite existing fields if necessary."""
        return format_str.format(**(self.to_dict() | kwargs))

    def to_dict(self, fields: list[str] = None):
        full_dict = self.others | {
            'type': self.type,
            'content': self.content,
            'index': self.index,
        }

        if fields is None:
            return full_dict

        return {field: full_dict[field] for field in fields}

    def copy(self):
        return deepcopy(self)
