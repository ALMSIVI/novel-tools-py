from abc import ABC
from pathlib import Path
from typing import Optional
from novel_tools.framework import Writer
from novel_tools.common import NovelData, Type, ACC, FieldMetadata


class Structure:
    """Recursive definition of a novel structure."""

    def __init__(self):
        self.title: Optional[NovelData] = None
        self.contents: list[NovelData] = []
        self.children: list[Structure] = []


class StructureWriter(Writer, ACC, ABC):
    """
    Abstract class that generates the novel hierarchy as it accepts the data. The `write()` method is left to child
    classes to implement.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('out_dir', 'Path',
                          description='The working directory.'),
            FieldMetadata('debug', 'bool', default=False,
                          description='If set to True, will print the error message to the terminal.'),
        ]

    def __init__(self, args):
        self.args = self.extract_fields(args)

        self.out_dir: Path = self.args['out_dir']
        self.debug = self.args['debug']

        self.structure = Structure()
        self.curr_volume = None
        self.curr_chapter = None
        self.has_volumes = False

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
