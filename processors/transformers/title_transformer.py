from typing import Union, Any
from framework import Processor
from common import NovelData, Type, ACC, FieldMetadata


class Unit:
    def __init__(self, title_filter: dict[str, Any], title_format: Union[str, dict[str, str]]):
        self.title_filter = title_filter
        self.title_format = title_format

    def filter(self, data: NovelData) -> bool:
        match = True
        for key, val in self.title_filter.items():
            if key == 'content':
                match = match and data.content == val
            elif key == 'type':
                match = match and data.type == Type[val.upper()]
            elif key == 'index':
                match = match and data.index == val
            else:
                match = match and data.get(key, None) == val

            if not match:
                return match

        return match

    def format(self, data: NovelData) -> NovelData:
        if type(self.title_format) is str:
            data.set(formatted=data.format(self.title_format))
        else:
            formatted = {}
            for key, val in self.title_format.items():
                formatted[key] = data.format(val)

            data.set(**formatted)

        return data


class TitleTransformer(Processor, ACC):
    """
    Formats the title, using the necessary information in the data.

    This class uses a list of "unit" processors. Each unit contains a "filter" and one or two format strings. One can
    filter based on any attribute of the given data, the most important of which include type and tag. If one format
    string is given, then it will be used to fill the "formatted" field. If a dict is given, then it will use the values
    to fill the custom key fields.

    Be careful if you want to use this on non-title data, for most writers use 'formatted' to determine whether the data
    is a title.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('units', 'list[{filter: dict[str, str], format: str | dict[str, str]}]',
                          description='The list of processing units. The filter is a dictionary with the fields as the '
                                      'key. The format can be either a string or a dict containing the format strings '
                                      'for each custom field. Please put the units with the most specific filters '
                                      'first, and leave the most generic last, to avoid short circuiting.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.units = [Unit(arg['filter'], arg['format']) for arg in args['units']]

    def process(self, data: NovelData) -> NovelData:
        for unit in self.units:
            if unit.filter(data):
                return unit.format(data)

        return data
