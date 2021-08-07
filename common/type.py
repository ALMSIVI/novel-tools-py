from enum import Enum

class Type(Enum):
    BOOK_INTRO = 1
    VOLUME_TITLE = 2
    VOLUME_INTRO = 3
    CHAPTER_TITLE = 4
    CHAPTER_CONTENT = 5
    UNRECOGNIZED = 6