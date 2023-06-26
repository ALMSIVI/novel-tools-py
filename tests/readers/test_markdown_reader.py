from pathlib import Path
from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from typing import Iterator
from novel_tools.framework import NovelData, Type
from novel_tools.readers.markdown_reader import MarkdownReader


@fixture
def read(mocker: MockerFixture, request: FixtureRequest):
    text, args = request.node.get_closest_marker('data').args
    mocker.patch('pathlib.Path.open', mocker.mock_open(read_data=text))
    return MarkdownReader(args | {'filename': 'text.md', 'in_dir': Path()}).read()


@mark.data('# Title\n\nText 1\n\n## Volume\n\nText 2\n\n### Chapter\n\nText 3\n\n ', {})
def test_read(read: Iterator[NovelData]):
    assert next(read) == NovelData('Title', Type.BOOK_TITLE)
    assert next(read) == NovelData('Text 1', Type.UNRECOGNIZED)
    assert next(read) == NovelData('Volume', Type.VOLUME_TITLE)
    assert next(read) == NovelData('Text 2', Type.UNRECOGNIZED)
    assert next(read) == NovelData('Chapter', Type.CHAPTER_TITLE)
    assert next(read) == NovelData('Text 3', Type.UNRECOGNIZED)
    assert next(read) == NovelData('', Type.UNRECOGNIZED)
    with raises(StopIteration):
        next(read)


@mark.data('line\n\n ', {'verbose': True})
def test_verbose(read: Iterator[NovelData]):
    assert next(read) == NovelData('line', Type.UNRECOGNIZED, source=Path('text.md'), line_num=1, raw='line')
    assert next(read) == NovelData('', Type.UNRECOGNIZED, source=Path('text.md'), line_num=3, raw='')
    with raises(StopIteration):
        next(read)


@mark.data('# Volume\n\n## Chapter\n\n### Unknown', {'levels': {'1': 'volume_title', '2': 'chapter_title'}})
def test_levels(read: Iterator[NovelData]):
    assert next(read) == NovelData('Volume', Type.VOLUME_TITLE)
    assert next(read) == NovelData('Chapter', Type.CHAPTER_TITLE)
    assert next(read) == NovelData('### Unknown', Type.UNRECOGNIZED)
    with raises(StopIteration):
        next(read)
