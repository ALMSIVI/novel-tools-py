from pydantic import BaseModel
from pydantic.fields import ModelField
from pathlib import Path
from types import GenericAlias
from novel_tools.utils import get_all_classes, format_text


def field_doc(field: ModelField) -> str:
    name = field.name
    field_type = str(field.outer_type_) if type(field.outer_type_) is GenericAlias else field.type_.__name__
    optional = ', optional' if not field.required else ''
    default = f', default={field.default}' if field.default is not None else ''
    description = field.field_info.description
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
                    fields = '\n'.join([f'- {field_doc(field)}' for field in stage_options.__fields__.values()])
                    f.write(fields)
                    f.write('\n')
                f.write('\n')
