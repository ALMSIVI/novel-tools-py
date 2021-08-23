import csv
import os
from common import NovelData
from framework import Writer
from utils import purify_name


class CsvWriter(Writer):
    """
    Generates a volume/chapter list as a csv file.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled.
    """

    def __init__(self, args):
        """
        Arguments:

        - csv_filename (str, optional, default='list.csv'): Filename of the output csv file.
        - out_dir (str): The directory to write the csv file to.
        - additional_fields (list[str], optional): Specifies additional fields to be included to the csv file.
        """
        self.filename = os.path.join(args['out_dir'], purify_name(args.get('csv_filename', 'list.csv')))
        self.field_names = ['type', 'index', 'content', 'formatted'] + args.get('additional_fields', [])

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

        self.writer.writerow(data.to_dict())
