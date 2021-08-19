from common import NovelData, Type
from .validator import Validator


class ChapterValidator(Validator):
    def __init__(self, args):
        """
         Arguments (apart from those inherited from Validator):

        - discard_chapters (bool): If set to True, restart indexing at the beginning of each new volume.
        """
        super().__init__(args)
        self.discard_chapters = args['discard_chapters']
        self.curr_volume = None

    def check(self, data: NovelData) -> bool:
        if data.data_type == Type.VOLUME_TITLE:
            self.curr_volume = data.content[1]
            if self.discard_chapters:
                self.indices.clear()
            return False

        return data.data_type == Type.CHAPTER_TITLE and ((self.special_field is None and data.index >= 0) or (
                self.special_field is not None and data.index < 0))

    def duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Duplicate chapter{self.volume_message} - expected: {corrected_index}, actual: {self.format(data)}'

    def missing_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Missing chapter{self.volume_message} - expected: {corrected_index}, actual: {self.format(data)}'

    @property
    def volume_message(self):
        return f' in volume {self.curr_volume}' if self.curr_volume else ''
