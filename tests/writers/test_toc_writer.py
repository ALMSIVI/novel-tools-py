from pathlib import Path
from pytest import fixture, FixtureRequest, mark
from common import NovelData, Type
from writers.toc_writer import TocWriter


def assert_toc(toc_path: Path, expected: str):
    assert toc_path.is_file()
    with toc_path.open('rt') as f:
        assert f.read() == expected


@fixture
def toc_writer(writer_directory: Path, request: FixtureRequest):
    node = request.node.get_closest_marker('args')
    custom_args = node.args[0] if node else {}
    return TocWriter({'out_dir': writer_directory} | custom_args)


def test_write(toc_writer: TocWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    toc_writer.accept(data)
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem')
    toc_writer.accept(data)
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 2, formatted='Chapter 2. Ipsum')
    toc_writer.accept(data)

    toc_writer.write()
    toc_path = writer_directory / 'toc.txt'
    assert_toc(toc_path, 'Volume 1. Lorem\n\tChapter 2. Ipsum\n')


@mark.args({'toc_filename': 'custom.txt'})
def test_custom_filename(toc_writer: TocWriter, writer_directory: Path):
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem')
    toc_writer.accept(data)
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 2, formatted='Chapter 2. Ipsum')
    toc_writer.accept(data)

    toc_writer.write()
    toc_path = writer_directory / 'custom.txt'
    assert_toc(toc_path, 'Volume 1. Lorem\n\tChapter 2. Ipsum\n')


def test_no_volume(toc_writer: TocWriter, writer_directory: Path):
    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem')
    toc_writer.accept(data)

    toc_writer.write()
    toc_path = writer_directory / 'toc.txt'
    assert_toc(toc_path, 'Chapter 1. Lorem\n')


def test_line_num(toc_writer: TocWriter, writer_directory: Path):
    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem', line_num=10)
    toc_writer.accept(data)

    toc_writer.write()
    toc_path = writer_directory / 'toc.txt'
    assert_toc(toc_path, 'Chapter 1. Lorem\t10\n')


@mark.args({'write_line_num': False})
def test_no_line_num(toc_writer: TocWriter, writer_directory: Path):
    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem', line_num=10)
    toc_writer.accept(data)

    toc_writer.write()
    toc_path = writer_directory / 'toc.txt'
    assert_toc(toc_path, 'Chapter 1. Lorem\n')


@mark.args({'debug': True})
def test_debug(toc_writer: TocWriter, writer_directory: Path):
    data = NovelData('Lorem', Type.CHAPTER_TITLE, 1, formatted='Chapter 1. Lorem', error='Error message')
    toc_writer.accept(data)

    toc_writer.write()
    toc_path = writer_directory / 'toc.txt'
    assert_toc(toc_path, 'Chapter 1. Lorem\tError message\n')
