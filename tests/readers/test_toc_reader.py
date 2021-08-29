from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import Type
from readers.toc_reader import TocReader
from tests.helpers import assert_data, format_structure


@fixture
def toc_reader(mocker: MockerFixture, request: FixtureRequest):
    toc, args = request.node.get_closest_marker('data').args
    toc = format_structure(toc)
    mocker.patch('builtins.open', mocker.mock_open(read_data=toc))
    reader = TocReader(args | {'in_dir': ''})
    yield reader
    reader.cleanup()


@mark.data('''
    Volume 1
    \tChapter 1
    \tChapter 2
    Volume 2
    \tChapter 3
''', {'has_volume': True, 'discard_chapters': False})
def test_read(toc_reader: TocReader):
    data = toc_reader.read()
    assert_data(data, 'Volume 1', Type.VOLUME_TITLE, 1)

    data = toc_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1)

    data = toc_reader.read()
    assert_data(data, 'Chapter 2', Type.CHAPTER_TITLE, 2)

    data = toc_reader.read()
    assert_data(data, 'Volume 2', Type.VOLUME_TITLE, 2)

    data = toc_reader.read()
    assert_data(data, 'Chapter 3', Type.CHAPTER_TITLE, 3)


@mark.data('''
    Volume 1\t1
    \tChapter 1\t2
    Volume 2\t25
    \tChapter 2\t27
''', {'has_volume': True, 'discard_chapters': False})
def test_read_line_num(toc_reader: TocReader):
    data = toc_reader.read()
    assert_data(data, 'Volume 1', Type.VOLUME_TITLE, 1, line_num=1)

    data = toc_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1, line_num=2)

    data = toc_reader.read()
    assert_data(data, 'Volume 2', Type.VOLUME_TITLE, 2, line_num=25)

    data = toc_reader.read()
    assert_data(data, 'Chapter 2', Type.CHAPTER_TITLE, 2, line_num=27)


@mark.data('''
    Chapter 1
    Chapter 2
    Chapter 3
''', {'has_volume': False, 'discard_chapters': False})
def test_read_no_volume(toc_reader: TocReader):
    data = toc_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1)

    data = toc_reader.read()
    assert_data(data, 'Chapter 2', Type.CHAPTER_TITLE, 2)

    data = toc_reader.read()
    assert_data(data, 'Chapter 3', Type.CHAPTER_TITLE, 3)


@mark.data('''
    Volume 1
    \tChapter 1
    Volume 2
    \tChapter 1
''', {'has_volume': True, 'discard_chapters': True})
def test_read_discard(toc_reader: TocReader):
    data = toc_reader.read()
    assert_data(data, 'Volume 1', Type.VOLUME_TITLE, 1)

    data = toc_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1)

    data = toc_reader.read()
    assert_data(data, 'Volume 2', Type.VOLUME_TITLE, 2)

    data = toc_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1)
