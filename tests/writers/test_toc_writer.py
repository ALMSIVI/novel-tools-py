from pytest import fixture
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.toc_writer import TocWriter


@fixture
def toc_writer():
    writer = TocWriter({'out_dir': '.'})
    yield writer
    writer.cleanup()


@fixture
def debug_writer():
    writer = TocWriter({'out_dir': '.', 'debug': True})
    yield writer
    writer.cleanup()


def test_write(toc_writer: TocWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Title', Type.BOOK_TITLE)
    toc_writer.write(data)
    handle.write.assert_not_called()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem')
    toc_writer.write(data)
    handle.write.assert_called_with('Volume 1. Lorem\n')

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 2, formatted='Chapter 2. Ipsum')
    toc_writer.write(data)
    handle.write.assert_called_with('\tChapter 2. Ipsum\n')


def test_no_volume(toc_writer: TocWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem')
    toc_writer.write(data)
    handle.write.assert_called_with('Chapter 1. Lorem\n')


def test_line_num(toc_writer: TocWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem', line_num=10)
    toc_writer.write(data)
    handle.write.assert_called_with('Chapter 1. Lorem\t10\n')


def test_debug(debug_writer: TocWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem', error='Error message')
    debug_writer.write(data)
    handle.write.assert_called_with('Chapter 1. Lorem\tError message\n')
