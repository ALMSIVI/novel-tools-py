import os
from typing import Optional
from framework import Reader
from common import NovelData, Type


class TocReader(Reader):
    """Reads from a table of contents (toc) file."""

    def __init__(self, args):
        """
        Arguments:

        - toc_filename (str, optional, default='toc.txt'): Filename of the toc file. This file should be generated from
          TocWriter.
        - in_dir (str, optional): The directory to read the toc file from. Required if the filename does not contain the
          path.
        - encoding (str, optional, default='utf-8'): Encoding of the toc file.
        - has_volume(bool): Specifies whether the toc contains volumes.
        """
        self.has_volume = args['has_volume']
        filename = args.get('toc_filename', 'toc.txt')
        filename = filename if os.path.isfile(filename) else os.path.join(args['in_dir'], filename)
        self.file = open(filename, 'rt', encoding=args.get('encoding', 'utf-8'))
        self.indices = {}

    def cleanup(self):
        self.file.close()

    def read(self) -> Optional[NovelData]:
        line = self.file.readline()
        if not line:
            return None

        elements = line.split('\t')
        line_num = None
        if elements[0] == '':
            # Must be chapter
            content = elements[1]
            data_type = Type.CHAPTER_TITLE
            if len(elements) > 2:
                line_num = int(elements[2])
        else:
            # Could be volume or chapter depending on has_volume
            content = elements[0]
            data_type = Type.VOLUME_TITLE if self.has_volume else Type.CHAPTER_TITLE
            if len(elements) > 1:
                line_num = int(elements[1])

        if data_type not in self.indices:
            self.indices[data_type] = 0
        self.indices[data_type] += 1
        data = NovelData(content.strip(), data_type, self.indices[data_type])
        if line_num is not None:
            data.set(line_num=line_num)

        return data
