import csv
import os

from common import NovelData, Type
from framework import Writer


class CsvWriter(Writer):
    """
    Generates a volume/chapter list as a csv file, without splitting the chapters into their respective text files.
    """

    def __init__(self, args):
        """
        Arguments:

        - csv_filename (str, optional, default='list.csv'): Filename of the output csv file.
        - out_dir (str): The directory to write the csv file to.
        - formats (dict[str, dict[str, str]]): Key is Type representations, and the value consists of two fields:
            - column: Name of the type that will appear on the csv column.
            - format: Format string that can use any NovelData field.
        - correct (bool): If set to True, will write the original index and the corresponding formatted title to the
          csv.
        - debug (bool): If set to True, will write the error message to the csv.
        - additional_fields (list[str], optional): Specifies additional fields to be included to the csv file.
        """
        self.filename = os.path.join(args['out_dir'], args.get('csv_filename', 'list.csv'))

        self.formats = {Type[key.upper()]: value for key, value in args['formats'].items()}
        self.correct = args['correct']
        self.debug = args['debug']
        self.additional_fields = args.get('additional_fields', [])

        self.field_names = ['type', 'index', 'content', 'formatted']
        if self.correct:
            self.field_names += ['o_index', 'o_formatted']
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
            'type': self.formats[data.data_type]['column'],
            'index': data.index,
            'content': data.content,
            'formatted': data.format(self.formats[data.data_type]['format'])
        }

        if self.correct:
            o_index = data.get('original_index')
            csv_data['o_index'] = o_index
            csv_data['o_formatted'] = data.format(self.formats[data.data_type]['format'], index=o_index)
        if self.debug:
            csv_data['error'] = data.get('error', '')

        for field in self.additional_fields:
            csv_data[field] = data.get(field)

        self.writer.writerow(csv_data)
