from novel_tools.framework import NovelData, Type
from .__validator__ import Validator, BaseOptions


class VolumeValidator(Validator):
    """
    Validates a volume.
    """

    def __init__(self, args):
        options = BaseOptions(**args)
        self.init_fields(options)

    def check(self, data: NovelData) -> bool:
        return data.type == Type.VOLUME_TITLE and data.index >= 0 and data.get('tag') == self.tag

    def _duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Duplicate volume - expected: {corrected_index}, actual: {self._format(data)}'

    def _missing_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Missing volume - expected: {corrected_index}, actual: {self._format(data)}'
