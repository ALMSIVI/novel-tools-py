import os
from typing import Iterator
from framework import Reader
from common import NovelData, Type, ACC, FieldMetadata


class TocReader(Reader, ACC):
    """Reads from a table of contents (toc) file."""

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('toc_filename', 'str', default='toc.txt',
                          description='Filename of the toc file. This file should be generated from `TocWriter`.'),
            FieldMetadata('in_dir', 'str', optional=True,
                          description='The directory to read the toc file from. Required if the filename does not '
                                      'contain the path.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the toc file.'),
            FieldMetadata('has_volume', 'bool',
                          description='Specifies whether the toc contains volumes.'),
            FieldMetadata('discard_chapters', 'bool',
                          description='If set to True, will start from chapter 1 again when entering a new volume.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.has_volume = args['has_volume']
        self.discard_chapters = args['discard_chapters']
        self.filename = args['toc_filename']
        self.in_dir = args['in_dir']
        self.encoding = args['encoding']

    def read(self) -> Iterator[NovelData]:
        full_filename = self.filename if os.path.isfile(self.filename) else os.path.join(self.in_dir, self.filename)
        with open(full_filename, 'rt', encoding=self.encoding) as f:
            indices = {Type.VOLUME_TITLE: 0, Type.CHAPTER_TITLE: 0}
            for line in f:
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

                    if data_type == Type.VOLUME_TITLE and self.discard_chapters:
                        indices[Type.CHAPTER_TITLE] = 0

                indices[data_type] += 1
                data = NovelData(content.strip(), data_type, indices[data_type])
                if line_num is not None:
                    data.set(line_num=line_num)

                yield data
