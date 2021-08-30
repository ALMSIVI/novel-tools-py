import os
from typing import Optional
from textwrap import dedent
from common import NovelData, Type


def assert_data(data: NovelData, content: str, data_type: Type, index: Optional[int] = None, **kwargs):
    assert data.content == content
    assert data.type == data_type
    assert data.index == index
    for key, value in kwargs.items():
        assert data.get(key) == value


def format_structure(structure: str) -> str:
    return dedent(structure).strip()


def assert_file(expected: str, actual: str):
    with open(expected, 'rt') as f:
        content1 = f.read()

    with open(actual, 'rt') as f:
        content2 = f.read()

    assert content1 == content2


def assert_directory(expected: str, actual: str):
    list1 = os.listdir(expected)
    list2 = os.listdir(actual)
    assert sorted(list1) == sorted(list2)

    for name in list1:
        name1 = os.path.join(expected, name)
        name2 = os.path.join(actual, name)
        if os.path.isfile(name1):
            assert_file(name1, name2)
        else:
            assert_directory(name1, name2)
