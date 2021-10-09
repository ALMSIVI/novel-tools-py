from pathlib import Path
from typing import Iterator
from framework import Reader
from common import NovelData, Type, ACC, FieldMetadata


class MarkdownReader(Reader, ACC):
    """
    Reads from a Markdown file. Only a strict subset of Markdown is supported. Namely, only titles (lines starting with
    `#`'s) will be recognized. Also, if a paragraph is split on several lines (separated by a single newline character),
    they will be treated as several paragraphs instead of one.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('md_filename', 'str', default='text.md',
                          description='The filename of the markdown file.'),
            FieldMetadata('in_dir', 'Path', optional=True,
                          description='The directory to read the text file from. Required if the filename does not '
                                      'contain the path.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='The encoding of the file.'),
            FieldMetadata('verbose', 'bool', default=False,
                          description='If set to True, additional information, including line number and raw line '
                                      'info, will be added to the data object.'),
            FieldMetadata('levels', 'dict[str, int]', default={1: 'book_title', 2: 'volume_title', 3: 'chapter_title'},
                          description='Specifies what level the header should be for each type.'),
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.md_path = Path(args['md_filename'])
        self.in_dir = args['in_dir']
        self.encoding = args['encoding']
        self.verbose = args['verbose']
        self.levels = {int(key): Type[value.upper()] for key, value in args['levels'].items()}

    def read(self) -> Iterator[NovelData]:
        md_path = self.md_path if self.md_path.is_file() else self.in_dir / self.md_path
        with md_path.open('rt', encoding=self.encoding) as f:
            line_num = 0
            prev_newline = False
            for line in f:
                line_num += 1
                content = line.strip()

                # In Markdown, double newline represents a new paragraph
                if content == '':
                    prev_newline = not prev_newline
                    if prev_newline:
                        continue
                else:
                    prev_newline = False

                data_type = Type.UNRECOGNIZED
                if content.startswith('#'):
                    index = content.index(' ')
                    if index in self.levels:
                        data_type = self.levels[index]
                        content = content[index + 1:]

                args = {'source': md_path, 'line_num': line_num, 'raw': line.rstrip()} if self.verbose else {}
                yield NovelData(content, data_type, **args)
