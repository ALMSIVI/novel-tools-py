import csv
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Iterator
from novel_tools.framework import NovelData, Type, Reader


class Options(BaseModel):
    csv_filename: str = Field(default='list.csv',
                              description='Filename of the csv list file. This file should be generated from '
                                          '`CsvWriter`, i.e., it must contain at least type, index and content.')

    in_dir: Path | None = Field(description='The directory to read the csv file from. Required if the filename does not'
                                            ' contain the path.')
    encoding: str = Field(default='utf-8', description='Encoding of the csv file.')
    types: dict[str, str] = Field(default={'line_num': 'int', 'source': 'Path'},
                                  description='Type of each additional field to be fetched. Currently, int, bool and '
                                              'Path are supported.')
    join_dir: list[str] = Field(default=['source'],
                                description='If the data corresponding to the given field names is type Path, it will '
                                            'be treated as a relative path and will be joined by `in_dir`.')


class CsvReader(Reader):
    """
    Recovers the novel structure from the csv list. The csv is required to contain a "content" column, but it does not
    have to contain the other fields from a NovelData.
    """

    def __init__(self, args):
        options = Options(**args)
        self.in_dir = options.in_dir
        csv_file = Path(options.csv_filename)
        csv_file = csv_file if csv_file.is_file() else Path(self.in_dir, csv_file)
        with csv_file.open('rt', encoding=options.encoding) as f:
            self.list = []
            reader = csv.DictReader(f)
            for row in reader:
                self.list.append(row)

        if 'content' not in self.list[0]:
            raise ValueError('csv does not contain valid columns.')

        self.types = options.types
        self.join_dir = options.join_dir

    def read(self) -> Iterator[NovelData]:
        for i in range(len(self.list)):
            data: dict = self.list[i]
            content = data.pop('content')
            data_type = Type[data.pop('type', 'unrecognized').upper()]
            index = data.pop('index', None)
            if index is not None:
                index = int(index)

            for name, field_type in self.types.items():
                if name not in data:
                    continue

                try:
                    if field_type == 'int':
                        data[name] = int(data[name])
                    if field_type == 'bool':
                        data[name] = bool(data[name])
                    if field_type == 'Path':
                        data[name] = Path(data[name])
                except ValueError:
                    data[name] = None

            for name in self.join_dir:
                if isinstance(data.get(name, None), Path):
                    data[name] = self.in_dir / data[name]

            yield NovelData(content, data_type, index, **data)
