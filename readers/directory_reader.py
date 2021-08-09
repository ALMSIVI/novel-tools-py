import os
from natsort import natsorted
from common import NovelData, Type
from framework import Reader


class DirectoryReader(Reader):
    """
    Reads from a directory structure. This directory should be generated from FileWriter, as it will follow certain
    conventions, such as the first line of the chapter file being the title.
    """

    def __init__(self, args):
        """
        Arguments:
        - read_contents (bool): If set to true, will open the files to read the contents.
        - default_volume (optional, str): If the novel doesn't have volumes but all chapters are stored in a directory,
          then the variable would store the directory name.
        """
        self.in_dir = args['in_dir']  # Will be supplied by the program, not the config
        self.read_contents = args['read_contents']
        self.default_volume = args.get('default_volume', None)

        # Create the list of volumes/directories to look for
        self.read_intro = self.read_contents and os.path.exists(os.path.join(self.in_dir, '_intro.txt'))
        self.volumes = [dir_name for dir_name in natsorted(os.listdir(self.in_dir)) if
                        os.path.isdir(os.path.join(self.in_dir, dir_name))]
        self.chapters = []
        self.curr_volume = -1
        self.curr_chapter = -1
        self.chapter_file = None

    def cleanup(self):
        if self.chapter_file and not self.chapter_file.closed:
            self.chapter_file.close()

    def read(self) -> NovelData:
        if self.read_intro:
            # Read intro
            self.read_intro = False
            with open(os.path.join(self.in_dir, '_intro.txt'), 'rt') as f:
                return NovelData(Type.BOOK_INTRO, f.read())

        # Read chapter contents
        if self.chapter_file:
            contents = self.chapter_file.read()
            self.chapter_file.close()
            self.chapter_file = None
            return NovelData(Type.CHAPTER_CONTENT, contents)

        self.curr_chapter += 1
        # Proceed to next volume
        if self.curr_volume == -1 or self.curr_chapter == len(self.chapters):
            self.curr_volume += 1
            if self.curr_volume == len(self.volumes):
                # End of novel
                return None

            volume_name = self.volumes[self.curr_volume]
            volume_dir = os.path.join(self.in_dir, volume_name)
            self.chapters = [filename for filename in natsorted(os.listdir(volume_dir)) if
                             os.path.isfile(os.path.join(volume_dir, filename))]
            self.curr_chapter = -1
            if volume_name != self.default_volume:
                return NovelData(Type.VOLUME_TITLE, volume_name, self.curr_volume + 1, filename=volume_name)

        # Read the next chapter
        filename = self.chapters[self.curr_chapter]
        full_filename = os.path.join(self.in_dir, self.volumes[self.curr_volume], filename)
        if filename == '_intro.txt' and self.read_contents:
            # Volume intro
            with open(full_filename, 'rt') as f:
                return NovelData(Type.VOLUME_INTRO, f.read())

        # Read chapter title
        self.chapter_file = open(full_filename, 'rt')
        title = self.chapter_file.readline()
        if not self.read_contents:
            self.chapter_file.close()
            self.chapter_file = None
        return NovelData(Type.CHAPTER_TITLE, title.strip(), self.curr_chapter, filename=filename)
