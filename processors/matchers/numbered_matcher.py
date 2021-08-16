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
        - index_group (optional, int): The group index for the title's order/index (starting from 0). Default is 0.
        - content_group (optional, int): The group index for the title's content (starting from 0). Default is 1.
        """
        self.type = Type[args['type'].upper()]
        self.regex = re.compile(args['regex'])
        self.index_group = args.get('index_group', 0) + 1
        self.content_group = args.get('content_group', 1) + 1

    def process(self, data: NovelData) -> NovelData:
        m = self.regex.match(data.content)
        if m:
            try:
                index = to_num(m[self.index_group])
                title = m[self.content_group].strip()
                return NovelData(self.type, title, index, data.error, **data.others)
            except ValueError:  # Not a valid number
                return data

        return data
