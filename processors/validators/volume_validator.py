from common import NovelData, Type
from .validator import Validator


class VolumeValidator(Validator):
    def check(self, data: NovelData) -> bool:
        return data.data_type == Type.VOLUME_TITLE and ((self.special_field is None and data.index >= 0) or (
                    self.special_field is not None and data.index < 0))

    def duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Duplicate volume - expected: {corrected_index}, actual: {self.format(data)}'

    def missing_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Missing volume - expected: {corrected_index}, actual: {self.format(data)}'
