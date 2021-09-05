import os
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.directory_writer import DirectoryWriter


@fixture
def directory_writer(request: FixtureRequest):
    args = request.node.get_closest_marker('args').args[0]
    writer = DirectoryWriter(args | {'out_dir': '.'})
    yield writer
    writer.cleanup()


@mark.args({})
def test_write(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Title', Type.BOOK_TITLE)
    directory_writer.write(data)
    mo.assert_called_with(os.path.join('.', '_intro.txt'), 'wt')
    handle.write.assert_called_with('Title\n')

    data = NovelData('Intro', Type.BOOK_INTRO)
    directory_writer.write(data)
    handle.write.assert_called_with('Intro\n')

    data = NovelData('Intro 2', Type.BOOK_INTRO)
    directory_writer.write(data)
    handle.write.assert_called_with('Intro 2\n')

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1 Lorem')
    directory_writer.write(data)
    mm.assert_called_with(os.path.join('.', 'Volume 1 Lorem'))

    data = NovelData('Intro', Type.VOLUME_INTRO)
    directory_writer.write(data)
    handle.close.assert_called_once()
    mo.assert_called_with(os.path.join('.', 'Volume 1 Lorem', '_intro.txt'), 'wt')
    handle.write.assert_called_with('Intro\n')

    data = NovelData('Intro 2', Type.VOLUME_INTRO)
    directory_writer.write(data)
    handle.write.assert_called_with('Intro 2\n')

    handle.reset_mock()
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.write(data)
    handle.close.assert_called_once()
    mo.assert_called_with(os.path.join('.', 'Volume 1 Lorem', 'Chapter 1 Ipsum.txt'), 'wt')
    handle.write.assert_called_with('Chapter 1 Ipsum\n')

    data = NovelData('Content', Type.CHAPTER_CONTENT)
    directory_writer.write(data)
    handle.write.assert_called_with('Content\n')

    data = NovelData('Content 2', Type.CHAPTER_CONTENT)
    directory_writer.write(data)
    handle.write.assert_called_with('Content 2\n')


@mark.args({})
def test_filename(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem', filename='v_1')
    directory_writer.write(data)
    mm.assert_called_with(os.path.join('.', 'v_1'))

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum', filename='c_1')
    directory_writer.write(data)
    mo.assert_called_with(os.path.join('.', 'v_1', 'c_1.txt'), 'wt')
    handle.write.assert_called_with('Chapter 1 Ipsum\n')


@mark.args({})
def test_default_volume(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('os.path.isdir', return_value=False)

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.write(data)
    mm.assert_called_once_with(os.path.join('.', 'default'))
    mo.assert_called_with(os.path.join('.', 'default', 'Chapter 1 Ipsum.txt'), 'wt')


@mark.args({'default_volume': 'No Volume'})
def test_custom_default_volume(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('os.path.isdir', return_value=False)

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.write(data)
    mm.assert_called_once_with(os.path.join('.', 'No Volume'))
    mo.assert_called_with(os.path.join('.', 'No Volume', 'Chapter 1 Ipsum.txt'), 'wt')


@mark.args({'intro_filename': 'introduction.md'})
def test_intro(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Title', Type.BOOK_TITLE)
    directory_writer.write(data)
    mo.assert_called_with(os.path.join('.', 'introduction.md'), 'wt')

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1 Lorem')
    directory_writer.write(data)

    data = NovelData('Intro', Type.VOLUME_INTRO)
    directory_writer.write(data)
    handle.close.assert_called_once()
    mo.assert_called_with(os.path.join('.', 'Volume 1 Lorem', 'introduction.md'), 'wt')


@mark.args({'debug': True})
def test_debug(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('os.mkdir')
    mocker.patch('builtins.open', mocker.mock_open())
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Title', error='Error')
    directory_writer.write(data)
    mp.assert_called_once_with('Error\t- Adjusted to Chapter 1 Title')


@mark.args({'write_newline': True})
def test_newline(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Title', Type.BOOK_TITLE)
    directory_writer.write(data)
    handle.write.assert_called_with('\n')
