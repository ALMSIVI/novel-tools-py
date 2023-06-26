from pydantic import BaseModel, Field
from pathlib import Path
import csv
from novel_tools.common import NovelData
from novel_tools.framework import Writer
from novel_tools.utils import purify_name


class Options(BaseModel):
    csv_filename: str = Field(default='list.csv', description='Filename of the output csv file.')
    out_dir: Path = Field(description='The directory to write the csv file to.')
    additional_fields: list[str] = Field(default=[],
                                         description='Specifies additional fields to be included to the csv file.')


class CsvWriter(Writer):
    """
    Generates a volume/chapter list as a csv file.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled.
    """

    def __init__(self, args):
        options = Options(**args)
        self.csv_path = options.out_dir / purify_name(options.csv_filename)
        self.field_names = ['type', 'index', 'content', 'formatted'] + options.additional_fields

        self.list = []

    def accept(self, data: NovelData) -> None:
        if not data.has('formatted'):  # Normally, only titles should contain this field
            return

        self.list.append(data)

    def write(self) -> None:
        with self.csv_path.open('wt', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.field_names)
            writer.writeheader()
            for data in self.list:
                writer.writerow(data.flat_dict(self.field_names))
