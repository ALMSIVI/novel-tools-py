from pydantic import BaseModel, DirectoryPath, FilePath
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from pathlib import Path
from typing import Any, Union, get_args, get_origin
from types import GenericAlias, NoneType, UnionType
from novel_tools.utils import get_all_classes, format_text


def get_type(annotation: type) -> str:
    if type(annotation) is GenericAlias:  # Example: list[str]
        return str(annotation)

    if get_origin(annotation) is UnionType or get_origin(annotation) is Union:
        types = get_args(annotation)
        if len(types) > 2 or types[-1] is not NoneType:  # Example: str | Path
            return str(annotation)
        # Example: str | None. We only want to display str because we will attach "optional" afterward.
        return get_type(types[0])

    if annotation is DirectoryPath:
        return 'DirectoryPath'

    if annotation is FilePath:
        return 'FilePath'

    return annotation.__name__  # Example: str


def default_is_none(default: Any) -> bool:
    return default is None or default is PydanticUndefined


def field_doc(name: str, info: FieldInfo) -> str:
    field_type = get_type(info.annotation)
    optional = ', optional' if not info.is_required() else ''
    default = f', default={info.default}' if not default_is_none(info.default) else ''
    description = info.description
    return f'{name} ({field_type + optional + default}): {description}'


def docgen(doc_filename: str | None = None):
    """
    Generates documentation for all specified ACCs.

    Args:
        doc_filename: The output doc filename. Default is 'docs.md' under the config's directory if config_filename is
                      specified, or the current directory if not.
    """
    all_options = get_all_classes()

    if doc_filename is None:
        doc_filename = Path() / 'docs.md'
    else:
        doc_filename = Path(doc_filename)

    with doc_filename.open('wt') as f:
        for stage, stage_classes_dict in all_options.items():
            f.write(f'## {stage.title()}\n\n')
            for stage_name, (stage_class, stage_options) in stage_classes_dict.items():
                f.write(f'### {stage_name}\n\n')
                f.write('**Description:**\n\n')
                if stage_class.__doc__ is not None:
                    f.write(format_text(stage_class.__doc__))
                    f.write('\n')

                if stage_options is not None:
                    stage_options: BaseModel
                    f.write('\n**Arguments:**\n\n')
                    fields = '\n'.join(
                        [f'- {field_doc(name, info)}' for name, info in stage_options.model_fields.items()])
                    f.write(fields)
                    f.write('\n')
                f.write('\n')
