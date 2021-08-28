from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class Null:
    """A placeholder class to be flagged as default None."""
    pass


class FieldMetadata:
    def __init__(self, name: str, field_type: str, *, optional: bool = False, default: Any = Null(),
                 options: list = None, include_when: Callable[[dict], bool] = None, description: str):
        self.name = name
        self.type = field_type
        self.optional = True if type(default) is not Null else optional
        self.default = default
        self.options = options
        self.include_when = include_when
        self.description = description

    @property
    def docstring(self):
        optional = ', optional' if self.optional else ''
        default = f', default={self.default}' if type(self.default) is not Null else ''
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

    @classmethod
    def extract_fields(cls, args: dict) -> dict:
        metadata_dict = {metadata.name: metadata for metadata in cls.required_fields()}
        fields = {}
        for key, val in args.items():
            if key in metadata_dict:
                metadata_dict.pop(key)
                fields[key] = val

        for key, val in metadata_dict.items():
            if not val.optional and val.include_when(args):
                raise ValueError(f'Required argument {key} not found')
            if type(val.default) is not Null:
                fields[key] = val.default

        return fields

    @classmethod
    def docstring(cls) -> str:
        metadata_list = cls.required_fields()
        return '\n'.join(['- ' + metadata.docstring for metadata in metadata_list])
