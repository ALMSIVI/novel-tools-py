import os
from pytest import fixture
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.toc_writer import TocWriter


@fixture
def toc_writer():
    return TocWriter({'out_dir': '.'})


@fixture
def debug_writer():
    return TocWriter({'out_dir': '.', 'debug': True})


def test_write(toc_writer: TocWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Title', Type.BOOK_TITLE)
    toc_writer.accept(data)
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem')
    toc_writer.accept(data)
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 2, formatted='Chapter 2. Ipsum')
    toc_writer.accept(data)

    toc_writer.write()
    m.assert_called_with(os.path.join('.', 'toc.txt'), 'wt')
    handle.assert_has_calls([mocker.call('Volume 1. Lorem\n'), mocker.call('\tChapter 2. Ipsum\n')])


def test_no_volume(toc_writer: TocWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem')
    toc_writer.accept(data)

    toc_writer.write()
    handle.assert_called_with('Chapter 1. Lorem\n')


def test_line_num(toc_writer: TocWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem', line_num=10)
    toc_writer.accept(data)

    toc_writer.write()
    handle.assert_called_with('Chapter 1. Lorem\t10\n')


def test_debug(debug_writer: TocWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem', error='Error message')
    debug_writer.accept(data)

    debug_writer.write()
    handle.assert_called_with('Chapter 1. Lorem\tError message\n')
