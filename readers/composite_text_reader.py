from typing import Optional
from framework import Reader
from common import NovelData, ACC, FieldMetadata
from .text_reader import TextReader
from .csv_reader import CsvReader
from .toc_reader import TocReader
from .metadata_json_reader import MetadataJsonReader


class CompositeTextReader(Reader, ACC):
    """
    Reads from a text file, but uses another reader (csv or toc) to provide the structure (volume/chapter titles).
    Additionally, could include a metadata reader for any additional information.
    Since the text file has a natural order, a TextReader will be used.
    - If csv is used, then it is preferred to contain either a "raw" column or a "line_num" column.
    - If toc is used, then it is preferred to contain line numbers.

    Notice that, unlike CompositeDirectoryReader, this reader will not not assign types other than titles. Consider
    pairing this with a TypeTransformer in order to get detailed types.

    Notice that some arguments from TextReader are not available:
    - verbose is not available; raw and line_num are needed to effectively matched against the structure data.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('in_dir', 'str', optional=True,
                          description='The directory to read the text file, structure file and metadata file (if it '
                                      'exists) from. Required if any of these filenames does not contain the path.'),
            FieldMetadata('structure', 'str', options=['csv', 'toc'],
                          description='Structure provider. Currently supported structures are \'csv\' and \'toc\'.'),
            FieldMetadata('metadata', 'str | bool', default=False,
                          description='If it is not specified or False, then no metadata will be read. If it is True, '
                                      'then the reader will use the default filename (specified in the reader). If it '
                                      'is a string, then the filename will be provided to the reader.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the chapter/structure/metadata files.'),
            # TextReader specific arguments
            FieldMetadata('text_filename', 'str', default='text.txt',
                          description='Filename of the text file.'),
            # CsvReader specific arguments
            FieldMetadata('csv_filename', 'str', default='list.csv', include_when=lambda a: a['structure'] == 'csv',
                          description='Filename of the csv list file. This file should be generated from `CsvWriter`, '
                                      'i.e., it must contain at least type, index and content.'),
            # TocReader specific arguments
            FieldMetadata('toc_filename', 'str', default='toc.txt', include_when=lambda a: a['structure'] == 'toc',
                          description='Filename of the toc file. This file should be generated from `TocWriter`.'),
            FieldMetadata('has_volume', 'bool', include_when=lambda a: a['structure'] == 'toc',
                          description='Specifies whether the toc contains volumes.'),
            FieldMetadata('discard_chapters', 'bool', include_when=lambda a: a['structure'] == 'toc',
                          description='If set to True, will start from chapter 1 again when entering a new volume.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        if args['structure'] == 'csv':
            self.structure = CsvReader(args)
        elif args['structure'] == 'toc':
            self.structure = TocReader(args)
        else:
            raise ValueError('structure should be either "csv" or "toc".')

        args['verbose'] = True  # Enforce verbose to get the line_num and raw
        self.reader = TextReader(args)
        self.curr_title = None

        if not args['metadata']:
            self.metadata = None
        else:
            if type(args['metadata']) is str:
                args['metadata_filename'] = args['metadata']
            self.metadata = MetadataJsonReader(args)

    def cleanup(self):
        self.reader.cleanup()
        self.structure.cleanup()

    def read(self) -> Optional[NovelData]:
        if self.metadata:
            metadata = self.metadata.read()
            self.metadata.cleanup()
            self.metadata = None
            return metadata

        if not self.curr_title:
            self.curr_title = self.structure.read()

        data = self.reader.read()
        # Title has been exhausted or eof reached, just return data
        if not data or not self.curr_title:
            return data

        # Compare line_num first, then raw/content. If there is a match, return curr_title.
        if self.curr_title.has('line_num') and self.curr_title.get('line_num') == data.get('line_num') or \
                self.curr_title.get('raw', self.curr_title.content) == data.get('raw', data.content):
            title = self.curr_title
            self.curr_title = None
            return title

        return data
