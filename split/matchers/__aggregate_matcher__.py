from framework import Processor
from common import NovelData, Type

class __AggregateMatcher__(Processor):
    '''
    *** INTERNAL CLASS ***
    Accepts a line and matches against the given list of regular Matchers.
    If one Matcher returns a non-UNRECOGNIZED result, that will be returned.
    If all Matchers return UNRECOGNIZED, then the original data is returned.
    '''

    def __init__(self, args: list[Processor]):
        self.matchers = args
    
    def before(self):
        for matcher in self.matchers:
            matcher.before()
    
    def after(self):
        for matcher in self.matchers:
            matcher.after()

    def process(self, data: NovelData) -> NovelData:
        for matcher in self.matchers:
            new_data = matcher.process(data)
            if new_data.type != Type.UNRECOGNIZED:
                return new_data

        return data