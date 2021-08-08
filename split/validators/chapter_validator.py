from common import NovelData, Type
from .validator import Validator

class ChapterValidator(Validator):
    curr_volume = None

    def precheck(self, data: NovelData) -> bool:
        if data.type == Type.VOLUME_TITLE:
            self.curr_volume = data.content[1]
            if self.discard_chapters:
                self.indices.clear()
            return False
        if data.type == Type.CHAPTER_TITLE:
            # Do not validate special titles (those with negative index values)
            if data.index < 0:
                self.indices.add(data.index)
                return False

            return True

        return False

    def duplicate_message(self, data: NovelData) -> str:
        if self.curr_volume:
            return f'Potential duplicate chapter in volume {self.curr_volume}: {self.format(data)}'
        return f'Potential duplicate chapter: {self.format(data)}'

    def missing_message(self, data: NovelData) -> str:
        if self.curr_volume:
            return f'Potential missing chapter in volume {self.curr_volume}: {self.curr_index + 1} (current chapter: {self.format(data)})'
        return f'Potential missing chapter: {self.curr_index + 1} (current chapter: {self.format(data)})'
