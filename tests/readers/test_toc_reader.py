from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from typing import Iterator
from common import NovelData, Type
from readers.toc_reader import TocReader
from utils import format_text


@fixture
def read(mocker: MockerFixture, request: FixtureRequest):
    toc, args = request.node.get_closest_marker('data').args
    toc = format_text(toc)
    mocker.patch('builtins.open', mocker.mock_open(read_data=toc))
    return TocReader(args | {'in_dir': ''}).read()


@mark.data('''
    Volume 1
    \tChapter 1
    \tChapter 2
    Volume 2
    \tChapter 3
''', {'has_volume': True, 'discard_chapters': False})
def test_read(read: Iterator[NovelData]):
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    assert next(read) == NovelData('Chapter 2', Type.CHAPTER_TITLE, 2)
    assert next(read) == NovelData('Volume 2', Type.VOLUME_TITLE, 2)
    assert next(read) == NovelData('Chapter 3', Type.CHAPTER_TITLE, 3)
    with raises(StopIteration):
        next(read)


@mark.data('''
    Volume 1\t1
    \tChapter 1\t2
    Volume 2\t25
    \tChapter 2\t27
''', {'has_volume': True, 'discard_chapters': False})
def test_read_line_num(read: Iterator[NovelData]):
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, line_num=1)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, line_num=2)
    assert next(read) == NovelData('Volume 2', Type.VOLUME_TITLE, 2, line_num=25)
    assert next(read) == NovelData('Chapter 2', Type.CHAPTER_TITLE, 2, line_num=27)
    with raises(StopIteration):
        next(read)


@mark.data('''
    Chapter 1
    Chapter 2
    Chapter 3
''', {'has_volume': False, 'discard_chapters': False})
def test_read_no_volume(read: Iterator[NovelData]):
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    assert next(read) == NovelData('Chapter 2', Type.CHAPTER_TITLE, 2)
    assert next(read) == NovelData('Chapter 3', Type.CHAPTER_TITLE, 3)
    with raises(StopIteration):
        next(read)


@mark.data('''
    Volume 1
    \tChapter 1
    Volume 2
    \tChapter 1
''', {'has_volume': True, 'discard_chapters': True})
def test_read_discard(read: Iterator[NovelData]):
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    assert next(read) == NovelData('Volume 2', Type.VOLUME_TITLE, 2)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    with raises(StopIteration):
        next(read)
