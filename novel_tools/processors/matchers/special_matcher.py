from pydantic import BaseModel, Field
import re
from novel_tools.framework import NovelData, Type, Processor


class Options(BaseModel):
    type: str = Field(description='Specifies the type for this matcher.')
    affixes: list[str] = Field(description='List of special names to match for.')
    regex: str = Field(description='The regex to match for. It will contain an "affixes" format, that will be '
                                   'replaced with the list of affixes. Example: ^{affixes}$ will match lines with any '
                                   'of the affixes.')
    affix_group: int = Field(default=0, description='The group index for the title\'s affix (starting from 0).')
    content_group: int = Field(default=1, description='The group index for the title\'s content (starting from 0). '
                                                      'Use -1 if there is no content.')
    tag: str = Field(default='special', description='The tag to append to matched data. This can be used in '
                                                    'TitleValidator for different formats.')


class SpecialMatcher(Processor):
    """
    Matches a special title, whose affixes are in the given list. Examples of special titles include Introduction,
    Foreword, or Conclusion. It can also be used without any affixes, in which you can simply use an empty affix array
    and just match the content.

    As special titles don't have an index, they will be assigned non-positive values, depending on their order in
    the list. It is done to avoid collision with regular titles in validators. Additionally, an "affix" field will be
    attached to the object.
    """

    def __init__(self, args):
        options = Options(**args)

        self.type = Type[options.type.upper()]
        self.affixes = options.affixes
        affix_str = '|'.join(self.affixes)
        self.regex = re.compile(options.regex.format(affixes=f'({affix_str})'))
        self.affix_group = options.affix_group + 1
        self.content_group = options.content_group + 1
        self.tag = options.tag

    def process(self, data: NovelData) -> NovelData:
        if data.type != Type.UNRECOGNIZED and data.type != self.type:
            return data

        m = self.regex.match(data.content)
        if m:
            for i in range(len(self.affixes)):
                if m[self.affix_group] == self.affixes[i]:
                    title = m[self.content_group].strip() if self.content_group != 0 else ''
                    tag = {'tag': self.tag} if self.tag else {}
                    return NovelData(title, self.type, -i - 1, matched=True, affix=self.affixes[i],
                                     **(data.others | tag))

            # If there is a match but no affixes are found, it might be the case that there is no affix at all.
            # In this case, leave the affix empty.
            title = m[self.content_group].strip() if self.content_group != 0 else ''
            tag = {'tag': self.tag} if self.tag else {}
            return NovelData(title, self.type, 0, matched=True, affix='', **(data.others | tag))

        return data
