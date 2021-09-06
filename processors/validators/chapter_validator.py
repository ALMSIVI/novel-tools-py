from common import NovelData, Type, FieldMetadata
from .validator import Validator


class ChapterValidator(Validator):
    """
    Validates a chapter, potentially within a volume.
    """
    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        fields = Validator.required_fields()
        fields += [
            FieldMetadata('discard_chapters', 'bool',
                          description='If set to True, restart indexing at the beginning of each new volume.'),
            FieldMetadata('volume_tag', 'str', default=None,
                          description='Only validates if the current volume is the given tag.')
        ]
        return fields

    def __init__(self, args):
        args = self.extract_fields(args)
        super().__init__(args)
        self.discard_chapters = args['discard_chapters']
        self.volume_tag = args['volume_tag']

        self.curr_volume = None
        self.validate_curr_volume = True

    def check(self, data: NovelData) -> bool:
        if data.type == Type.VOLUME_TITLE:
            self.validate_curr_volume = self.volume_tag is None or self.volume_tag == data.get('tag')

            self.curr_volume = data
            if self.discard_chapters:
                self.indices.clear()
                self.curr_index = 0
            return False

        return self.validate_curr_volume and data.type == Type.CHAPTER_TITLE and data.index >= 0 and data.get(
            'tag') == self.tag

    def duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Duplicate chapter{self.volume_message} - expected: {corrected_index}, actual: {self.format(data)}'

    def missing_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Missing chapter{self.volume_message} - expected: {corrected_index}, actual: {self.format(data)}'

    @property
    def volume_message(self):
        if self.curr_volume:
            volume_format = self.curr_volume.format('index = {index}, content = {content}')
            return f' in volume ({volume_format})'
        return ''
