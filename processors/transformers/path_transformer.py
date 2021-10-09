from pathlib import Path
from framework import Processor
from common import NovelData, ACC, FieldMetadata


class PathTransformer(Processor, ACC):
    """
    Given `in_dir`, this transformer will replace all `Path` fields with the paths relative to its `in_dir`.
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('in_dir', 'Path',
                          description='The parent directory for all the novel data.'),
            FieldMetadata('fields', 'list[str]', default=['source'],
                          description='A list of fields of type `Path` to transform.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        self.in_dir = args['in_dir']
        self.fields = args['fields']

    def process(self, data: NovelData) -> NovelData:
        for field in self.fields:
            path = data.get(field, None)
            if isinstance(path, Path):
                data.set(**{field: path.relative_to(self.in_dir)})
        return data
