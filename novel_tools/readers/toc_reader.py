from pydantic import BaseModel, DirectoryPath, Field
from pathlib import Path
from typing import Iterator
from novel_tools.framework import NovelData, Type, Reader


class Options(BaseModel):
    toc_filename: str = Field(default='toc.txt', description='Filename of the toc file. This file should be generated '
                                                             'from `TocWriter`.')
    in_dir: DirectoryPath | None = Field(default=None, description='The directory to read the toc file from. Required '
                                                                   'if the filename does not contain the path.')
    encoding: str = Field(default='utf-8', description='Encoding of the toc file.')
    has_volume: bool = Field(description='Specifies whether the toc contains volumes.')
    discard_chapters: bool = Field(description='If set to True, will start from chapter 1 again when entering a '
                                               'new volume.')


class TocReader(Reader):
    """Reads from a table of contents (toc) file."""

    def __init__(self, args):
        options = Options(**args)
        self.has_volume = options.has_volume
        self.discard_chapters = options.discard_chapters
        self.filename = Path(options.toc_filename)
        self.in_dir = options.in_dir
        self.encoding = options.encoding

    def read(self) -> Iterator[NovelData]:
        toc_path = self.filename if self.filename.is_file() else self.in_dir / self.filename
        with toc_path.open('rt', encoding=self.encoding) as f:
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
