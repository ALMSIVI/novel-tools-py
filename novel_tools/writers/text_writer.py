from novel_tools.common import FieldMetadata
from .__structure_writer__ import StructureWriter, Structure
from novel_tools.utils import purify_name


class TextWriter(StructureWriter):
    """
    Writes the entire novel to a text file.
    If a title field has been passed from a TitleTransformer and has the 'formatted' field filled, then the field will
    be prioritized.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return StructureWriter.required_fields() + [
            FieldMetadata('use_title', 'bool',
                          description='If set to True, will use the book title (if specified) as the text filename.'),
            FieldMetadata('text_filename', 'str', default='text.txt',
                          description='Filename of the output text file, if `use_title` is False.'),
        ]

    def __init__(self, args):
        super().__init__(args)
        self.use_title = self.args['use_title']
        self.filename = self.args['text_filename']

    def write(self) -> None:
        self._cleanup()

        title = self.structure.title
        title_text = self._get_content(title) if title else ''
        filename = purify_name(self._get_filename(title) + '.txt' if self.use_title else self.filename)
        with (self.out_dir / filename).open('wt') as f:
            if title:
                f.write(title_text + '\n\n')

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

    def __write_volume(self, volume: Structure, f):
        if title := volume.title:
            f.write(self._get_content(title) + '\n\n')

        if len(volume.contents) > 0:
            f.write(volume.contents[0].content)
            f.write('\n\n')

        for i in range(len(volume.children)):
            chapter = volume.children[i]
            title = chapter.title
            f.write(self._get_content(title) + '\n\n')
            f.write(chapter.contents[0].content)
            if i != len(volume.children) - 1:
                f.write('\n\n')
