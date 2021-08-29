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


def assert_file(filename1: str, filename2: str):
    with open(filename1, 'rt') as f:
        content1 = f.read()

    with open(filename2, 'rt') as f:
        content2 = f.read()

    assert content1 == content2


def assert_directory(dir1: str, dir2: str):
    list1 = os.listdir(dir1)
    list2 = os.listdir(dir2)
    assert sorted(list1) == sorted(list2)

    for name in list1:
        name1 = os.path.join(dir1, name)
        name2 = os.path.join(dir2, name)
        if os.path.isfile(name1):
            assert_file(name1, name2)
        else:
            assert_directory(name1, name2)
