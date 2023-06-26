from pydantic import BaseModel, Field
from typing import Pattern
from novel_tools.framework import NovelData, Type, Processor
from novel_tools.utils import to_num


class Options(BaseModel):
    type: str = Field(description='Specifies the type for this matcher.')
    regex: Pattern = Field(description='The regex to match for. It will contain two groups: the first group is the '
                                       'index, the second (optional) is the title.')
    index_group: int = Field(default=0, description='The group index for the title\'s order/index (starting from 0).')
    content_group: int = Field(default=1, description='The group index for the title\'s content (starting from 0). '
                                                      'Use -1 if there is no content.')
    tag: str | None = Field(description='The tag to append to matched data. Sometimes there may exist several '
                                        'independent sets of indices within the same book; for example, there might '
                                        'be two different Introductions by different authors before the first '
                                        'chapter, or there might be several interludes across the volume. In such '
                                        'case, one can attach a tag to the data, and have a special Validator that '
                                        'only checks for that tag.')


class NumberedMatcher(Processor):
    """Matches a regular chapter/volume, with an index and/or a title."""

    def __init__(self, args):
        options = Options(**args)
        self.type = Type[options.type.upper()]
        self.regex = options.regex
        self.index_group = options.index_group + 1
        self.content_group = options.content_group + 1
        self.tag = options.tag

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
