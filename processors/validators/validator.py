from abc import abstractmethod
from framework import Processor
from common import NovelData


class Validator(Processor):
    """
    Validates whether the title indices are continuous, i.e., whether there exist duplicate of missing chapter indices.
    """

    def __init__(self, args):
        """
        Arguments:

        - overwrite (bool, optional, default=True): If set to True, will overwrite the old index with the corrected one,
          and keep the original index in the 'original_index' field. If set to False, the corrected index will be stored
          in the 'corrected_index' field.

          In either case, a field called 'error' will be created if a validation error occurs.

        - special_field (bool | str, optional, default=False): Irregular titles usually have negative indices, but some
          will have a custom field specifying its index within these special titles. If this field is set to False, the
          validator will use the built-in index. If set to True, will validate the default field 'special_index'. One
          can also customize the field name by using a string instead of a boolean.

          Notice that, if this field is set, then the validator will NOT validate regular titles. If you want to
          validate both regular titles and special titles, please use two validators, one for each type of title.
        """
        self.overwrite = args.get('overwrite', True)
        if 'special_field' not in args or args['special_field'] == False:
            self.special_field = None
        elif type(args['special_field']) is str:
            self.special_field = args['special_field']
        else:
            # value is True
            self.special_field = 'special_index'

        self.indices = set()
        self.curr_index = 0

    def process(self, data: NovelData) -> NovelData:
        """
        Validates the index, and tries to fix any errors if the correct flag is set to true.
        Returns a copy of the original result if correct is false, or a fixed result if true.
        """
        new_data = data.copy()
        corrected_index = self.get_index(data)

        if not self.check(data):
            self.set_index(new_data, corrected_index)
            return new_data

        # Duplicate detection
        if corrected_index in self.indices:
            # Auto fix by trying attempting to increase the index (positive only)
            while corrected_index in self.indices:
                corrected_index += 1

            new_data.set(error=self.duplicate_message(data, corrected_index))

        # Missing detection
        if self.curr_index != 0 and self.curr_index + 1 != corrected_index:
            corrected_index = self.curr_index + 1

            new_data.set(error=self.missing_message(data, corrected_index))

        self.indices.add(corrected_index)
        self.curr_index = corrected_index
        self.set_index(new_data, corrected_index)
        return new_data

    def get_index(self, data: NovelData):
        return data.index if self.special_field is None else data.get(self.special_field)

    def set_index(self, data: NovelData, corrected_index: int):
        if self.overwrite:
            if self.special_field is None:
                original_index = data.index
                data.index = corrected_index
            else:
                original_index = data.get(self.special_field)
                data.set(**{self.special_field: corrected_index})

            data.set(original_index=original_index)
        else:
            data.set(corrected_index=corrected_index)

    def format(self, result: NovelData) -> str:
        format_str = 'index = {index}, content = {content}' if self.special_field is None else \
            f'index = {{{self.special_field}}}, content = {{content}}'

        return result.format(format_str)

    @abstractmethod
    def check(self, data: NovelData) -> bool:
        """Performs a check as of whether to validate the object. If it returns false, skip validation and move on."""
        pass

    @abstractmethod
    def duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        pass

    @abstractmethod
    def missing_message(self, data: NovelData, corrected_index: int) -> str:
        pass
