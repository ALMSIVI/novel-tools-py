from abc import ABC
from framework import Writer
from common import NovelData, Type, ACC, FieldMetadata
from utils import purify_name


class Structure:
    """Recursive definition of a novel structure."""

    def __init__(self):
        self.title: str = ''
        self.filename: str = ''
        self.contents: list[str] = []
        self.children: list[Structure] = []


def join_content(contents: list[str]) -> str:
    return ''.join(contents).strip()


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
        if data.has('error'):
            print(data.get('error'))

        if data.type == Type.BOOK_TITLE:
            self.structure.title = data.get('formatted', data.content)
            self.structure.filename = data.get('filename', data.get('formatted', data.content))
        elif data.type == Type.BOOK_INTRO:
            self.append_content(self.structure.contents, data.content)
        elif data.type == Type.VOLUME_TITLE:
            self.has_volumes = True
            self.curr_volume = Structure()
            self.curr_volume.title = data.get('formatted', data.content)
            self.curr_volume.filename = purify_name(data.get('filename', data.get('formatted', data.content)))
            self.structure.children.append(self.curr_volume)
        elif data.type == Type.VOLUME_INTRO:
            self.append_content(self.curr_volume.contents, data.content)
        elif data.type == Type.CHAPTER_TITLE:
            self.curr_chapter = Structure()
            self.curr_chapter.title = data.get('formatted', data.content)
            self.curr_chapter.filename = purify_name(data.get('filename', data.get('formatted', data.content)))
            if self.has_volumes:
                self.curr_volume.children.append(self.curr_chapter)
            else:
                self.structure.children.append(self.curr_chapter)
        elif data.type == Type.CHAPTER_CONTENT:
            self.append_content(self.curr_chapter.contents, data.content)
        else:
            print(f'Unrecognized data type: {data.type}')

    def append_content(self, contents: list[str], content: str):
        contents.append(content + '\n')
        if content != '' and self.write_newline:
            contents.append('\n')

    def cleanup(self):
        intro = join_content(self.structure.contents)
        self.structure.contents = [] if intro == '' else [intro]

        if self.has_volumes:
            for volume in self.structure.children:
                intro = join_content(volume.contents)
                volume.contents = [] if intro == '' else [intro]

                for chapter in volume.children:
                    content = join_content(chapter.contents)
                    chapter.contents = [content]
        else:
            for chapter in self.structure.children:
                content = join_content(chapter.contents)
                chapter.contents = [content]
