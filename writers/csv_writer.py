import csv
import os
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
            FieldMetadata('out_dir', 'str',
                          description='The directory to write the csv file to.'),
            FieldMetadata('additional_fields', 'list[str]', default=[],
                          description='Specifies additional fields to be included to the csv file.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.filename = os.path.join(args['out_dir'], purify_name(args['csv_filename']))
        self.field_names = ['type', 'index', 'content', 'formatted'] + args['additional_fields']

        self.file = None
        self.writer = None

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if not data.has('formatted'):  # Normally, should only contain volume and chapter titles
            return

        if not self.file:
            self.file = open(self.filename, 'wt')
            self.writer = csv.DictWriter(self.file, fieldnames=self.field_names)
            self.writer.writeheader()

        self.writer.writerow(data.to_dict(self.field_names))
