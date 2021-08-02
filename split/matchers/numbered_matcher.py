import re
from split.matchers import *
from split.matchers.utils import to_num, purify_name

class NumberedMatcher(Matcher):
    '''Matches a regular chapter/volume, with an index and/or a title.'''

    def __init__(self, args):
        '''
        Arguments:
        - regex: The regex to match for. It will contain two groups: the first group is the index, the second (optional) is the title.
        - format: The format for the chapter/volume.
        '''
        self.regex = re.compile(args['regex'])
        self.format_str = args['format']

    def match(self, line: str) -> MatchResult:
        m = self.regex.match(line)
        if m:
            try:
                index = to_num(m[1])
                title = m[2].strip()
                return MatchResult(True, index, title)
            except:  # Not a valid number
                return MatchResult(False, None, None)

        return MatchResult(False, None, None)

    def format(self, result: MatchResult) -> str:
        return self.format_str.format(index=result.index, title=result.title)

    def filename(self, result: MatchResult) -> str:
        return purify_name(self.format(result))
