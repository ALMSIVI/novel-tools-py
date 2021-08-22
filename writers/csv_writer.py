import csv
import os
from common import NovelData, Type
from framework import Writer
from utils import purify_name


class CsvWriter(Writer):
    """
    Generates a volume/chapter list as a csv file.
    """

    def __init__(self, args):
        """
        Arguments:

        - csv_filename (str, optional, default='list.csv'): Filename of the output csv file.
        - out_dir (str): The directory to write the csv file to.
        - formats (dict[str, str]): Key is Type representations, and the value is the format string that can use any
          NovelData field.
        - correct (bool): If set to True, will write the original index and the corresponding formatted title to the
          csv.
        - debug (bool, optional, default=False): If set to True, will write the error message to the csv.
        - additional_fields (list[str], optional): Specifies additional fields to be included to the csv file.
        """
        self.filename = os.path.join(args['out_dir'], purify_name(args.get('csv_filename', 'list.csv')))

        self.formats = {Type[key.upper()]: value for key, value in args['formats'].items()}
        self.correct = args['correct']
        self.debug = args.get('debug', False)
        self.additional_fields = args.get('additional_fields', [])

        self.field_names = ['type', 'index', 'content', 'formatted']
        if self.correct:
            self.field_names += ['original_index', 'original_formatted']
        if self.debug:
            self.field_names += ['error']

        self.field_names += self.additional_fields
        self.file = None
        self.writer = None

    def cleanup(self):
        if self.file:
            self.file.close()

    def write(self, data: NovelData):
        if data.data_type not in self.formats:  # Normally, should only contain volume and chapter titles
            return

        if not self.file:
            self.file = open(self.filename, 'wt')
            self.writer = csv.DictWriter(self.file, fieldnames=self.field_names)
            self.writer.writeheader()

        csv_data = {
            'type': data.data_type,
            'index': data.index,
            'content': data.content,
            'formatted': data.format(self.formats[data.data_type])
        }

        if self.correct:
            original_index = data.get('original_index')
            csv_data['original_index'] = original_index
            csv_data['original_formatted'] = data.format(self.formats[data.data_type], index=original_index)
        if self.debug:
            csv_data['error'] = data.get('error', '')

        for field in self.additional_fields:
            csv_data[field] = data.get(field)

        self.writer.writerow(csv_data)
