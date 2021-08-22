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
        - index_group (int, optional, default=0): The group index for the title's order/index (starting from 0).
        - content_group (int, optional, default=1): The group index for the title's content (starting from 0).
        - tag (str, optional): The tag for this data. Sometimes there may exist several independent sets of indices
          within the same book; for example, there might be two different Introductions by different authors before the
          first chapter, or there might be several interludes across the volume. In such case, one can attach a tag to
          the data, and have a special Validator that only checks for that tag.
        """
        self.type = Type[args['type'].upper()]
        self.regex = re.compile(args['regex'])
        self.index_group = args.get('index_group', 0) + 1
        self.content_group = args.get('content_group', 1) + 1
        self.tag = args.get('tag', None)

    def process(self, data: NovelData) -> NovelData:
        m = self.regex.match(data.content)
        if m:
            try:
                index = to_num(m[self.index_group])
                title = m[self.content_group].strip()
                tag = {'tag': self.tag} if self.tag else {}
                return NovelData(title, self.type, index, **(data.others | tag))
            except ValueError:  # Not a valid number
                return data

        return data
