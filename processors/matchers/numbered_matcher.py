import re
from framework import Processor
from common import NovelData, Type
from utils import to_num


class NumberedMatcher(Processor):
    """Accepts a line in a book and matches a regular chapter/volume, with an index and/or a title."""

    def __init__(self, args):
        """
        Arguments:
        - type (str): Specifies the type for this matcher.
        - regex (str): The regex to match for. It will contain two groups: the first group is the index, the second
          (optional) is the title.
        """
        self.type = Type[args['type'].upper()]
        self.regex = re.compile(args['regex'])

    def process(self, data: NovelData) -> NovelData:
        m = self.regex.match(data.content)
        if m:
            try:
                index = to_num(m[1])
                title = m[2].strip()
                return NovelData(self.type, title, index, data.error, **data.others)
            except KeyError:  # Not a valid number
                return data

        return data
