from common import NovelData, Type
from .validator import Validator


class VolumeValidator(Validator):
    def check(self, data: NovelData) -> bool:
        if data.data_type == Type.VOLUME_TITLE:
            # Do not validate special titles (those with negative index values)
            if data.index < 0:
                self.indices.add(data.index)
                return False

            return True

        return False

    def duplicate_message(self, data: NovelData) -> str:
        return f'Potential duplicate volume: {self.format(data)}'

    def missing_message(self, data: NovelData) -> str:
        return f'Potential missing volume: {self.curr_index + 1} (current volume: {self.format(data)})'
