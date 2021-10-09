import csv
from common import NovelData, ACC, FieldMetadata
from framework import Writer
from utils import purify_name


class CsvWriter(Writer, ACC):
    """
    Generates a volume/chapter list as a csv file.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('csv_filename', 'str', default='list.csv',
                          description='Filename of the output csv file.'),
            FieldMetadata('out_dir', 'Path',
                          description='The directory to write the csv file to.'),
            FieldMetadata('additional_fields', 'list[str]', default=[],
                          description='Specifies additional fields to be included to the csv file.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.csv_path = args['out_dir'] / purify_name(args['csv_filename'])
        self.field_names = ['type', 'index', 'content', 'formatted'] + args['additional_fields']

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
