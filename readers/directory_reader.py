import os
from typing import Iterator
from natsort import os_sorted
from common import NovelData, Type, ACC, FieldMetadata
from framework import Reader


class DirectoryReader(Reader, ACC):
    """
    Reads from a directory structure. This directory should be generated from FileWriter, as it will follow certain
    conventions, such as the first line of the chapter file being the title.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('in_dir', 'str',
                          description='The working directory.'),
            FieldMetadata('read_contents', 'bool',
                          description='If set to True, will open the files to read the contents.'),
            FieldMetadata('discard_chapters', 'bool',
                          description='If set to True, will start from chapter 1 again when entering a new volume.'),
            FieldMetadata('default_volume', 'str', default=None,
                          description='If the novel does not have volumes but all chapters are stored in a directory, '
                                      'then the variable would store the directory name.'),
            FieldMetadata('intro_filename', 'str', default='_intro.txt',
                          description='The filename of the book/volume introduction file(s).'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the chapter file(s).')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.in_dir = args['in_dir']
        self.read_contents = args['read_contents']
        self.discard_chapters = args['discard_chapters']
        self.default_volume = args['default_volume']
        self.encoding = args['encoding']
        self.intro_filename = args['intro_filename']

        # Create the list of volumes/directories to look for
        self.volumes = [dir_name for dir_name in os_sorted(os.listdir(self.in_dir)) if
                        os.path.isdir(os.path.join(self.in_dir, dir_name))]
        if self.default_volume in self.volumes:
            self.volumes = [self.default_volume]

    def read(self) -> Iterator[NovelData]:
        # Read intro file
        intro_filename = os.path.join(self.in_dir, self.intro_filename)
        if self.read_contents and os.path.isfile(intro_filename):
            with open(intro_filename, 'rt', encoding=self.encoding) as f:
                yield NovelData(f.read(), Type.BOOK_INTRO)

        volume_index = 0
        chapter_index = 0
        for volume in self.volumes:
            volume_index += 1
            if self.discard_chapters:
                chapter_index = 0

            if volume != self.default_volume:
                yield NovelData(volume, Type.VOLUME_TITLE, volume_index, source=volume)

            volume_path = os.path.join(self.in_dir, volume)
            chapters = [chapter for chapter in os_sorted(os.listdir(volume_path))
                        if os.path.isfile(os.path.join(volume_path, chapter))]
            # Read intro file
            if self.intro_filename in chapters:
                chapters.remove(self.intro_filename)
                if self.read_contents:
                    with open(os.path.join(volume_path, self.intro_filename), 'rt', encoding=self.encoding) as f:
                        yield NovelData(f.read(), Type.VOLUME_INTRO)

            for chapter in chapters:
                chapter_index += 1
                with open(os.path.join(volume_path, chapter), 'rt', encoding=self.encoding) as f:
                    yield NovelData(f.readline().strip(), Type.CHAPTER_TITLE, chapter_index, source=chapter)
                    if self.read_contents:
                        yield NovelData(f.read(), Type.CHAPTER_CONTENT)
