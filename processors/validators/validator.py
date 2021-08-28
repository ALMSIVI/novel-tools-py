from abc import abstractmethod
from framework import Processor
from common import NovelData, ACC, FieldMetadata


class Validator(Processor, ACC):
    """
    Validates whether the title indices are continuous, i.e., whether there exist duplicate of missing chapter indices.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('overwrite', 'bool', default=True,
                          description='If set to True, will overwrite the old index with the corrected one, and keep '
                                      'the original index in the \'original_index\' field. If set to False, '
                                      'the corrected index will be stored in the \'corrected_index\' field. In either '
                                      'case, a field called \'error\' will be created if a validation error occurs.'),
            FieldMetadata('tag', 'str', default=None,
                          description='Only validate on the given tag. Sometimes there may exist several independent '
                                      'sets of indices within the same book; for example, there might be two '
                                      'different Introductions by different authors before the first chapter, '
                                      'or there might be several interludes across the volume. In such case, '
                                      'one can attach a tag to the data, and have a special Validator that only '
                                      'checks for that tag.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.overwrite = args['overwrite']
        self.tag = args['tag']
        self.indices = set()
        self.curr_index = 0

    def process(self, data: NovelData) -> NovelData:
        """
        Validates the index, and tries to fix any errors if the correct flag is set to true.
        Returns a copy of the original result if correct is false, or a fixed result if true.
        """
        new_data = data.copy()
        corrected_index = data.index

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

    def set_index(self, data: NovelData, corrected_index: int):
        if self.overwrite:
            original_index = data.index
            data.index = corrected_index
            data.set(original_index=original_index)
        else:
            data.set(corrected_index=corrected_index)

    @staticmethod
    def format(result: NovelData) -> str:
        return result.format('index = {index}, content = {content}')

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
