from pydantic import BaseModel, DirectoryPath, Field
from abc import ABC
from pathlib import Path
from novel_tools.framework import NovelData, Type, Writer


class Structure:
    """Recursive definition of a novel structure."""

    def __init__(self):
        self.title: NovelData | None = None
        self.contents: list[NovelData] = []
        self.children: list[Structure] = []


class BaseOptions(BaseModel):
    out_dir: DirectoryPath = Field(description='The working directory.')
    debug: bool = Field(default=False, description='If set to True, will print the error message to the terminal.')


class StructureWriter(Writer, ABC):
    """
    Abstract class that generates the novel hierarchy as it accepts the data. The `write()` method is left to child
    classes to implement.
    """
    out_dir: Path
    debug: bool
    structure: Structure
    curr_volume: Structure = None
    curr_chapter: Structure = None
    has_volumes: bool = False

    def init_fields(self, options: BaseOptions):
        self.structure = Structure()
        self.out_dir = options.out_dir
        self.debug = options.debug

    def accept(self, data: NovelData) -> None:
        if self.debug and data.get('error', '') != '':
            print(data.get('error'))

        match data.type:
            case Type.BOOK_TITLE:
                self.structure.title = data
            case Type.BOOK_INTRO:
                self.structure.contents.append(data)
            case Type.VOLUME_TITLE:
                self.has_volumes = True
                self.curr_volume = Structure()
                self.curr_volume.title = data
                self.structure.children.append(self.curr_volume)
            case Type.VOLUME_INTRO:
                self.curr_volume.contents.append(data)
            case Type.CHAPTER_TITLE:
                self.curr_chapter = Structure()
                self.curr_chapter.title = data
                if self.has_volumes:
                    self.curr_volume.children.append(self.curr_chapter)
                else:
                    self.structure.children.append(self.curr_chapter)
            case Type.CHAPTER_CONTENT:
                self.curr_chapter.contents.append(data)
            case _:
                print(f'Unrecognized data type: {data.type}')

    def _join_content(self, contents: list[NovelData]) -> str:
        contents_str = []
        for content in contents:
            contents_str.append(content.content + '\n')

        return ''.join(contents_str).strip()

    def _cleanup(self):
        intro = self._join_content(self.structure.contents)
        self.structure.contents = [] if intro == '' else [NovelData(intro, Type.BOOK_INTRO)]

        if self.has_volumes:
            for volume in self.structure.children:
                intro = self._join_content(volume.contents)
                volume.contents = [] if intro == '' else [NovelData(intro, Type.VOLUME_INTRO)]

                for chapter in volume.children:
                    content = self._join_content(chapter.contents)
                    chapter.contents = [NovelData(content, Type.CHAPTER_CONTENT)]
        else:
            for chapter in self.structure.children:
                content = self._join_content(chapter.contents)
                chapter.contents = [NovelData(content, Type.CHAPTER_CONTENT)]

    @staticmethod
    def _get_content(data: NovelData):
        return data.get('formatted', data.content)

    @classmethod
    def _get_filename(cls, data: NovelData):
        return data.get('filename', cls._get_content(data))
