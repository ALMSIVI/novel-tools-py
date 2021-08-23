import re
from framework import Processor
from common import NovelData, Type


class SpecialMatcher(Processor):
    """
    Accepts a line in a book and matches a special title, whose affixes are in the given list. Examples of special
    titles include Introduction, Foreword, or Conclusion.

    As they usually don't have a regular index, they will be assigned negative values, depending on their order in the
    list. The use of negative values is to avoid collision with regular titles in validators. Additionally, an "affix"
    field will be attached to the object.
    """

    def __init__(self, args):
        """
        Arguments:

        - type (str): Specifies the type for this matcher.
        - affixes (list[str]): List of special names to match for.
        - regex (str): The regex to match for. It will contain a "affixes" format, that will be replaced with the list
          of affixes. Example: ^{affixes}$ will match lines with any of the affixes.
        - affix_group (int, optional, default=0): The group index for the title's affix (starting from 0).
        - content_group (int, optional, default=1): The group index for the title's content (starting from 0).
        - tag (str, optional): The tag to append to matched data. Sometimes there may exist several independent sets of
          indices within the same book; for example, there might be two different Introductions by different authors
          before the first chapter, or there might be several interludes across the volume. In such case, one can attach
          a tag to the data, and have a special Validator that only checks for that tag.
        """
        self.type = Type[args['type'].upper()]
        self.affixes = args['affixes']
        affix_str = '|'.join(self.affixes)
        self.regex = re.compile(args['regex'].format(affixes=f'({affix_str})'))
        self.affix_group = args.get('affix_group', 0) + 1
        self.content_group = args.get('content_group', 1) + 1
        self.tag = args.get('tag', None)

    def process(self, data: NovelData) -> NovelData:
        m = self.regex.match(data.content)
        if m:
            for i in range(len(self.affixes)):
                if m[self.affix_group] == self.affixes[i]:
                    title = m[self.content_group].strip()
                    tag = {'tag': self.tag} if self.tag else {}
                    return NovelData(title, self.type, -i - 1, affix=self.affixes[i], **(data.others | tag))

        return data
