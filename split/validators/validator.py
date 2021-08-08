from abc import abstractmethod
from framework import Processor
from common import NovelData

class Validator(Processor):
    def __init__(self, args):
        '''
        Arguments:
        - discard_chapters (bool): If set to True, restart indexing at the beginning of each new volume.
        - correct (bool): If set to True, automatically correct the indices.
        - verbose (optional, bool): If set to True, will keep a copy of the uncorrected index in the others field. Default is False.
        '''
        self.discard_chapters = args['discard_chapters']
        self.correct = args['correct']
        self.verbose = args.get('verbose', False)

    def before(self):
        self.indices = set()
        self.curr_index = 0

    def process(self, data: NovelData) -> NovelData:
        '''
        Validates the index, and tries to fix any errors if the correct flag is set to true.
        Returns a copy of the original result if correct is false, or a fixed result if true.
        '''
        new_data = data.copy()
        if self.verbose and not data.has('original_index'):
            new_data.set(original_index=data.index)

        if not self.precheck(data):
            return new_data

        # Duplicate detection
        if data.index in self.indices:
            # Auto fix by trying attempting to increase the index (positive only)
            if self.correct:
                while new_data.index in self.indices:
                    new_data.index += 1

            new_data.error = self.duplicate_message(data)

        # Missing detection
        if self.curr_index != 0 and self.curr_index + 1 != new_data.index:
            if self.correct:
                new_data.index = self.curr_index + 1

            new_data.error = self.missing_message(data)

        self.indices.add(new_data.index)
        self.curr_index = new_data.index
        return new_data

    def format(self, result: NovelData) -> str:
        return result.format('index = {index}, title = {content}')

    @abstractmethod
    def precheck(self, data: NovelData) -> bool:
        '''Performs a check as of whether to validate the object. If it returns false, skip validation and move on.'''
        pass

    @abstractmethod
    def duplicate_message(self, data: NovelData) -> str:
        pass

    @abstractmethod
    def missing_message(self, data: NovelData) -> str:
        pass