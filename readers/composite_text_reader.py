from typing import Optional
from framework import Reader
from common import NovelData
from .text_reader import TextReader
from .csv_reader import CsvReader
from .toc_reader import TocReader
from .metadata_json_reader import MetadataJsonReader


class CompositeTextReader(Reader):
    """
    Reads from a text file, but uses another reader (csv or toc) to provide the structure (volume/chapter titles).
    Additionally, could include a metadata reader for any additional information.
    Since the text file has a natural order, a TextReader will be used.
    If csv is used, then it is preferred to contain either a "raw" column or a "line_num" column, instead of "content".
    If toc is used, then it is preferred to contain line numbers.
    Notice that, unlike CompositeDirectoryReader, this reader will not not assign types other than titles. Consider
    pairing this with a TypeTransformer in order to get detailed types.
    """

    def __init__(self, args):
        """
        Arguments:

        - in_dir (str, optional): The directory to read the text file, structure file and metadata file (if it exists)
          from. Required if any of these filenames does not contain the path.
        - structure (str): Structure provider. Should be either csv or toc.
        - metadata (str | bool, optional): If it is not specified or False, then no metadata will be read. If it is
          True, then the reader will use the default filename (specified in the reader). If it is a string, then the
          filename will be provided to the reader.
        - encoding (str, optional, default='utf-8'): Encoding of the text/structure/metadata files.

        CsvReader specific arguments (if csv is used):

        - csv_filename (str, default='list.csv'): Filename of the csv list file. This file should be generated from
          CsvWriter, i.e., it must contain at least type, index and content.

        TocReader specific arguments (if toc is used):

        - toc_filename (str, optional, default='toc.txt'): Filename of the toc file. This file should be generated from
          TocWriter.
        - has_volume(bool): Specifies whether the toc contains volumes.
        - discard_chapters (bool): If set to True, will start from chapter 1 again when entering a new volume.

        TextReader specific arguments:
        - text_filename (str, optional, default='text.txt'): Filename of the text file.
        - verbose is not available; raw and line_num are needed to effectively matched against the structure data.
        """
        if args['structure'] == 'csv':
            self.structure = CsvReader(args)
        elif args['structure'] == 'toc':
            self.structure = TocReader(args)
        else:
            raise ValueError('structure should be either "csv" or "toc".')

        args['verbose'] = True  # Enforce verbose to get the line_num and raw
        self.reader = TextReader(args)
        self.curr_title = None

        if not args.get('metadata', False):
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
