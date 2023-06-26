from pydantic import BaseModel, Field
from pathlib import Path
from typing import Iterator
from natsort import os_sorted
from novel_tools.framework import NovelData, Type, Reader
from .text_reader import TextReader

supported_extensions = ['.txt', '.md']


class Options(BaseModel):
    in_dir: Path = Field(description='The working directory.')
    read_contents: bool = Field(description='If set to True, will open the files to read the contents.')
    discard_chapters: bool = Field(description='If set to True, will start from chapter 1 again when entering a new '
                                               'volume.')
    default_volume: str | None = Field(description='If the novel does not have volumes but all chapters are stored in a'
                                                   ' directory, then the variable would store the directory name.')
    intro_filename: str = Field(default='_intro.txt',
                                description='The filename of the book/volume introduction file(s).')
    encoding: str = Field(default='utf-8', description='Encoding of the chapter file(s).')
    merge_newlines: bool = Field(default=False,
                                 description='If set to True, will merge two newline characters into one. Sometimes '
                                             'newline characters carry meanings, and we do not want decorative '
                                             'newlines to mix with those meaningful ones.')


class DirectoryReader(Reader):
    """
    Reads from a directory structure. This directory should be generated from FileWriter, as it will follow certain
    conventions, such as the first line of the chapter file being the title.
    """

    def __init__(self, args):
        options = Options(**args)
        self.in_dir = options.in_dir
        self.read_contents = options.read_contents
        self.discard_chapters = options.discard_chapters
        self.default_volume = self.in_dir / options.default_volume if options.default_volume else None
        self.encoding = options.encoding
        self.intro_filename = options.intro_filename
        self.merge_newlines = options.merge_newlines

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

            chapter: Path  # natsort can accept a range of types, so we need to make type checker happy
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
            'text_filename': str(filename),
            'in_dir': self.in_dir,
            'encoding': self.encoding,
            'verbose': True,
            'merge_newlines': self.merge_newlines
        })
