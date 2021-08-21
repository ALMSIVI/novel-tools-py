from typing import Optional
from framework import Reader
from common import NovelData
from .text_reader import TextReader
from .csv_reader import CsvReader
from .toc_reader import TocReader
from .metadata_json_reader import MetadataJsonReader


class CompositeTextReader(Reader):
    """
    Reads from a text file, but uses another reader (csv or toc) to provide the structure.
    Additionally, could include a metadata reader for any additional information.
    Since the text file has a natural order, a TextReader is used.
    """

    def __init__(self, args):
        """
        Arguments:

        - in_dir (str, optional): The directory to read the text file, structure file and metadata file (if it exists)
          from. Required if any of these filenames does not contain the path.
        - text_filename (str, optional, default='text.txt'): Filename of the text file.
        - structure (str): Structure provider. Should be either csv or toc.
        - structure_filename (str, optional): Filename of the structure file that is needed for the provider. If not
          specified, will use the respective reader's default filename (specified in the reader).
        - metadata (str | bool, optional): If it is False, then no metadata will be read. If it is True, then the
          reader will use the default filename (specified in the reader). If it is a string, then the filename will be
          provided to the reader.

        The rest of the arguments are from TextReader:

        - encoding (str, optional, default='utf-8'): The encoding of the file.
        - types (dict[str, str], optional): Correspondence between csv types and novel types. Required if the structure
          is csv.
        """
        reader_args = {'in_dir': args['in_dir']} if 'in_dir' in args else {}

        if args['structure'] == 'csv':
            if 'structure_filename' in args:
                reader_args['csv_filename'] = args['structure_filename']
                reader_args['types'] = args['types']
            self.structure = CsvReader(reader_args)
        elif args['structure'] == 'toc':
            if 'structure_filename' in args:
                reader_args['toc_filename'] = args['structure_filename']
            self.structure = TocReader(reader_args)
        else:
            raise ValueError('structure should be either "csv" or "toc".')

        if not args.get('metadata', False):
            self.metadata = None
        else:
            if type(args['metadata']) is str:
                reader_args['metadata_filename'] = args['metadata_filename']
            metadata_reader = MetadataJsonReader(reader_args)
            self.metadata = metadata_reader.read()
            metadata_reader.cleanup()

        args['verbose'] = True  # Enforce verbose to get the line_num and raw
        self.reader = TextReader(args)

        self.curr_title = None

    def cleanup(self):
        self.reader.cleanup()
        self.structure.cleanup()

    def read(self) -> Optional[NovelData]:
        if self.metadata:
            metadata = self.metadata
            self.metadata = None
            return metadata

        if not self.curr_title:
            self.curr_title = self.structure.read()

        data = self.reader.read()
        # Title has been exhausted or eof reached, just return data
        if not data or not self.curr_title:
            return data

        # Compare raw first (if it exists), then line_num. If there is a match, return curr_title.
        if self.curr_title.has('raw') and data.get('raw') == self.curr_title.get('raw') or self.curr_title.get(
                'line_num') == data.get('line_num'):
            return self.curr_title

        return data
