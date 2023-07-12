from copy import deepcopy
from dataclasses import dataclass
from enum import Enum


class Type(str, Enum):
    BOOK_TITLE = 'BOOK_TITLE'
    BOOK_INTRO = 'BOOK_INTRO'
    VOLUME_TITLE = 'VOLUME_TITLE'
    VOLUME_INTRO = 'VOLUME_INTRO'
    CHAPTER_TITLE = 'CHAPTER_TITLE'
    CHAPTER_CONTENT = 'CHAPTER_CONTENT'
    UNRECOGNIZED = 'UNRECOGNIZED'


class Index:
    # The regular index for numbered chapters/volumes (should be self increasing), and the internal index for special
    # chapters/volumes.
    index: int
    sub_index: str | int
    tag: str
    order: int


class Content:
    content: str
    # If the data is an indexed type, this field contains the indexed part. For example, for a chapter title
    # "Chapter 1. Rain", content would be "Rain" while formatted would contain "Chapter 1.".
    formatted: str
    raw: str


@dataclass(init=False)
class NovelData:
    """
    Represents an intermediate object of the worker.
    """
    content: Content
    index: Index
    # Holds any errors during processing.
    error: str
    type: Type = Type.UNRECOGNIZED

    def copy(self):
        return deepcopy(self)
