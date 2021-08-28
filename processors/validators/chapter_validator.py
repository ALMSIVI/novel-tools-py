from common import NovelData, Type
from .validator import Validator


class ChapterValidator(Validator):
    def __init__(self, args):
        """
         Arguments (apart from those inherited from Validator):

        - discard_chapters (bool): If set to True, restart indexing at the beginning of each new volume.
        - volume_special_field (bool | str, optional, default=False): Similar to special_field, but only applies to the
          volume. The volume is not used for validation, only for outputting error messages. So volume will be processed
          regardless of whether the volume is a special volume. This field only specifies what field to look for if a
          special volume is found.
        """
        super().__init__(args)
        self.discard_chapters = args['discard_chapters']
        if 'volume_special_field' not in args or args['volume_special_field'] is False:
            self.volume_special_field = None
        elif args['volume_special_field'] is True:
            self.volume_special_field = 'volume_special_field'
        else:
            self.volume_special_field = args['volume_special_field']

        self.curr_volume = None

    def check(self, data: NovelData) -> bool:
        if data.type == Type.VOLUME_TITLE:
            self.curr_volume = data
            if self.discard_chapters:
                self.indices.clear()
                self.curr_index = 0
            return False

        return data.type == Type.CHAPTER_TITLE and data.index >= 0 and data.get('tag', None) == self.tag

    def duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Duplicate chapter{self.volume_message} - expected: {corrected_index}, actual: {self.format(data)}'

    def missing_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Missing chapter{self.volume_message} - expected: {corrected_index}, actual: {self.format(data)}'

    @property
    def volume_message(self):
        return f' in volume ({self.curr_volume_formatted})' if self.curr_volume else ''

    @property
    def curr_volume_formatted(self):
        format_str = 'index = {index}, content = {content}' \
            if self.volume_special_field is None or not self.curr_volume.has(self.volume_special_field) \
            else f'index = {{{self.volume_special_field}}}, content={{content}}'
        return self.curr_volume.format(format_str)
