import os
from typing import Optional
from framework import Reader
from common import NovelData, Type


class TocReader(Reader):
    """Reads from a table of content file."""

    def __init__(self, args):
        """
        Arguments:
        - toc_filename (optional, str): Filename of the toc file. This file should be generated from TocWriter. Default
          is toc.txt.
        """
        self.file = open(os.path.join(args['in_dir'], args.get('toc_filename', 'toc.txt')), 'rt')

    def cleanup(self):
        self.file.close()

    def read(self) -> Optional[NovelData]:
        line = self.file.readline()
        if not line:
            return None

        elements = line.strip().split('\t')
        line_num = None
        if elements[0] == '':
            # Chapter
            content = elements[1]
            data_type = Type.CHAPTER_TITLE
            if len(elements) > 2:
                line_num = int(elements[2])
        else:
            # Volume
            content = elements[0]
            data_type = Type.VOLUME_TITLE
            if len(elements) > 2:
                line_num = int(elements[1])

        data = NovelData(data_type, content)
        if line_num:
            data.set(line_num=line_num)

        return data
