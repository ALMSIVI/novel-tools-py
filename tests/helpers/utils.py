from typing import Optional
import platform
from textwrap import dedent
from common import NovelData, Type


def assert_data(data: NovelData, content: str, data_type: Type, index: Optional[int] = None, **kwargs):
    assert data.content == content
    assert data.data_type == data_type
    assert data.index == index
    for key, value in kwargs.items():
        assert data.get(key) == value


def format_structure(structure: str) -> str:
    return dedent(structure).strip()