from pydantic import Field
from novel_tools.common import NovelData, Type
from .__structure_writer__ import StructureWriter, Structure, BaseOptions
from novel_tools.utils import purify_name


class Options(BaseOptions):
    default_volume: str = Field(default='default',
                                description='If the volume does not have volumes, specify the directory name to place '
                                            'the chapter files.')
    intro_filename: str = Field(default='_intro.txt',
                                description='The filename of the book/volume introduction file.')


class DirectoryWriter(StructureWriter):
    """
    Generates volume directories and chapter files. If there is no volume, a default volume will be created.
    It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled. One
    can also use the same transformer to attach a 'filename' field, and the writer will prioritize this field.
    """

    def __init__(self, args):
        options = Options(**args)
        self.init_fields(options)
        self.default_volume = options.default_volume
        self.intro_filename = options.intro_filename

    def write(self) -> None:
        self._cleanup()

        # Write intro
        if len(self.structure.contents) > 0:
            with (self.out_dir / self.intro_filename).open('wt') as f:
                f.write(self.structure.contents[0].content)

        # Write volume
        if self.has_volumes:
            for volume in self.structure.children:
                self.__write_volume(volume)
        else:
            default_volume = Structure()
            default_volume.title = NovelData('', Type.VOLUME_TITLE, filename=self.default_volume)
            default_volume.children = self.structure.children
            self.__write_volume(default_volume)

    def __write_volume(self, volume: Structure):
        title = volume.title
        filename = purify_name(self._get_filename(title))
        volume_path = self.out_dir / filename
        volume_path.mkdir(exist_ok=True)

        if len(volume.contents) > 0:
            with (volume_path / self.intro_filename).open('wt') as f:
                f.write(volume.contents[0].content)

        # Write chapter
        for chapter in volume.children:
            title = chapter.title
            filename = purify_name(self._get_filename(title))
            chapter_path = volume_path / (filename + '.txt')
            with chapter_path.open('wt') as f:
                f.write(self._get_content(title) + '\n\n')
                f.write(chapter.contents[0].content)
