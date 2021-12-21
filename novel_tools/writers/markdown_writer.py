from novel_tools.common import Type, NovelData, FieldMetadata
from .__structure_writer__ import StructureWriter, Structure
from novel_tools.utils import purify_name


class MarkdownWriter(StructureWriter):
    """
    Writes the entire novel to a Markdown file.
    If a title field has been passed from a TitleTransformer and has the 'formatted' field filled, then the field will
    be prioritized.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return StructureWriter.required_fields() + [
            FieldMetadata('use_title', 'bool',
                          description='If set to True, will use the book title (if specified) as the Markdown '
                                      'filename.'),
            FieldMetadata('md_filename', 'str', default='text.md',
                          description='Filename of the output Markdown file, if `use_title` is False.'),
            FieldMetadata('levels', 'dict[str, int]', default={'book_title': 1, 'volume_title': 2, 'chapter_title': 3},
                          description='Specifies what level the header should be for each type.'),
            FieldMetadata('write_newline', 'bool', default=False,
                          description='If set to True, will insert a newline after a non-blank line. This will avoid '
                                      'contents on consecutive lines being treated as the same paragraph.'),
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        super().__init__(args)
        self.use_title = args['use_title']
        self.filename = args['md_filename']
        self.levels = {Type[key.upper()]: '#' * value + ' ' for key, value in args['levels'].items()}
        self.write_newline = args['write_newline']

    def write(self) -> None:
        self._cleanup()

        title = self.structure.title
        title_text = self._get_content(title) if title else ''
        filename = purify_name(self._get_filename(title) + '.md' if self.use_title else self.filename)
        with (self.out_dir / filename).open('wt') as f:
            if title:
                f.write(self.levels.get(Type.BOOK_TITLE, '') + title_text + '\n\n')

            # Write intro
            if len(self.structure.contents) > 0:
                f.write(self.structure.contents[0].content)
                f.write('\n\n')

            # Write volume
            if self.has_volumes:
                for i in range(len(self.structure.children)):
                    self.__write_volume(self.structure.children[i], f)
                    if i != len(self.structure.children) - 1:
                        f.write('\n\n')
            else:
                default_volume = Structure()
                default_volume.children = self.structure.children
                self.__write_volume(default_volume, f)

    def _join_content(self, contents: list[NovelData]) -> str:
        contents_str = []
        for content in contents:
            contents_str.append(content.content + '\n')
            if self.write_newline:
                contents_str.append('\n')

        return ''.join(contents_str).strip()

    def __write_volume(self, volume: Structure, f):
        if title := volume.title:
            f.write(self.levels.get(Type.VOLUME_TITLE, '') + self._get_content(title) + '\n\n')

        if len(volume.contents) > 0:
            f.write(volume.contents[0].content)
            f.write('\n\n')

        for i in range(len(volume.children)):
            chapter = volume.children[i]
            title = chapter.title
            f.write(self.levels.get(Type.CHAPTER_TITLE, '') + self._get_content(title) + '\n\n')
            f.write(chapter.contents[0].content)
            if i != len(volume.children) - 1:
                f.write('\n\n')