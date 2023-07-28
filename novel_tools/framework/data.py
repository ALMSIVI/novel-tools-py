from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Type(str, Enum):
    BOOK_TITLE = 'BOOK_TITLE'
    BOOK_INTRO = 'BOOK_INTRO'
    VOLUME_TITLE = 'VOLUME_TITLE'
    VOLUME_INTRO = 'VOLUME_INTRO'
    CHAPTER_TITLE = 'CHAPTER_TITLE'
    CHAPTER_CONTENT = 'CHAPTER_CONTENT'
    UNRECOGNIZED = 'UNRECOGNIZED'


@dataclass
class Index:
    """
    Attributes:
        index: The regular index for numbered chapters/volumes (should be self increasing), and the internal index for
               special chapters/volumes.
        sub_index: Used to identify chapter parts (e.g., Chapter 1 Part 1).
        tag: Used to identify different index "sets" (e.g., regular chapters and Interludes).
        order: The internal order used by the Worker process.
    """
    index: int
    sub_index: str | int
    tag: str
    order: int


@dataclass
class Source:
    """
    Attributes:
        file: The file which the data originates from. It may be None when the data source is unambiguous, e.g., when
              reading from a single file.
        line_num: The line number which the data originates from.
    """
    file: Path
    line_num: int


@dataclass(init=False)
class Content:
    """
    Attributes:
        formatted: If the data is an indexed type, this field contains the indexed part. For example, for a chapter
                   title "Chapter 1. Rain", content would be "Rain" while formatted would contain "Chapter 1.".
    """
    content: str
    formatted: str
    raw: str


@dataclass(init=False)
class NovelData:
    """
    Represents an intermediate object of the worker.
    Attributes:
        error: Holds any errors during processing.
        matched: Whether a Matcher has successfully matched this data.
    """
    content: Content
    index: Index
    source: Source
    error: str
    type: Type = Type.UNRECOGNIZED
    matched: bool = False

    def copy(self):
        return deepcopy(self)
