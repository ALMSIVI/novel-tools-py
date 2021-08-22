from typing import Optional
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from readers.directory_reader import DirectoryReader


def assert_data(data: NovelData, content: str, data_type: Type, index: Optional[int], **kwargs):
    assert data.content == content
    assert data.data_type == data_type
    assert data.index == index
    for key, value in kwargs.items():
        assert data.get(key) == value


@fixture
def directory_reader(mocker: MockerFixture, request: FixtureRequest):
    args, dir_list, is_dir, isfile = request.node.get_closest_marker('args').args
    mocker.patch('os.listdir', return_value=dir_list)
    mocker.patch('os.path.isdir', side_effect=is_dir)
    mocker.patch('os.path.isfile', return_value=isfile)
    reader = DirectoryReader(args | {'in_dir': '.'})
    yield reader
    reader.cleanup()


@mark.args({'read_contents': False, 'discard_chapters': False}, ['Volume 1', 'Volume 2'], [True, True], False)
def test_no_discard(directory_reader: DirectoryReader, mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt', 'Chapter 2.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = directory_reader.read()
    assert_data(data, 'Volume 1', Type.VOLUME_TITLE, 1, filename='Volume 1')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\n'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1, filename='Chapter 1.txt')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 2\n'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 2', Type.CHAPTER_TITLE, 2, filename='Chapter 2.txt')

    mocker.patch('os.listdir', return_value=['Chapter 3.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = directory_reader.read()
    assert_data(data, 'Volume 2', Type.VOLUME_TITLE, 2, filename='Volume 2')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 3\n'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 3', Type.CHAPTER_TITLE, 3, filename='Chapter 3.txt')

    data = directory_reader.read()
    assert data is None


@mark.args({'read_contents': False, 'discard_chapters': True}, ['Volume 1', 'Volume 2'], [True, True], False)
def test_discard(directory_reader: DirectoryReader, mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt', 'Chapter 2.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = directory_reader.read()
    assert_data(data, 'Volume 1', Type.VOLUME_TITLE, 1, filename='Volume 1')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\n'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1, filename='Chapter 1.txt')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 2\n'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 2', Type.CHAPTER_TITLE, 2, filename='Chapter 2.txt')

    mocker.patch('os.listdir', return_value=['Chapter 1.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = directory_reader.read()
    assert_data(data, 'Volume 2', Type.VOLUME_TITLE, 2, filename='Volume 2')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\n'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1, filename='Chapter 1.txt')

    data = directory_reader.read()
    assert data is None


@mark.args({'read_contents': True, 'discard_chapters': False}, ['Volume 1'], [True], False)
def test_contents(directory_reader: DirectoryReader, mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt', 'Chapter 2.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = directory_reader.read()
    assert_data(data, 'Volume 1', Type.VOLUME_TITLE, 1, filename='Volume 1')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\nLorem Ipsum'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1, filename='Chapter 1.txt')
    data = directory_reader.read()
    assert_data(data, 'Lorem Ipsum', Type.CHAPTER_CONTENT, None)

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 2\n'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 2', Type.CHAPTER_TITLE, 2, filename='Chapter 2.txt')
    data = directory_reader.read()
    assert_data(data, '', Type.CHAPTER_CONTENT, None)

    data = directory_reader.read()
    assert data is None


@mark.args({'read_contents': True, 'discard_chapters': False}, ['Volume 1', '_intro.txt'], [True, False], True)
def test_intro(directory_reader: DirectoryReader, mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open(read_data='Book Intro'))
    data = directory_reader.read()
    assert_data(data, 'Book Intro', Type.BOOK_INTRO, None)

    mocker.patch('os.listdir', return_value=['Chapter 1.txt', '_intro.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    data = directory_reader.read()
    assert_data(data, 'Volume 1', Type.VOLUME_TITLE, 1, filename='Volume 1')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Volume Intro'))
    data = directory_reader.read()
    assert_data(data, 'Volume Intro', Type.VOLUME_INTRO, None)

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\nLorem Ipsum'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1, filename='Chapter 1.txt')
    data = directory_reader.read()
    assert_data(data, 'Lorem Ipsum', Type.CHAPTER_CONTENT, None)

    data = directory_reader.read()
    assert data is None


@mark.args({'read_contents': False, 'discard_chapters': False, 'default_volume': 'Default'}, ['Default'], [True], False)
def test_default_volume(directory_reader: DirectoryReader, mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\nLorem Ipsum'))
    data = directory_reader.read()
    assert_data(data, 'Chapter 1', Type.CHAPTER_TITLE, 1, filename='Chapter 1.txt')

    data = directory_reader.read()
    assert data is None
