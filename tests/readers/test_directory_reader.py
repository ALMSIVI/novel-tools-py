from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from typing import Iterator
from common import NovelData, Type
from readers.directory_reader import DirectoryReader


@fixture
def read(mocker: MockerFixture, request: FixtureRequest):
    args, dir_list, is_dir, isfile = request.node.get_closest_marker('args').args
    mocker.patch('os.listdir', return_value=dir_list)
    mocker.patch('os.path.isdir', side_effect=is_dir)
    mocker.patch('os.path.isfile', return_value=isfile)
    return DirectoryReader(args | {'in_dir': '.'}).read()


@mark.args({'read_contents': False, 'discard_chapters': False}, ['Volume 1', 'Volume 2'], [True, True], False)
def test_no_discard(read: Iterator[NovelData], mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt', 'Chapter 2.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source='Volume 1')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\n'))
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source='Chapter 1.txt', raw='Chapter 1',
                                   line_num=1)

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 2\n'))
    assert next(read) == NovelData('Chapter 2', Type.CHAPTER_TITLE, 2, source='Chapter 2.txt', raw='Chapter 2',
                                   line_num=1)

    mocker.patch('os.listdir', return_value=['Chapter 3.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    assert next(read) == NovelData('Volume 2', Type.VOLUME_TITLE, 2, source='Volume 2')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 3\n'))
    assert next(read) == NovelData('Chapter 3', Type.CHAPTER_TITLE, 3, source='Chapter 3.txt', raw='Chapter 3',
                                   line_num=1)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': False, 'discard_chapters': True}, ['Volume 1', 'Volume 2'], [True, True], False)
def test_discard(read: Iterator[NovelData], mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt', 'Chapter 2.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source='Volume 1')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\n'))
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source='Chapter 1.txt', raw='Chapter 1',
                                   line_num=1)

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 2\n'))
    assert next(read) == NovelData('Chapter 2', Type.CHAPTER_TITLE, 2, source='Chapter 2.txt', raw='Chapter 2',
                                   line_num=1)

    mocker.patch('os.listdir', return_value=['Chapter 1.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    assert next(read) == NovelData('Volume 2', Type.VOLUME_TITLE, 2, source='Volume 2')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\n'))
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source='Chapter 1.txt', raw='Chapter 1',
                                   line_num=1)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': True, 'discard_chapters': False}, ['Volume 1'], [True], False)
def test_contents(read: Iterator[NovelData], mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt'])
    mocker.patch('os.path.isfile', return_value=False)
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source='Volume 1')

    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\nLorem Ipsum'))
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source='Chapter 1.txt', raw='Chapter 1',
                                   line_num=1)
    assert next(read) == NovelData('Lorem Ipsum', Type.CHAPTER_CONTENT, source='Chapter 1.txt', raw='Lorem Ipsum',
                                   line_num=2)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': True, 'discard_chapters': False}, ['Volume 1', '_intro.txt'], [False, True], True)
def test_intro(read: Iterator[NovelData], mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open(read_data='Book Intro'))
    assert next(read) == NovelData('Book Intro', Type.BOOK_INTRO, source='_intro.txt', raw='Book Intro', line_num=1)

    mocker.patch('os.listdir', return_value=['Chapter 1.txt', '_intro.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source='Volume 1')

    mocker.patch('builtins.open', mocker.mock_open(read_data='Volume Intro'))
    assert next(read) == NovelData('Volume Intro', Type.VOLUME_INTRO, source='_intro.txt', raw='Volume Intro',
                                   line_num=1)

    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1'))
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source='Chapter 1.txt', raw='Chapter 1',
                                   line_num=1)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': False, 'discard_chapters': False, 'default_volume': 'Default'}, ['Default'], [True], False)
def test_default_volume(read: Iterator[NovelData], mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt'])
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\nLorem Ipsum'))
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source='Chapter 1.txt', raw='Chapter 1',
                                   line_num=1)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': True, 'discard_chapters': False, 'merge_newlines': True}, ['Volume 1'], [True], False)
def test_merge_newlines(read: Iterator[NovelData], mocker: MockerFixture):
    mocker.patch('os.listdir', return_value=['Chapter 1.txt'])
    mocker.patch('os.path.isfile', return_value=False)
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source='Volume 1')

    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='Chapter 1\n\nLorem Ipsum\n\n\nDolor Sit Amet'))
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source='Chapter 1.txt', raw='Chapter 1',
                                   line_num=1)
    assert next(read) == NovelData('Lorem Ipsum', Type.CHAPTER_CONTENT, source='Chapter 1.txt', raw='Lorem Ipsum',
                                   line_num=3)
    assert next(read) == NovelData('', Type.CHAPTER_CONTENT, source='Chapter 1.txt', raw='',
                                   line_num=5)
    assert next(read) == NovelData('Dolor Sit Amet', Type.CHAPTER_CONTENT, source='Chapter 1.txt', raw='Dolor Sit Amet',
                                   line_num=6)

    with raises(StopIteration):
        next(read)
