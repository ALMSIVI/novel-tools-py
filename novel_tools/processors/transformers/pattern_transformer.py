from pydantic import BaseModel, Field
from typing import Pattern
from novel_tools.framework import Processor
from novel_tools.common import NovelData


class Substitution(BaseModel):
    pattern: Pattern
    new: str


class Unit(BaseModel):
    filter: dict[str, str]
    subs: list[Substitution]

    def replace(self, data: NovelData):
        data_dict = data.flat_dict()
        if not all(data_dict.get(key) != val for key, val in self.filter.items()):
            return data

        content = data.content

        for sub in self.subs:
            pattern = sub.pattern
            new = sub.new
            while match := pattern.search(content):
                begin, end = match.span()
                content = content[:begin] + new.format(*match.groups()) + content[end:]

        data.content = content
        return data


class Options(BaseModel):
    units: list[Unit] = Field(description='The list of processing units. `filter` is a dictionary with the fields as '
                                          'the key, and `subs` lists the operations to be performed if the data is '
                                          'not filtered. `pattern` is a regex describing the pattern, and `new` is '
                                          'the string to replace the pattern.')


class PatternTransformer(Processor):
    """
    Alters the content of the data by changing some patterns (usually in chapter contents). You can use this to format
    punctuation symbols in the novel, or change from custom dividers to Markdown-style ones.
    """

    def __init__(self, args):
        options = Options(**args)
        self.units = options.units

    def process(self, data: NovelData) -> NovelData:
        for unit in self.units:
            data = unit.replace(data)

        return data
