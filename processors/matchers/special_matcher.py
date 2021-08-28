import re
from framework import Processor
from common import NovelData, Type, ACC, FieldMetadata


class SpecialMatcher(Processor, ACC):
    """
    Accepts a line in a book and matches a special title, whose affixes are in the given list. Examples of special
    titles include Introduction, Foreword, or Conclusion.

    As they usually don't have a regular index, they will be assigned negative values, depending on their order in the
    list. The use of negative values is to avoid collision with regular titles in validators. Additionally, an "affix"
    field will be attached to the object.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('type', 'str',
                          description='Specifies the type for this matcher.'),
            FieldMetadata('affixes', 'list[str]',
                          description='List of special names to match for.'),
            FieldMetadata('regex', 'str',
                          description='The regex to match for. It will contain a "affixes" format, that will be '
                                      'replaced with the list of affixes. Example: ^{affixes}$ will match lines with '
                                      'any of the affixes.'),
            FieldMetadata('affix_group', 'int', default=0,
                          description='The group index for the title\'s affix (starting from 0).'),
            FieldMetadata('content_group', 'int', default=1,
                          description='The group index for the title\'s content (starting from 0).'),
            FieldMetadata('tag', 'str', default='special',
                          description='The tag to append to matched data. This can be used in TitleValidator for '
                                      'different formats.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.type = Type[args['type'].upper()]
        self.affixes = args['affixes']
        affix_str = '|'.join(self.affixes)
        self.regex = re.compile(args['regex'].format(affixes=f'({affix_str})'))
        self.affix_group = args['affix_group'] + 1
        self.content_group = args['content_group'] + 1
        self.tag = args['tag']

    def process(self, data: NovelData) -> NovelData:
        m = self.regex.match(data.content)
        if m:
            for i in range(len(self.affixes)):
                if m[self.affix_group] == self.affixes[i]:
                    title = m[self.content_group].strip()
                    tag = {'tag': self.tag} if self.tag else {}
                    return NovelData(title, self.type, -i - 1, affix=self.affixes[i], **(data.others | tag))

        return data
