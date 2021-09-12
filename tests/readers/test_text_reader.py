from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from typing import Iterator
from common import NovelData, Type
from readers.text_reader import TextReader


@fixture
def read(mocker: MockerFixture, request: FixtureRequest):
    text, args = request.node.get_closest_marker('data').args
    mocker.patch('builtins.open', mocker.mock_open(read_data=text))
    reader = TextReader(args | {'filename': 'text.txt', 'in_dir': ''})
    return reader.read()


@mark.data('line\n ', {})
def test_read(read: Iterator[NovelData]):
    assert next(read) == NovelData('line', Type.UNRECOGNIZED)
    assert next(read) == NovelData('', Type.UNRECOGNIZED)
    with raises(StopIteration):
        next(read)


@mark.data('line\n ', {'verbose': True})
def test_verbose(read: Iterator[NovelData]):
    assert next(read) == NovelData('line', Type.UNRECOGNIZED, source='text.txt', line_num=1, raw='line')
    assert next(read) == NovelData('', Type.UNRECOGNIZED, source='text.txt', line_num=2, raw='')
    with raises(StopIteration):
        next(read)
