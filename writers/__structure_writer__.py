from abc import ABC
from typing import Optional
from framework import Writer
from common import NovelData, Type, ACC, FieldMetadata


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
            FieldMetadata('out_dir', 'str',
                          description='The working directory.'),
            FieldMetadata('debug', 'bool', default=False,
                          description='If set to True, will print the error message to the terminal.'),
            FieldMetadata('write_newline', 'bool', default=False,
                          description='If set to True, will insert a newline after a non-blank line. This will avoid '
                                      'contents on consecutive lines being treated as the same paragraph.'),
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.out_dir = args['out_dir']
        self.debug = args['debug']
        self.write_newline = args['write_newline']

        self.structure = Structure()
        self.curr_volume = None
        self.curr_chapter = None
        self.has_volumes = False

    def accept(self, data: NovelData) -> None:
        if self.debug and data.get('error', '') != '':
            print(data.get('error'))

        if data.type == Type.BOOK_TITLE:
            self.structure.title = data
        elif data.type == Type.BOOK_INTRO:
            self.structure.contents.append(data)
        elif data.type == Type.VOLUME_TITLE:
            self.has_volumes = True
            self.curr_volume = Structure()
            self.curr_volume.title = data
            self.structure.children.append(self.curr_volume)
        elif data.type == Type.VOLUME_INTRO:
            self.curr_volume.contents.append(data)
        elif data.type == Type.CHAPTER_TITLE:
            self.curr_chapter = Structure()
            self.curr_chapter.title = data
            if self.has_volumes:
                self.curr_volume.children.append(self.curr_chapter)
            else:
                self.structure.children.append(self.curr_chapter)
        elif data.type == Type.CHAPTER_CONTENT:
            self.curr_chapter.contents.append(data)
        else:
            print(f'Unrecognized data type: {data.type}')

    def __join_content(self, contents: list[NovelData]) -> str:
        contents_str = []
        for content in contents:
            contents_str.append(content.content + '\n')
            if self.write_newline:
                contents_str.append('\n')

        return ''.join(contents_str).strip()

    def _cleanup(self):
        intro = self.__join_content(self.structure.contents)
        self.structure.contents = [] if intro == '' else [NovelData(intro, Type.BOOK_INTRO)]

        if self.has_volumes:
            for volume in self.structure.children:
                intro = self.__join_content(volume.contents)
                volume.contents = [] if intro == '' else [NovelData(intro, Type.VOLUME_INTRO)]

                for chapter in volume.children:
                    content = self.__join_content(chapter.contents)
                    chapter.contents = [NovelData(content, Type.CHAPTER_CONTENT)]
        else:
            for chapter in self.structure.children:
                content = self.__join_content(chapter.contents)
                chapter.contents = [NovelData(content, Type.CHAPTER_CONTENT)]

    @staticmethod
    def _get_content(data: NovelData):
        return data.get('formatted', data.content)

    @classmethod
    def _get_filename(cls, data: NovelData):
        return data.get('filename', cls._get_content(data))
