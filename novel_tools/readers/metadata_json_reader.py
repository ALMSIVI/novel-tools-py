from pydantic import BaseModel, Field
import json
from pathlib import Path
from typing import Iterator
from novel_tools.framework import NovelData, Type, Reader


class Options(BaseModel):
    metadata_filename: str = Field(default='metadata.json',
                                   description='Filename of the metadata json file. The metadata MUST contain a '
                                               '\'title\' field.')
    in_dir: Path | None = Field(description='The directory to read the metadata file from. Required if the filename '
                                            'does not contain the path.')
    encoding: str = Field(default='utf-8', description='Encoding of the json file.')


class MetadataJsonReader(Reader):
    """
    Reads a json that contains the metadata of the book file. Will only generate a BOOK_TITLE, with the `others` field
    populated with the other metadata.
    """

    def __init__(self, args):
        options = Options(**args)
        json_path = Path(options.metadata_filename)
        json_path = json_path if json_path.is_file() else options.in_dir / json_path
        with json_path.open('rt', encoding=options.encoding) as f:
            self.metadata = json.load(f)

        if 'title' not in self.metadata:
            raise ValueError('Metadata does not contain "title" field.')

    def read(self) -> Iterator[NovelData]:
        title = self.metadata['title']
        self.metadata.pop('title')
        yield NovelData(title, Type.BOOK_TITLE, **self.metadata)
