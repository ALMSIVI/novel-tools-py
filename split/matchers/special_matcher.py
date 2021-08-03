import re
from . import *
from .utils import purify_name

class SpecialMatcher(Matcher):
    '''Matches a special chapter, whose prefix is in the given dict.'''

    def __init__(self, args):
        '''
        Arguments:
        - prefixes: list of special names to match for.
        '''
        self.prefixes = args['prefixes']
        self.regex = re.compile(args['regex'].format(
            prefixes=f'({"|".join(self.prefixes)})'))
        self.format_str = args['format']

    def match(self, line: str) -> MatchResult:
        m = self.regex.match(line)
        if m:
            for i in range(len(self.prefixes)):
                if m[0] == self.prefixes[i]:
                    title = m[2].strip()
                    # Use negative number to avoid colliding with numbered titles
                    return MatchResult(True, -i - 1, title)

        return MatchResult(False, None, None)

    def format(self, result: MatchResult) -> str:
        return self.format_str.format(prefix=self.prefixes[-result.index - 1], title=result.title)

    def filename(self, result: MatchResult) -> str:
        return purify_name(self.format(result))