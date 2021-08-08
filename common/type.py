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