import re
from novel_tools.framework import Processor
from novel_tools.common import NovelData, Type, ACC, FieldMetadata
from novel_tools.utils import to_num


class NumberedMatcher(Processor, ACC):
    """Matches a regular chapter/volume, with an index and/or a title."""

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('type', 'str',
                          description='Specifies the type for this matcher.'),
            FieldMetadata('regex', 'str',
                          description='The regex to match for. It will contain two groups: the first group is the '
                                      'index, the second (optional) is the title.'),
            FieldMetadata('index_group', 'int', default=0,
                          description='The group index for the title\'s order/index (starting from 0).'),
            FieldMetadata('content_group', 'int', default=1,
                          description='The group index for the title\'s content (starting from 0). Use -1 if there is '
                                      'no content.'),
            FieldMetadata('tag', 'str', default=None,
                          description='The tag to append to matched data. Sometimes there may exist several '
                                      'independent sets of indices within the same book; for example, there might be '
                                      'two different Introductions by different authors before the first chapter, '
                                      'or there might be several interludes across the volume. In such case, '
                                      'one can attach a tag to the data, and have a special Validator that only '
                                      'checks for that tag.')
        ]

    def __init__(self, args):
        self.args = self.extract_fields(args)

        self.type = Type[self.args['type'].upper()]
        self.regex = re.compile(self.args['regex'])
        self.index_group = self.args['index_group'] + 1
        self.content_group = self.args['content_group'] + 1
        self.tag = self.args['tag']

    def process(self, data: NovelData) -> NovelData:
        if data.type != Type.UNRECOGNIZED and data.type != self.type:
            return data

        m = self.regex.match(data.content)
        if m:
            try:
                index = to_num(m[self.index_group])
                title = m[self.content_group].strip() if self.content_group != 0 else ''
                tag = {'tag': self.tag} if self.tag else {}
                return NovelData(title, self.type, index, matched=True, **(data.others | tag))
            except ValueError:  # Not a valid number
                return data

        return data
