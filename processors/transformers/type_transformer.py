from framework import Processor
from common import NovelData, Type


class TypeTransformer(Processor):
    """Determines the true type for all data with UNRECOGNIZED type."""

    # noinspection PyUnusedLocal
    def __init__(self, args):
        self.first_line = False
        self.in_volume = False
        self.in_chapter = False

    def process(self, data: NovelData) -> NovelData:
        # At this stage, only title types are assigned now.
        if data.data_type == Type.VOLUME_TITLE:
            self.in_volume = True
            self.in_chapter = False
        elif data.data_type == Type.CHAPTER_TITLE:
            self.in_chapter = True
        elif not data.content:  # Empty string, treat as BLANK
            data.data_type = Type.BLANK
        elif not self.in_volume:  # book metadata or intro
            if self.first_line:  # Treat first line as book title
                data.data_type = Type.BOOK_TITLE
            else:
                data.data_type = Type.BOOK_INTRO
        elif not self.in_chapter:  # volume intro
            data.data_type = Type.VOLUME_INTRO
        else:  # chapter content
            data.data_type = Type.CHAPTER_CONTENT

        self.first_line = True
        return data
