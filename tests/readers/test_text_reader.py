from pathlib import Path
from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from typing import Iterator
from novel_tools.common import NovelData, Type
from novel_tools.readers.text_reader import TextReader


@fixture
def read(mocker: MockerFixture, request: FixtureRequest):
    text, args = request.node.get_closest_marker('data').args
    mocker.patch('pathlib.Path.open', mocker.mock_open(read_data=text))
    return TextReader(args | {'filename': 'text.txt', 'in_dir': Path()}).read()


@mark.data('line\n ', {})
def test_read(read: Iterator[NovelData]):
    assert next(read) == NovelData('line', Type.UNRECOGNIZED)
    assert next(read) == NovelData('', Type.UNRECOGNIZED)
    with raises(StopIteration):
        next(read)


@mark.data('line\n ', {'verbose': True})
def test_verbose(read: Iterator[NovelData]):
    assert next(read) == NovelData('line', Type.UNRECOGNIZED, source=Path('text.txt'), line_num=1, raw='line')
    assert next(read) == NovelData('', Type.UNRECOGNIZED, source=Path('text.txt'), line_num=2, raw='')
    with raises(StopIteration):
        next(read)


@mark.data('line 1\n\nline 2\n\n\nline 3\n\n\n\nline 4', {'merge_newlines': True})
def test_merge_newlines(read: Iterator[NovelData]):
    assert next(read) == NovelData('line 1', Type.UNRECOGNIZED)
    assert next(read) == NovelData('line 2', Type.UNRECOGNIZED)
    assert next(read) == NovelData('', Type.UNRECOGNIZED)
    assert next(read) == NovelData('line 3', Type.UNRECOGNIZED)
    assert next(read) == NovelData('', Type.UNRECOGNIZED)
    assert next(read) == NovelData('line 4', Type.UNRECOGNIZED)
    with raises(StopIteration):
        next(read)
