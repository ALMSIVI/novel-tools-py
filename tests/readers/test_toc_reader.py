from textwrap import dedent
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import Type
from readers.toc_reader import TocReader


def format_toc(toc: str):
    return dedent(toc).strip()


def create(args):
    return TocReader(args | {'in_dir': ''})


@fixture
def toc_reader(mocker: MockerFixture, request: FixtureRequest):
    toc, args = request.node.get_closest_marker('data').args
    toc = format_toc(toc)
    mocker.patch('builtins.open', mocker.mock_open(read_data=toc))
    reader = create(args)
    yield reader
    reader.cleanup()


@mark.data('''
    Volume 1
    \tChapter 1
    \tChapter 2
    Volume 2
    \tChapter 3
''', {'has_volume': True})
def test_read(toc_reader: TocReader):
    data = toc_reader.read()
    assert data.content == 'Volume 1'
    assert data.data_type == Type.VOLUME_TITLE
    assert data.index == 1

    data = toc_reader.read()
    assert data.content == 'Chapter 1'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 1

    data = toc_reader.read()
    assert data.content == 'Chapter 2'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 2

    data = toc_reader.read()
    assert data.content == 'Volume 2'
    assert data.data_type == Type.VOLUME_TITLE
    assert data.index == 2

    data = toc_reader.read()
    assert data.content == 'Chapter 3'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 3


@mark.data('''
    Volume 1\t1
    \tChapter 1\t2
    \tChapter 2\t10
    Volume 2\t25
    \tChapter 3\t27
''', {'has_volume': True})
def test_read_line_num(toc_reader: TocReader):
    data = toc_reader.read()
    assert data.content == 'Volume 1'
    assert data.data_type == Type.VOLUME_TITLE
    assert data.index == 1
    assert data.get('line_num') == 1

    data = toc_reader.read()
    assert data.content == 'Chapter 1'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 1
    assert data.get('line_num') == 2

    data = toc_reader.read()
    assert data.content == 'Chapter 2'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 2
    assert data.get('line_num') == 10

    data = toc_reader.read()
    assert data.content == 'Volume 2'
    assert data.data_type == Type.VOLUME_TITLE
    assert data.index == 2
    assert data.get('line_num') == 25

    data = toc_reader.read()
    assert data.content == 'Chapter 3'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 3
    assert data.get('line_num') == 27


@mark.data('''
    Chapter 1
    Chapter 2
    Chapter 3
''', {'has_volume': False})
def test_read_no_volume(toc_reader: TocReader):
    data = toc_reader.read()
    assert data.content == 'Chapter 1'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 1

    data = toc_reader.read()
    assert data.content == 'Chapter 2'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 2

    data = toc_reader.read()
    assert data.content == 'Chapter 3'
    assert data.data_type == Type.CHAPTER_TITLE
    assert data.index == 3
