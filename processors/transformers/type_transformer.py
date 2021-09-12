from framework import Processor
from common import NovelData, Type, ACC, FieldMetadata


class TypeTransformer(Processor, ACC):
    """Determines the true type for all data with UNRECOGNIZED type."""

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return []

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
        elif self.in_chapter:
            data.type = Type.CHAPTER_CONTENT
        elif self.in_volume:
            data.type = Type.VOLUME_INTRO
        else:
            # Outside of volume, should be book metadata or intro. Treat first line as book title.
            data.type = Type.BOOK_TITLE if self.first_line else Type.BOOK_INTRO

        self.first_line = False
        return data
