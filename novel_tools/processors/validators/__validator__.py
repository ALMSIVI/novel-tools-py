from pydantic import BaseModel, Field
from abc import abstractmethod
from novel_tools.framework import NovelData, Processor


class BaseOptions(BaseModel):
    overwrite: bool = Field(default=True,
                            description='If set to True, will overwrite the old index with the corrected one, and keep '
                                        'the original index in the \'original_index\' field. If set to False, the '
                                        'corrected index will be stored in the \'corrected_index\' field. In either'
                                        'case, a field called \'error\' will be created if a validation error occurs.')
    tag: str | None = Field(description='Only validate on the given tag. Sometimes there may exist several '
                                        'independent sets of indices within the same book; for example, there might '
                                        'be two different Introductions by different authors before the first '
                                        'chapter, or there might b several interludes across the volume. In such '
                                        'case, one can attach a tag to the data, and have a special Validator that '
                                        'only checks for that tag.')
    begin_index: int = Field(default=1, description='The starting index to validate against.')


class Validator(Processor):
    """
    Validates whether the title indices are continuous, i.e., whether there exist duplicate of missing chapter indices.
    """
    overwrite: bool
    tag: str
    curr_index: int
    indices: set[int]

    def init_fields(self, options: BaseOptions):
        self.overwrite = options.overwrite
        self.tag = options.tag
        self.curr_index = options.begin_index - 1
        self.indices = set()

    def process(self, data: NovelData) -> NovelData:
        """
        Validates the index, and tries to fix any errors if the correct flag is set to true.
        Returns a copy of the original result if correct is false, or a fixed result if true.
        """
        if not self.check(data):
            return data

        new_data = data.copy()
        corrected_index = data.index

        # Duplicate detection
        if corrected_index in self.indices:
            # Auto fix by trying attempting to increase the index (positive only)
            while corrected_index in self.indices:
                corrected_index += 1

            new_data.set(error=self._duplicate_message(data, corrected_index))

        # Missing detection
        if self.curr_index + 1 != corrected_index:
            corrected_index = self.curr_index + 1

            new_data.set(error=self._missing_message(data, corrected_index))

        self.indices.add(corrected_index)
        self.curr_index = corrected_index
        self.__set_index(new_data, corrected_index)
        return new_data

    def __set_index(self, data: NovelData, corrected_index: int):
        if self.overwrite:
            original_index = data.index
            data.index = corrected_index
            data.set(original_index=original_index)
        else:
            data.set(corrected_index=corrected_index)

    @staticmethod
    def _format(result: NovelData) -> str:
        return result.format('index = {index}, content = {content}')

    @abstractmethod
    def check(self, data: NovelData) -> bool:
        """Performs a check as of whether to validate the object. If it returns false, skip validation and move on."""
        pass

    @abstractmethod
    def _duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        pass

    @abstractmethod
    def _missing_message(self, data: NovelData, corrected_index: int) -> str:
        pass
