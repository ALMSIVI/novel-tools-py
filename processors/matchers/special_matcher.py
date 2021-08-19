import re
from framework import Processor
from common import NovelData, Type
from utils import to_num


class SpecialMatcher(Processor):
    """
    Accepts a line in a book and matches a special title, whose prefixes are in the given list. Examples of special
    titles include Introduction, Foreword, or Conclusion. As they usually don't have a regular index, they will be
    assigned negative values, depending on their order in the list. The use of negative values is to avoid collision
    with regular titles in validators.

    Sometimes there may be multiples of these special titles. For example, there might be multiple intros by different
    authors, or for different versions. In such cases, if an index is specified in the regex, a 'special_index' field
    will be attached to the NovelData.
    """

    def __init__(self, args):
        """
        Arguments:

        - type (str): Specifies the type for this matcher.
        - affixes (list[str]): List of special names to match for.
        - regex (str): The regex to match for. It will contain a "affixes" format, that will be replaced with the list
          of affixes. Example: ^{affixes}$ will match lines with any of the affixes.
        - affix_group (int, optional, default=0): The group index for the title's affix (starting from 0).
        - index_group (int, optional, default=-1): The group index for the title's order/index (starting from 0), if
          such exists. -1 represents Do Not Find.
        - content_group (int, optional, default=1): The group index for the title's content (starting from 0).
        """
        self.type = Type[args['type'].upper()]
        self.affixes = args['affixes']
        affix_str = '|'.join(self.affixes)
        self.regex = re.compile(args['regex'].format(affixes=f'({affix_str})'))
        self.affix_group = args.get('affix_group', 0) + 1
        self.index_group = args.get('index_group', -1) + 1
        self.content_group = args.get('content_group', 1) + 1

    def process(self, data: NovelData) -> NovelData:
        m = self.regex.match(data.content)
        if m:
            for i in range(len(self.affixes)):
                if m[self.affix_group] == self.affixes[i]:
                    title = m[self.content_group].strip()
                    if self.index_group == 0:
                        return NovelData(title, self.type, -i - 1, **data.others)
                    else:
                        try:
                            index = to_num(m[self.index_group])
                            return NovelData(title, self.type, -i - 1, **data.others, special_index=index)
                        except ValueError:
                            return data

        return data
