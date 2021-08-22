from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import Type
from readers.composite_directory_reader import CompositeDirectoryReader
from tests.helpers.utils import assert_data, format_structure


@fixture
def composite_reader(mocker: MockerFixture, request: FixtureRequest):
    args, texts, is_file = request.node.get_closest_marker('args').args
    if args.get('metadata', False):
        structure, metadata = texts
        mocker.patch('json.load', return_value=metadata)
    else:
        structure = texts

    structure = format_structure(structure)
    mocker.patch('os.path.isfile', return_value=is_file)
    mocker.patch('builtins.open', mocker.mock_open(read_data=structure))

    reader = CompositeDirectoryReader(args | {'in_dir': '.'})
    yield reader
    reader.cleanup()


@mark.args({'structure': 'csv'}, '''
    type,content,index,raw
    volume_title,Test Volume,1,Test Volume One
    chapter_title,Test Chapter,1,Test Chapter One
''', False)
def test_csv(composite_reader: CompositeDirectoryReader, mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Test Chapter One.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = composite_reader.read()
    assert_data(data, 'Test Volume', Type.VOLUME_TITLE, 1, raw='Test Volume One')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Test Chapter\nLorem Ipsum'))
    data = composite_reader.read()
    assert_data(data, 'Test Chapter', Type.CHAPTER_TITLE, 1, raw='Test Chapter One')

    data = composite_reader.read()
    assert_data(data, 'Lorem Ipsum', Type.CHAPTER_CONTENT, None)

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
    assert_data(data, 'Test Volume One', Type.VOLUME_TITLE, 1)

    mocker.patch('builtins.open', mocker.mock_open(read_data='Test Chapter\nLorem Ipsum'))
    data = composite_reader.read()
    assert_data(data, 'Test Chapter One', Type.CHAPTER_TITLE, 1)

    data = composite_reader.read()
    assert_data(data, 'Lorem Ipsum', Type.CHAPTER_CONTENT, None)

    data = composite_reader.read()
    assert data is None


@mark.args({'structure': 'csv', 'metadata': True}, ('''
    type,content,index
    volume_title,Test Volume,1
''', {'title': 'Title'}), False)
def test_metadata(composite_reader: CompositeDirectoryReader, mocker: MockerFixture):
    data = composite_reader.read()
    assert_data(data, 'Title', Type.BOOK_TITLE, None)

    mocker.patch('os.listdir', return_value=[])
    data = composite_reader.read()
    assert_data(data, 'Test Volume', Type.VOLUME_TITLE, 1)

    data = composite_reader.read()
    assert data is None


@mark.args({'structure': 'csv'}, '''
    type,content,index
    volume_title,Test Volume,1
''', True)
def test_intro(composite_reader: CompositeDirectoryReader, mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open(read_data='Book Intro'))
    data = composite_reader.read()
    assert_data(data, 'Book Intro', Type.BOOK_INTRO, None)

    mocker.patch('os.listdir', return_value=['_intro.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='Volume Intro'))
    data = composite_reader.read()
    assert_data(data, 'Test Volume', Type.VOLUME_TITLE, 1)

    data = composite_reader.read()
    assert_data(data, 'Volume Intro', Type.VOLUME_INTRO, None)

    data = composite_reader.read()
    assert data is None
