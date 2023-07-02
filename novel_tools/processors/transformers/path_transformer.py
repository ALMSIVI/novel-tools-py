from pydantic import BaseModel, DirectoryPath, Field
from pathlib import Path
from novel_tools.framework import NovelData, Processor


class Options(BaseModel):
    in_dir: DirectoryPath = Field(description='The parent directory for all the novel data.')
    fields: list[str] = Field(default=['source'], description='A list of fields of type `Path` to transform.')


class PathTransformer(Processor):
    """
    Given `in_dir`, this transformer will replace all `Path` fields with the paths relative to its `in_dir`.
    """

    def __init__(self, args):
        options = Options(**args)
        self.in_dir = options.in_dir
        self.fields = options.fields

    def process(self, data: NovelData) -> NovelData:
        for field in self.fields:
            path = data.get(field, None)
            if isinstance(path, Path):
                data.set(**{field: path.relative_to(self.in_dir)})
        return data
