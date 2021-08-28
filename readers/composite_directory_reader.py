import os
from typing import Optional
from framework import Reader
from common import NovelData, Type, ACC, FieldMetadata
from .csv_reader import CsvReader
from .toc_reader import TocReader
from .metadata_json_reader import MetadataJsonReader


class CompositeDirectoryReader(Reader, ACC):
    """
    Reads from a directory, but uses another reader (csv or toc) to provide the structure (volume/chapter titles).
    Additionally, could include a metadata reader for any additional information.
    Since the directory doesn't have an explicit structure, the DirectoryReader needs to read everything first before it
    can be matched against the structure. This might result in an extended initialization time.
    - If csv is used, then it is preferred contain a "raw" column, instead "content".
    - If toc is used, then the titles MUST match the directory/file names.

    Notice that some arguments from DirectoryReader are not available:
    - discard_chapters is not available; this will be automatically inferred from the structure provider.
    - read_contents is not available; please use the structure reader directly if you don't want the contents.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('in_dir', 'str',
                          description='The working directory. Should also include the structure file and the metadata '
                                      'file, if specified.'),
            FieldMetadata('structure', 'str', options=['csv', 'toc'],
                          description='Structure provider. Currently supported structures are \'csv\' and \'toc\'.'),
            FieldMetadata('metadata', 'str | bool', default=False,
                          description='If it is not specified or False, then no metadata will be read. If it is True, '
                                      'then the reader will use the default filename (specified in the reader). If it '
                                      'is a string, then the filename will be provided to the reader.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the chapter/structure/metadata files.'),
            # DirectoryReader specific arguments
            FieldMetadata('intro_filename', 'str', default='_intro.txt',
                          description='The filename of the book/volume introduction file(s).'),
            FieldMetadata('default_volume', 'str', default=None,
                          description='If the novel does not have volumes but all chapters are stored in a directory, '
                                      'then the variable would store the directory name.'),
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

        # Initialization of a directory reader
        self.in_dir = args['in_dir']
        self.encoding = args['encoding']
        self.intro_filename = args['intro_filename']

        self.read_intro = os.path.isfile(os.path.join(self.in_dir, self.intro_filename))
        self.chapters = []
        self.curr_volume = args['default_volume']
        self.file = None
        self.curr_type = Type.UNRECOGNIZED

        if not args['metadata']:
            self.metadata = None
        else:
            if type(args['metadata']) is str:
                args['metadata_filename'] = args['metadata']
            self.metadata = MetadataJsonReader(args)

    def cleanup(self):
        if self.file and not self.file.closed:
            self.file.close()
        self.structure.cleanup()

    def read(self) -> Optional[NovelData]:
        if self.metadata:
            metadata = self.metadata.read()
            self.metadata.cleanup()
            self.metadata = None
            return metadata

        # Then read the intro
        if self.read_intro:
            self.read_intro = False
            with open(os.path.join(self.in_dir, self.intro_filename), 'rt', encoding=self.encoding) as f:
                return NovelData(f.read(), Type.BOOK_INTRO)

        # Read chapter contents
        if self.file:
            contents = self.file.read()
            self.file.close()
            self.file = None
            return NovelData(contents, self.curr_type)

        # Get the next piece from the structure
        data = self.structure.read()
        if data is None:
            return None

        title = data.get('raw', data.content)
        if data.type == Type.VOLUME_TITLE:
            self.curr_volume = title
            volume_dir = os.path.join(self.in_dir, self.curr_volume)
            self.chapters = [filename for filename in os.listdir(volume_dir) if
                             os.path.isfile(os.path.join(volume_dir, filename))]

            # Check if there are any volume intro files
            if self.intro_filename in self.chapters:
                self.file = open(os.path.join(volume_dir, self.intro_filename), 'rt', encoding=self.encoding)
                self.curr_type = Type.VOLUME_INTRO
        elif data.type == Type.CHAPTER_TITLE:
            # Assume that title may not include extension
            filename = [name for name in self.chapters if name.startswith(title)][0]
            self.file = open(os.path.join(self.in_dir, self.curr_volume, filename), 'rt',
                             encoding=self.encoding)
            self.file.readline()  # Skip title
            self.curr_type = Type.CHAPTER_CONTENT

        return data
