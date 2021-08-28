import os
from typing import Optional
from natsort import natsorted
from common import NovelData, Type, ACC, FieldMetadata
from framework import Reader


class DirectoryReader(Reader, ACC):
    """
    Reads from a directory structure. This directory should be generated from FileWriter, as it will follow certain
    conventions, such as the first line of the chapter file being the title.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('in_dir', 'str',
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
                          description='Encoding of the chapter file(s).')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.in_dir = args['in_dir']
        self.read_contents = args['read_contents']
        self.discard_chapters = args['discard_chapters']
        self.default_volume = args['default_volume']
        self.encoding = args['encoding']
        self.intro_filename = args['intro_filename']

        # Create the list of volumes/directories to look for
        self.read_intro = self.read_contents and os.path.isfile(os.path.join(self.in_dir, self.intro_filename))
        self.volumes = [dir_name for dir_name in natsorted(os.listdir(self.in_dir)) if
                        os.path.isdir(os.path.join(self.in_dir, dir_name))]
        if self.default_volume in self.volumes:
            self.volumes = [self.default_volume]

        self.chapters = []
        self.curr_volume = -1
        self.curr_chapter = 0  # The true chapter index, i.e., it will be affected by discard_chapters.
        self.chapter_index = -1  # The index in self.chapters, and will be reset when entering a new volume.
        self.chapter_file = None

    def cleanup(self):
        if self.chapter_file and not self.chapter_file.closed:
            self.chapter_file.close()

    def read(self) -> Optional[NovelData]:
        if self.read_intro:
            # Read intro
            self.read_intro = False
            with open(os.path.join(self.in_dir, self.intro_filename), 'rt', encoding=self.encoding) as f:
                return NovelData(f.read(), Type.BOOK_INTRO)

        # Read chapter contents
        if self.chapter_file:
            contents = self.chapter_file.read()
            self.chapter_file.close()
            self.chapter_file = None
            return NovelData(contents, Type.CHAPTER_CONTENT)

        self.chapter_index += 1
        # Proceed to next volume
        if self.curr_volume == -1 or self.chapter_index == len(self.chapters):
            self.curr_volume += 1
            if self.curr_volume == len(self.volumes):
                # End of novel
                return None

            volume_name = self.volumes[self.curr_volume]
            volume_dir = os.path.join(self.in_dir, volume_name)
            self.chapters = [filename for filename in natsorted(os.listdir(volume_dir)) if
                             os.path.isfile(os.path.join(volume_dir, filename))]

            # Check if there are any volume intro files; if so, move the file to the beginning of the list
            if self.intro_filename in self.chapters:
                self.chapters.remove(self.intro_filename)
                self.chapters.insert(0, self.intro_filename)

            self.chapter_index = -1
            if self.discard_chapters:
                self.curr_chapter = 0

            if volume_name != self.default_volume:
                return NovelData(volume_name, Type.VOLUME_TITLE, self.curr_volume + 1, filename=volume_name)
            else:
                self.chapter_index += 1

        # Read the next chapter or volume intro
        filename = self.chapters[self.chapter_index]
        full_filename = os.path.join(self.in_dir, self.volumes[self.curr_volume], filename)
        if filename == self.intro_filename and self.read_contents:
            with open(full_filename, 'rt', encoding=self.encoding) as f:
                return NovelData(f.read(), Type.VOLUME_INTRO)

        # Read chapter title
        self.curr_chapter += 1
        self.chapter_file = open(full_filename, 'rt', encoding=self.encoding)
        title = self.chapter_file.readline()
        if not self.read_contents:
            self.chapter_file.close()
            self.chapter_file = None
        return NovelData(title.strip(), Type.CHAPTER_TITLE, self.curr_chapter, filename=filename)
