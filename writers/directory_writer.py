import os
from common import FieldMetadata
from .__structure_writer__ import StructureWriter, Structure


class DirectoryWriter(StructureWriter):
    """
    Generates volume directories and chapter files. If there is no volume, a default volume will be created.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled. One
    can also use the same transformer to attach a 'filename' field, and the writer will prioritize this field.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return StructureWriter.required_fields() + [
            FieldMetadata('default_volume', 'str', default='default',
                          description='If the volume does not have volumes, specify the directory name to place the '
                                      'chapter files.'),
            FieldMetadata('intro_filename', 'str', default='_intro.txt',
                          description='The filename of the book/volume introduction file(s).')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        super().__init__(args)
        self.default_volume = args['default_volume']
        self.intro_filename = args['intro_filename']

    def write(self) -> None:
        self.cleanup()

        # Write intro
        if len(self.structure.contents) > 0:
            with open(os.path.join(self.out_dir, self.intro_filename), 'wt') as f:
                f.write(self.structure.contents[0])

        # Write volume
        if self.has_volumes:
            for volume in self.structure.children:
                self.write_volume(volume)
        else:
            default_volume = Structure()
            default_volume.filename = self.default_volume
            default_volume.children = self.structure.children
            self.write_volume(default_volume)

    def write_volume(self, volume: Structure):
        volume_dir = os.path.join(self.out_dir, volume.filename)
        if not os.path.isdir(volume_dir):
            os.mkdir(volume_dir)

        if len(volume.contents) > 0:
            with open(os.path.join(volume_dir, self.intro_filename), 'wt') as f:
                f.write(volume.contents[0])

        # Write chapter
        for chapter in volume.children:
            chapter_filename = os.path.join(volume_dir, chapter.filename + '.txt')
            with open(chapter_filename, 'wt') as f:
                f.write(chapter.title + '\n\n')
                f.write(chapter.contents[0])
