from pathlib import Path
from typing import Iterator
from natsort import os_sorted
from novel_tools.common import NovelData, Type, ACC, FieldMetadata
from novel_tools.framework import Reader
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
            FieldMetadata('in_dir', 'Path',
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
        self.in_dir: Path = args['in_dir']
        self.read_contents = args['read_contents']
        self.discard_chapters = args['discard_chapters']
        self.default_volume = self.in_dir / args['default_volume'] if args['default_volume'] else None
        self.encoding = args['encoding']
        self.intro_filename = args['intro_filename']
        self.merge_newlines = args['merge_newlines']

        # Create the list of volumes/directories to look for
        self.volumes: list[Path] = [dir_path for dir_path in os_sorted(self.in_dir.iterdir()) if dir_path.is_dir()]
        if self.default_volume in self.volumes:
            self.volumes = [self.default_volume]

    def read(self) -> Iterator[NovelData]:
        # Read intro file
        intro_path = self.in_dir / self.intro_filename
        if self.read_contents and intro_path.is_file():
            text_reader = self.__get_text_reader(intro_path)
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
                yield NovelData(volume.stem, Type.VOLUME_TITLE, volume_index, source=volume)

            chapters = [chapter for chapter in os_sorted(volume.iterdir()) if chapter.is_file()
                        and chapter.suffix in supported_extensions]
            # Read intro file
            intro_path = Path(volume, self.intro_filename)
            if intro_path in chapters:
                chapters.remove(intro_path)
                if self.read_contents:
                    text_reader = self.__get_text_reader(intro_path)
                    for data in text_reader.read():
                        data.type = Type.VOLUME_INTRO
                        yield data

            for chapter in chapters:
                chapter_index += 1
                text_reader = self.__get_text_reader(chapter)
                read = text_reader.read()
                data = next(read)  # Title
                data.type = Type.CHAPTER_TITLE
                data.index = chapter_index
                yield data
                if self.read_contents:
                    for data in read:
                        data.type = Type.CHAPTER_CONTENT
                        yield data

    def __get_text_reader(self, filename: Path) -> TextReader:
        return TextReader({
            'text_filename': filename,
            'in_dir': self.in_dir,
            'encoding': self.encoding,
            'verbose': True,
            'merge_newlines': self.merge_newlines
        })
