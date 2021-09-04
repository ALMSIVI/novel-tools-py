from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from readers.composite_directory_reader import CompositeDirectoryReader
from textwrap import dedent


def format_structure(structure: str) -> str:
    return dedent(structure).strip()


@fixture
def composite_reader(mocker: MockerFixture, request: FixtureRequest):
    args, texts, is_file = request.node.get_closest_marker('args').args
    structure = format_structure(texts)
    mocker.patch('os.path.isfile', return_value=is_file)
    mocker.patch('builtins.open', mocker.mock_open(read_data=structure))

    reader = CompositeDirectoryReader(args | {'in_dir': '.'})
    yield reader
    reader.cleanup()


@mark.args({'structure': 'csv'}, '''
    type,content,index,formatted
    volume_title,Test Volume,1,Test Volume One
    chapter_title,Test Chapter,1,Test Chapter One
''', False)
def test_csv(composite_reader: CompositeDirectoryReader, mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Test Chapter One.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = composite_reader.read()
    assert data == NovelData('Test Volume', Type.VOLUME_TITLE, 1, formatted='Test Volume One')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Test Chapter\nLorem Ipsum'))
    data = composite_reader.read()
    assert data == NovelData('Test Chapter', Type.CHAPTER_TITLE, 1, formatted='Test Chapter One')

    data = composite_reader.read()
    assert data == NovelData('Lorem Ipsum', Type.CHAPTER_CONTENT, None)

    data = composite_reader.read()
    assert data is None


@mark.args({'structure': 'toc', 'has_volume': True, 'discard_chapters': False}, '''
    Test Volume One
    \tTest Chapter One
''', False)
def test_toc(composite_reader: CompositeDirectoryReader, mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Test Chapter One.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = composite_reader.read()
    assert data == NovelData('Test Volume One', Type.VOLUME_TITLE, 1)

    mocker.patch('builtins.open', mocker.mock_open(read_data='Test Chapter\nLorem Ipsum'))
    data = composite_reader.read()
    assert data == NovelData('Test Chapter One', Type.CHAPTER_TITLE, 1)

    data = composite_reader.read()
    assert data == NovelData('Lorem Ipsum', Type.CHAPTER_CONTENT, None)

    data = composite_reader.read()
    assert data is None


@mark.args({'structure': 'csv'}, '''
    type,content,index
    volume_title,Test Volume,1
''', True)
def test_intro(composite_reader: CompositeDirectoryReader, mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open(read_data='Book Intro'))
    data = composite_reader.read()
    assert data == NovelData('Book Intro', Type.BOOK_INTRO, None)

    mocker.patch('os.listdir', return_value=['_intro.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='Volume Intro'))
    data = composite_reader.read()
    assert data == NovelData('Test Volume', Type.VOLUME_TITLE, 1)

    data = composite_reader.read()
    assert data == NovelData('Volume Intro', Type.VOLUME_INTRO, None)

    data = composite_reader.read()
    assert data is None
