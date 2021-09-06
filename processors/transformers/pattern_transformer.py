import re
from typing import Any
from framework import Processor
from common import NovelData, ACC, FieldMetadata


class Unit:
    def __init__(self, data_filter: dict[str, Any], subs: list[dict]):
        self.data_filter = data_filter
        self.subs = subs
        for sub in self.subs:
            sub['pattern'] = re.compile(sub['pattern'])

    def replace(self, data: NovelData):
        data_dict = data.flat_dict()
        if not all(data_dict.get(key) != val for key, val in self.data_filter.items()):
            return data

        content = data.content

        for sub in self.subs:
            pattern = sub['pattern']
            new = sub['new']
            while match := pattern.search(content):
                begin, end = match.span()
                content = content[:begin] + new.format(*match.groups()) + content[end:]

        data.content = content
        return data


class PatternTransformer(Processor, ACC):
    """
    Alters the content of the data by changing some patterns (usually in chapter contents). You can use this to format
    punctuation symbols in the novel, or change from custom dividers to Markdown-style ones.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata("units", 'list[{filter: dict[str, str], subs: list[{pattern: str, new: str}]}]',
                          description='The list of processing units. `filter` is a dictionary with the fields as the '
                                      'key, and `subs` lists the operations to be performed if the data is not '
                                      'filtered. `pattern` is a regex describing the pattern, and `new` is the string '
                                      'to replace the pattern.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.units = [Unit(arg['filter'], arg['subs']) for arg in args['units']]

    def process(self, data: NovelData) -> NovelData:
        for unit in self.units:
            data = unit.replace(data)

        return data
