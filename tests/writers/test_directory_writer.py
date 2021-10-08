import os
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.directory_writer import DirectoryWriter
from utils import format_text


@fixture
def directory_writer(request: FixtureRequest):
    node = request.node.get_closest_marker('args')
    custom_args = node.args[0] if node else {}
    return DirectoryWriter(custom_args | {'out_dir': '.'})


def test_write(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo().write

    data = NovelData('Title', Type.BOOK_TITLE)
    directory_writer.accept(data)

    data = NovelData('Intro', Type.BOOK_INTRO)
    directory_writer.accept(data)

    data = NovelData('Intro 2', Type.BOOK_INTRO)
    directory_writer.accept(data)

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1 Lorem')
    directory_writer.accept(data)

    data = NovelData('Intro', Type.VOLUME_INTRO)
    directory_writer.accept(data)

    data = NovelData('Intro 2', Type.VOLUME_INTRO)
    directory_writer.accept(data)

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.accept(data)

    data = NovelData('Content', Type.CHAPTER_CONTENT)
    directory_writer.accept(data)

    data = NovelData('Content 2', Type.CHAPTER_CONTENT)
    directory_writer.accept(data)

    directory_writer.write()
    mm.assert_called_with(os.path.join('.', 'Volume 1 Lorem'))
    mo.assert_has_calls([
        mocker.call(os.path.join('.', '_intro.txt'), 'wt'),
        mocker.call(os.path.join('.', 'Volume 1 Lorem', '_intro.txt'), 'wt'),
        mocker.call(os.path.join('.', 'Volume 1 Lorem', 'Chapter 1 Ipsum.txt'), 'wt')
    ], any_order=True)
    handle.assert_has_calls([
        mocker.call(format_text('''
            Intro
            Intro 2
        ''')),
        mocker.call(format_text('''
            Intro
            Intro 2
        ''')),
        mocker.call('Chapter 1 Ipsum\n\n'),
        mocker.call(format_text('''
            Content
            Content 2
        '''))
    ])


def test_filename(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo().write

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem', filename='v_1')
    directory_writer.accept(data)

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum', filename='c_1')
    directory_writer.accept(data)

    directory_writer.write()
    mm.assert_called_with(os.path.join('.', 'v_1'))
    mo.assert_called_with(os.path.join('.', 'v_1', 'c_1.txt'), 'wt')
    handle.assert_any_call('Chapter 1 Ipsum\n\n')


def test_default_volume(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('os.path.isdir', return_value=False)

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.accept(data)

    directory_writer.write()
    mm.assert_called_once_with(os.path.join('.', 'default'))
    mo.assert_called_with(os.path.join('.', 'default', 'Chapter 1 Ipsum.txt'), 'wt')


@mark.args({'default_volume': 'No Volume'})
def test_custom_default_volume(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('os.path.isdir', return_value=False)

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.accept(data)

    directory_writer.write()
    mm.assert_called_once_with(os.path.join('.', 'No Volume'))
    mo.assert_called_with(os.path.join('.', 'No Volume', 'Chapter 1 Ipsum.txt'), 'wt')


@mark.args({'intro_filename': 'introduction.md'})
def test_intro(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())

    data = NovelData('Intro', Type.BOOK_INTRO)
    directory_writer.accept(data)

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1 Lorem')
    directory_writer.accept(data)

    data = NovelData('Intro', Type.VOLUME_INTRO)
    directory_writer.accept(data)

    directory_writer.write()
    mo.assert_has_calls([
        mocker.call(os.path.join('.', 'introduction.md'), 'wt'),
        mocker.call(os.path.join('.', 'Volume 1 Lorem', 'introduction.md'), 'wt')
    ], any_order=True)


@mark.args({'debug': True})
def test_debug(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('os.mkdir')
    mocker.patch('builtins.open', mocker.mock_open())
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Title', error='Error')
    directory_writer.accept(data)

    directory_writer.write()
    mp.assert_called_once_with('Error')
