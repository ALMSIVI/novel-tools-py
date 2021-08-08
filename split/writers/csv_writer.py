import csv, os
from framework import Writer
from common import NovelData, Type

class CsvWriter(Writer):
    '''
    Generates a volume/chapter list as a csv file, without splitting the chapters into their respective text files.
    '''
    def __init__(self, args):
        '''
        Arguments:
        - formats (dict[str, dict[str, str]]): Key is Type representations, and the value consists of two fields:
            - column: Name of the type that will appear on the csv column.
            - format: Format string that contains {index} and {title} to be formatted.
        - correct (bool): If set to True, will write the original index and the corresponding formatted title to the csv.
        - debug (bool): If set to True, will write the error message to the csv.
        - verbose (optional, bool): If set to True, will write the line number and raw content to the csv. Default is False.
        '''
        out_dir = args.get('out_dir', args['in_dir']) # Both will be supplied by the program, not the config
        self.filename = os.path.join(out_dir, 'list.csv')

        self.formats = {Type[key.upper()]: value for key, value in args['formats'].items()}
        self.correct = args['correct']
        self.debug = args['debug']
        self.verbose = args.get('verbose', False)

        self.field_names = ['type', 'index', 'title', 'formatted']
        if self.correct:
            self.field_names += ['o_index', 'o_formatted']
        if self.debug:
            self.field_names += ['error']
        if self.verbose:
            self.field_names += ['line_num', 'raw']
    
    
    def before(self):
        self.file = open(self.filename, 'wt')
        self.writer = csv.DictWriter(self.file, fieldnames=self.field_names)
        self.writer.writeheader()

    def after(self):
        self.file.close() 
    
    def write(self, data: NovelData):
        if data.type not in self.formats: # Normally, should only contain volume and chapter titles
            return

        csv_data = {
            'type': self.formats[data.type]['column'],
            'index': data.index,
            'title': data.content,
            'formatted': self.formats[data.type]['format'].format(index=data.index, title=data.content)
        }
        if self.correct:
            o_index = data.get('original_index')
            csv_data |= {
                'o_index': o_index,
                'o_formatted': self.formats[data.type]['format'].format(index=o_index, title=data.content)
            }
        if self.debug:
            csv_data |= {
                'error': data.error
            }
        if self.verbose:
            csv_data |= {
                'line_num': data.get('line_num'),
                'raw': data.get('raw')
            }
        
        self.writer.writerow(csv_data)