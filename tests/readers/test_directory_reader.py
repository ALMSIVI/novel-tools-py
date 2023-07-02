from pathlib import Path
from pytest import fixture, FixtureRequest, mark, raises
from typing import Iterator
from novel_tools.framework import NovelData, Type
from novel_tools.readers.directory_reader import DirectoryReader


def transform_list(file_list: list[str], volume: str = '') -> list[Path]:
    return [Path(volume, file) for file in file_list]


@fixture
def test_directory(request: FixtureRequest, reader_directory: Path) -> Path:
    return reader_directory / 'directory_reader' / request.node.name


@fixture
def read(request: FixtureRequest, test_directory: Path):
    args, = request.node.get_closest_marker('args').args
    return DirectoryReader(args | {'in_dir': test_directory}).read()


@mark.args({'read_contents': False, 'discard_chapters': False})
def test_no_discard(read: Iterator[NovelData], test_directory: Path):
    volume_1 = test_directory / 'Volume 1'
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source=volume_1)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source=volume_1 / 'Chapter 1.txt',
                                   raw='Chapter 1', line_num=1)
    assert next(read) == NovelData('Chapter 2', Type.CHAPTER_TITLE, 2, source=volume_1 / 'Chapter 2.txt',
                                   raw='Chapter 2', line_num=1)

    volume_2 = test_directory / 'Volume 2'
    assert next(read) == NovelData('Volume 2', Type.VOLUME_TITLE, 2, source=volume_2)
    assert next(read) == NovelData('Chapter 3', Type.CHAPTER_TITLE, 3, source=volume_2 / 'Chapter 3.txt',
                                   raw='Chapter 3', line_num=1)
    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': False, 'discard_chapters': True})
def test_discard(read: Iterator[NovelData], test_directory: Path):
    volume_1 = test_directory / 'Volume 1'
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source=volume_1)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source=volume_1 / 'Chapter 1.txt',
                                   raw='Chapter 1', line_num=1)
    assert next(read) == NovelData('Chapter 2', Type.CHAPTER_TITLE, 2, source=volume_1 / 'Chapter 2.txt',
                                   raw='Chapter 2', line_num=1)

    volume_2 = test_directory / 'Volume 2'
    assert next(read) == NovelData('Volume 2', Type.VOLUME_TITLE, 2, source=volume_2)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source=volume_2 / 'Chapter 1.txt',
                                   raw='Chapter 1', line_num=1)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': True, 'discard_chapters': False})
def test_contents(read: Iterator[NovelData], test_directory: Path):
    volume_1 = test_directory / 'Volume 1'
    chapter_1 = volume_1 / 'Chapter 1.txt'
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source=volume_1)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source=chapter_1, raw='Chapter 1', line_num=1)
    assert next(read) == NovelData('Lorem Ipsum', Type.CHAPTER_CONTENT, source=chapter_1, raw='Lorem Ipsum', line_num=2)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': True, 'discard_chapters': False})
def test_intro(read: Iterator[NovelData], test_directory: Path):
    assert next(read) == NovelData('Book Intro', Type.BOOK_INTRO, source=test_directory / '_intro.txt',
                                   raw='Book Intro', line_num=1)

    volume_1 = test_directory / 'Volume 1'
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source=volume_1)
    assert next(read) == NovelData('Volume Intro', Type.VOLUME_INTRO, source=volume_1 / '_intro.txt',
                                   raw='Volume Intro', line_num=1)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source=volume_1 / 'Chapter 1.txt',
                                   raw='Chapter 1', line_num=1)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': False, 'discard_chapters': False, 'default_volume': 'Default'})
def test_default_volume(read: Iterator[NovelData], test_directory: Path):
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1,
                                   source=test_directory / 'Default' / 'Chapter 1.txt', raw='Chapter 1', line_num=1)

    with raises(StopIteration):
        next(read)


@mark.args({'read_contents': True, 'discard_chapters': False, 'merge_newlines': True})
def test_merge_newlines(read: Iterator[NovelData], test_directory: Path):
    volume_1 = test_directory / 'Volume 1'
    chapter_1 = volume_1 / 'Chapter 1.txt'
    assert next(read) == NovelData('Volume 1', Type.VOLUME_TITLE, 1, source=volume_1)
    assert next(read) == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, source=chapter_1, raw='Chapter 1',
                                   line_num=1)
    assert next(read) == NovelData('Lorem Ipsum', Type.CHAPTER_CONTENT, source=chapter_1, raw='Lorem Ipsum',
                                   line_num=3)
    assert next(read) == NovelData('', Type.CHAPTER_CONTENT, source=chapter_1, raw='',
                                   line_num=5)
    assert next(read) == NovelData('Dolor Sit Amet', Type.CHAPTER_CONTENT, source=chapter_1,
                                   raw='Dolor Sit Amet', line_num=6)

    with raises(StopIteration):
        next(read)
