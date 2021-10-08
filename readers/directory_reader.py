import os
from typing import Iterator
from natsort import os_sorted
from common import NovelData, Type, ACC, FieldMetadata
from framework import Reader
from .text_reader import TextReader

supported_extensions = ['.txt', '.md']


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
                          description='Encoding of the chapter file(s).'),
            FieldMetadata('merge_newlines', 'bool', default=False,
                          description='If set to True, will merge two newline characters into one. Sometimes newline '
                                      'characters carry meanings, and we do not want decorative newlines to mix with '
                                      'those meaningful ones.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.in_dir = args['in_dir']
        self.read_contents = args['read_contents']
        self.discard_chapters = args['discard_chapters']
        self.default_volume = args['default_volume']
        self.encoding = args['encoding']
        self.intro_filename = args['intro_filename']
        self.merge_newlines = args['merge_newlines']

        # Create the list of volumes/directories to look for
        self.volumes = [dir_name for dir_name in os_sorted(os.listdir(self.in_dir)) if
                        os.path.isdir(os.path.join(self.in_dir, dir_name))]
        if self.default_volume in self.volumes:
            self.volumes = [self.default_volume]

    def read(self) -> Iterator[NovelData]:
        # Read intro file
        intro_filename = os.path.join(self.in_dir, self.intro_filename)
        if self.read_contents and os.path.isfile(intro_filename):
            text_reader = self.__get_text_reader(intro_filename)
            for data in text_reader.read():
                data.type = Type.BOOK_INTRO
                yield data

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
                        if os.path.isfile(os.path.join(volume_path, chapter))
                        and os.path.splitext(chapter)[1] in supported_extensions]
            # Read intro file
            if self.intro_filename in chapters:
                chapters.remove(self.intro_filename)
                if self.read_contents:
                    text_reader = self.__get_text_reader(os.path.join(volume_path, self.intro_filename))
                    for data in text_reader.read():
                        data.type = Type.VOLUME_INTRO
                        yield data

            for chapter in chapters:
                chapter_index += 1
                text_reader = self.__get_text_reader(os.path.join(volume_path, chapter))
                read = text_reader.read()
                data = next(read)  # Title
                data.type = Type.CHAPTER_TITLE
                data.index = chapter_index
                yield data
                if self.read_contents:
                    for data in read:
                        data.type = Type.CHAPTER_CONTENT
                        yield data

    def __get_text_reader(self, filename: str) -> TextReader:
        return TextReader({
            'text_filename': filename,
            'in_dir': self.in_dir,
            'encoding': self.encoding,
            'verbose': True,
            'merge_newlines': self.merge_newlines
        })
