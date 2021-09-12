from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from textwrap import dedent
from typing import Iterator
from common import NovelData, Type
from readers.csv_reader import CsvReader


def format_csv(csv: str):
    return dedent(csv).strip()


@fixture
def read(mocker: MockerFixture, request: FixtureRequest):
    csv = request.node.get_closest_marker('data').args[0]
    csv = format_csv(csv)
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    return CsvReader({'in_dir': ''}).read()


@mark.data('''
    type,content,index,formatted,line_num
    volume_title,Test Volume,1,Test,1
    chapter_title,Test Chapter,1,Test,2
''')
def test_read(read: Iterator[NovelData]):
    assert next(read) == NovelData('Test Volume', Type.VOLUME_TITLE, 1, formatted='Test', line_num=1)
    assert next(read) == NovelData('Test Chapter', Type.CHAPTER_TITLE, 1, formatted='Test', line_num=2)
    with raises(StopIteration):
        next(read)


def test_invalid(mocker: MockerFixture):
    csv = format_csv('''
    type
    volume_title
    ''')
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    with raises(ValueError, match='csv does not contain valid columns.'):
        CsvReader({'in_dir': ''})
