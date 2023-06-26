from novel_tools.framework import NovelData, Processor


class AggregateMatcher(Processor):
    """
    *** INTERNAL CLASS ***
    Accepts a line and matches against the given list of regular Matchers.
    If one Matcher returns a non-UNRECOGNIZED result, that will be returned.
    If all Matchers return UNRECOGNIZED, then the original data is returned.
    """

    def __init__(self, args: list[Processor]):
        self.matchers = args

    def process(self, data: NovelData) -> NovelData:
        for matcher in self.matchers:
            new_data = matcher.process(data)
            if new_data.get('matched', False):
                new_data.pop('matched')
                return new_data

        return data
