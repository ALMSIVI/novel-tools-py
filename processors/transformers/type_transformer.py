from framework import Processor
from common import NovelData, Type


class TypeTransformer(Processor):
    """Determines the true type for all data with UNRECOGNIZED type."""

    # noinspection PyUnusedLocal
    def __init__(self, args):
        self.first_line = True
        self.in_volume = False
        self.in_chapter = False

    def process(self, data: NovelData) -> NovelData:
        # Theoretically BLANK can fit anywhere, but they are omitted for concision.
        if data.type == Type.VOLUME_TITLE:
            # After this, should either be volume intro or chapter title.
            self.in_volume = True
            self.in_chapter = False
        elif data.type == Type.CHAPTER_TITLE:
            # After this, should only be chapter content.
            self.in_chapter = True
        elif not data.content:
            # Empty content that is not a title, treat as BLANK.
            data.type = Type.BLANK
        elif not self.in_volume:
            # Outside of volume, should be book metadata or intro. Treat first line as book title.
            data.type = Type.BOOK_TITLE if self.first_line else Type.BOOK_INTRO
        elif not self.in_chapter:
            # Outside of chapter, should be volume intro.
            data.type = Type.VOLUME_INTRO
        else:
            # Inside chapter, should be chapter content.
            data.type = Type.CHAPTER_CONTENT

        self.first_line = False
        return data
