from abc import ABC, abstractmethod
from typing import Any


class Null:
    """A placeholder class to be flagged as default None."""
    pass


class FieldMetadata:
    def __init__(self, name: str, field_type: str, *, optional: bool = False, default: Any = Null(),
                 options: list[Any] = None, description: str, properties: list['FieldMetadata'] = None):
        self.name = name
        self.type = field_type
        self.optional = True if type(default) is not Null else optional
        self.default = default
        self.options = options
        self.description = description
        self.properties = properties

    def docstring(self, indent: int = 2):
        """indent refers to the indentation of object properties."""
        optional = ', optional' if self.optional else ''
        default = f', default={self.default}' if type(self.default) is not Null else ''
        options = f', options={self.options}' if self.options is not None else ''
        properties = '\n' + ' ' * indent + 'Properties:\n' + '\n'.join(
            [' ' * indent + '- ' + prop.docstring(indent + 2) for prop in self.properties]) \
            if self.properties is not None else ''

        return f'{self.name} ({self.type + optional + default + options}): {self.description}{properties}'


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
        return cls.__extract_fields(args, cls.required_fields())

    @classmethod
    def __extract_fields(cls, args: dict, required_fields: list[FieldMetadata]):
        metadata_dict: dict[str, FieldMetadata] = {metadata.name: metadata for metadata in required_fields}
        fields = {}
        for key, val in args.items():
            if key in metadata_dict:
                metadata = metadata_dict.pop(key)
                if metadata.options is not None and val not in metadata.options:
                    raise ValueError(f'argument {key} is {val} but the options are {metadata.options}')

                if metadata.properties is not None:
                    val = cls.__extract_fields(val, metadata.properties)

                fields[key] = val

        for key, val in metadata_dict.items():
            if not val.optional:
                raise ValueError(f'Required argument {key} not found')
            if type(val.default) is not Null:
                fields[key] = val.default

        return fields

    @classmethod
    def docstring(cls) -> str:
        metadata_list = cls.required_fields()
        return '\n'.join(['- ' + metadata.docstring() for metadata in metadata_list])
