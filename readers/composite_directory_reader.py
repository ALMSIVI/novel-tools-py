import os
from typing import Optional
from framework import Reader
from common import NovelData, Type
from .csv_reader import CsvReader
from .toc_reader import TocReader
from .metadata_json_reader import MetadataJsonReader


class CompositeDirectoryReader(Reader):
    """
    Reads from a directory, but uses another reader (csv or toc) to provide the structure.
    Additionally, could include a metadata reader for any additional information.
    Since the directory doesn't have an explicit structure, DirectoryReader cannot be used.
    If csv is used, then there MUST be a "raw" column, which will be matched against the directory/file names.
    If toc is used, then the titles MUST match the directory/file names.
    """

    def __init__(self, args):
        """
        Arguments:

        - in_dir (str): The working directory. Should also include the structure file and the metadata file, if
          specified.
        - structure (string): Structure provider. Should be either csv or toc.
        - structure_filename (string, optional): Filename of the structure file that is needed for the provider. If not
          specified, will use the respective reader's default filename (specified in the reader).
        - metadata (string | bool, optional): If it is False, then no metadata will be read. If it is True, then the
          reader will use the default filename (specified in the reader). If it is a string, then the filename will be
          provided to the reader.

        The rest of the arguments are from TextReader:

        - default_volume (str, optional): If the novel doesn't have volumes but all chapters are stored in a directory,
          then the variable would store the directory name.
        - intro_filename (str, optional, default='_intro.txt'): The name if the book/volume introduction file.
        """
        reader_args = {'in_dir': args['in_dir']}

        if args['structure'] == 'csv':
            if 'structure_filename' in args:
                reader_args['csv_filename'] = args['structure_filename']
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

        self.in_dir = args['in_dir']
        self.curr_volume = args.get('default_volume', '')
        self.intro_filename = args.get('intro_filename', '_intro.txt')
        self.read_intro = os.path.exists(os.path.join(self.in_dir, self.intro_filename))

        self.chapter_file = None
        self.curr_title = None
        self.curr_type = Type.UNRECOGNIZED

    def cleanup(self):
        if self.chapter_file and not self.chapter_file.closed:
            self.chapter_file.close()
        self.structure.cleanup()

    def read(self) -> Optional[NovelData]:
        if self.metadata:
            metadata = self.metadata
            self.metadata = None
            return metadata

        # Then read the intro
        if self.read_intro:
            self.read_intro = False
            with open(os.path.join(self.in_dir, self.intro_filename), 'rt') as f:
                return NovelData(f.read(), Type.BOOK_INTRO)

        # Read chapter contents
        if self.chapter_file:
            contents = self.chapter_file.read()
            self.chapter_file.close()
            self.chapter_file = None
            return NovelData(contents, self.curr_type)

        if not self.curr_title:
            self.curr_title = self.structure.read()
            if not self.curr_title:
                return None

        content = self.curr_title.get('raw', self.curr_title.content)
        if self.curr_title.data_type == Type.VOLUME_TITLE:
            self.curr_volume = content
            # Look for volume intro
            if self.intro_filename in os.listdir(os.path.join(self.in_dir, self.curr_volume)):
                self.chapter_file = open(os.path.join(self.in_dir, self.curr_volume, self.intro_filename), 'rt')
                self.curr_type = Type.VOLUME_INTRO
        elif self.curr_title.data_type == Type.CHAPTER_TITLE:
            self.chapter_file = open(os.path.join(self.in_dir, self.curr_volume, content), 'rt')
            self.curr_type = Type.CHAPTER_CONTENT

        return self.curr_title
