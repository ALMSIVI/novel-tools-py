import os
from typing import Optional
from framework import Reader
from common import NovelData, Type
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
        - structure (string): Structure provider. Should be either csv or toc.
        - structure_filename (optional, string): Filename of the structure file that is needed for the provider. If not
          specified, will use the respective reader's default filename (specified in the reader).
        - metadata (optional, string | bool): If it is False, then no metadata will be read. If it is True, then the
          reader will use the default filename (specified in the reader). If it is a string, then the filename will be
          provided to the reader.
        The rest of the arguments are from TextReader:
        - encoding (optional, str): The encoding of the file. Default is utf-8.
        - types (optional, dict[str, str]): Correspondence between csv types and novel types. Required if the structure
          is csv.
        """
        reader_args = {'in_dir': args['in_dir']}  # This will be provided by the program, not the config

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
        elif type(args['metadata']) is str:
            reader_args['metadata_filename'] = args['metadata']
            self.metadata = MetadataJsonReader(reader_args)
        else:
            self.metadata = MetadataJsonReader({})

        args['verbose'] = True  # Enforce verbose to get the line_num and raw
        self.reader = TextReader(args)

        self.curr_title = None

        # If there is no metadata, use the filename as title
        path, extension = os.path.splitext(args['filename'])
        self.title = path.split('/')[-1]

        self.title_read = False

    def cleanup(self):
        self.reader.cleanup()
        self.structure.cleanup()
        if self.metadata:
            self.metadata.cleanup()

    def read(self) -> Optional[NovelData]:
        # The first data must be BOOK_TITLE
        if not self.title_read:
            self.title_read = True
            if self.metadata:
                return self.metadata.read()
            return NovelData(self.title, Type.BOOK_TITLE)

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
