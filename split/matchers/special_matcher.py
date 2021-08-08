import re
from framework import Processor
from common import NovelData, Type

class SpecialMatcher(Processor):
    '''Accepts a line in a book and matches a special chapter, whose prefix is in the given dict.'''

    def __init__(self, args):
        '''
        Arguments:
        - type (str): Specifies the type for this matcher.
        - prefixes (list[str]): List of special names to match for.
        - regex (str): The regex to match for. It will contain a "prefex" format, that will be replaced with the list of prefixes.
        '''
        self.type = Type[args['type'].upper()]
        self.prefixes = args['prefixes']
        prefix_str = '|'.join(self.prefixes)
        self.regex = re.compile(args['regex'].format(prefixes=f'({prefix_str})'))

    def process(self, data: NovelData) -> NovelData:
        m = self.regex.match(data.content)
        if m:
            for i in range(len(self.prefixes)):
                if m[0] == self.prefixes[i]:
                    title = m[2].strip()
                    # Use negative number to avoid colliding with numbered titles
                    return NovelData(self.type, title, -i - 1, data.error, data.order, **data.others)

        return data.copy()