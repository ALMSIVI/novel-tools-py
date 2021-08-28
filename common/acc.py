from abc import ABC, abstractmethod
from typing import Any


class FieldMetadata:
    def __init__(self, name: str, field_type: str, *, optional: bool = False, default: Any = None,
                 description: str):
        self.name = name
        self.type = field_type
        self.optional = optional
        self.default = default
        self.description = description

    @property
    def docstring(self):
        optional = ', optional' if self.optional else ''
        default = f', default={self.default}' if self.default else ''
        return f'{self.name} ({self.type + optional + default}): {self.description}'


class ACC(ABC):
    """
    ACC stands for Argument-Constructed Class. It means that the class will have an __init__() method with a single
    `args` dict.

    Children of this class requires a `required_fields` property that exposes the fields that needs to be extracted from
    the arguments. In return, the class will provide a method called `extract_args` that will extract all fields needed
    to initialize the object, and fill in any optional fields.

    Having this `required_fields` property is beneficial because:
    - We can automatically generate documentation for these classes;
    - If we want to build a GUI, we can use the properties of these fields to dynamically construct configuration form
      controls.
    """

    @staticmethod
    @abstractmethod
    def required_fields() -> list[FieldMetadata]:
        pass

    def extract_fields(self, args: dict) -> dict:
        metadata_dict = {metadata.name: metadata for metadata in self.required_fields()}
        fields = {}
        for key, val in args.items():
            if key in metadata_dict:
                metadata_dict.pop(key)
                fields[key] = val

        for key, val in metadata_dict.items():
            if not val.optional:
                raise ValueError(f'Required argument {key} not found')
            fields[key] = val.default

        return fields

    @classmethod
    def docstring(cls) -> str:
        metadata_list = cls.required_fields()
        return '\n'.join([metadata.docstring for metadata in metadata_list])
