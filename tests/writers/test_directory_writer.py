from pathlib import Path
from typing import Union
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from novel_tools.framework import NovelData, Type
from novel_tools.writers.directory_writer import DirectoryWriter


def assert_directory(writer_directory: Path, expected: dict[Union[str, dict[str, str]]]):
    volumes = list(writer_directory.iterdir())
    assert len(volumes) == len(expected)
    for path in volumes:
        name = path.name
        assert name in expected
        if path.is_dir():  # Volume directory
            chapters = list(path.iterdir())
            chapter_dict = expected[name]
            assert len(chapters) == len(chapter_dict)
            for chapter_path in chapters:
                chapter_name = chapter_path.name
                assert chapter_name in chapter_dict
                assert chapter_path.is_file()
                with chapter_path.open('rt') as f:
                    assert f.read() == chapter_dict[chapter_name]
        else:  # Intro file
            with path.open('rt') as f:
                assert f.read() == expected[name]


@fixture
def directory_writer(writer_directory: Path, request: FixtureRequest):
    node = request.node.get_closest_marker('args')
    custom_args = node.args[0] if node else {}
    return DirectoryWriter(custom_args | {'out_dir': writer_directory})


def test_write(directory_writer: DirectoryWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    directory_writer.accept(data)
    data = NovelData('Intro', Type.BOOK_INTRO)
    directory_writer.accept(data)
    data = NovelData('Intro 2', Type.BOOK_INTRO)
    directory_writer.accept(data)
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1 Lorem')
    directory_writer.accept(data)
    data = NovelData('Intro 3', Type.VOLUME_INTRO)
    directory_writer.accept(data)
    data = NovelData('Intro 4', Type.VOLUME_INTRO)
    directory_writer.accept(data)
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.accept(data)
    data = NovelData('Content', Type.CHAPTER_CONTENT)
    directory_writer.accept(data)
    data = NovelData('Content 2', Type.CHAPTER_CONTENT)
    directory_writer.accept(data)
    data = NovelData('Dolor', Type.CHAPTER_TITLE, 2, formatted='Chapter 2 Dolor')
    directory_writer.accept(data)
    data = NovelData('Content 3', Type.CHAPTER_CONTENT)
    directory_writer.accept(data)
    data = NovelData('Sit', Type.VOLUME_TITLE, 2, formatted='Volume 2 Sit')
    directory_writer.accept(data)
    data = NovelData('Amet', Type.CHAPTER_TITLE, 3, formatted='Chapter 3 Amet')
    directory_writer.accept(data)
    data = NovelData('Content 4', Type.CHAPTER_CONTENT)
    directory_writer.accept(data)

    directory_writer.write()
    assert_directory(writer_directory, {
        '_intro.txt': 'Intro\nIntro 2',
        'Volume 1 Lorem': {
            '_intro.txt': 'Intro 3\nIntro 4',
            'Chapter 1 Ipsum.txt': 'Chapter 1 Ipsum\n\nContent\nContent 2',
            'Chapter 2 Dolor.txt': 'Chapter 2 Dolor\n\nContent 3'
        },
        'Volume 2 Sit': {
            'Chapter 3 Amet.txt': 'Chapter 3 Amet\n\nContent 4'
        }
    })


def test_filename(directory_writer: DirectoryWriter, writer_directory: Path):
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem', filename='v_1')
    directory_writer.accept(data)
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum', filename='c_1')
    directory_writer.accept(data)

    directory_writer.write()
    assert_directory(writer_directory, {
        'v_1': {
            'c_1.txt': 'Chapter 1 Ipsum\n\n'
        }
    })


def test_default_volume(directory_writer: DirectoryWriter, writer_directory: Path):
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.accept(data)

    directory_writer.write()
    assert_directory(writer_directory, {
        'default': {
            'Chapter 1 Ipsum.txt': 'Chapter 1 Ipsum\n\n'
        }
    })


@mark.args({'default_volume': 'No Volume'})
def test_custom_default_volume(directory_writer: DirectoryWriter, writer_directory: Path):
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Ipsum')
    directory_writer.accept(data)

    directory_writer.write()
    assert_directory(writer_directory, {
        'No Volume': {
            'Chapter 1 Ipsum.txt': 'Chapter 1 Ipsum\n\n'
        }
    })


@mark.args({'intro_filename': 'introduction.md'})
def test_intro(directory_writer: DirectoryWriter, writer_directory: Path):
    data = NovelData('Intro', Type.BOOK_INTRO)
    directory_writer.accept(data)
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1 Lorem')
    directory_writer.accept(data)
    data = NovelData('Intro 2', Type.VOLUME_INTRO)
    directory_writer.accept(data)

    directory_writer.write()
    assert_directory(writer_directory, {
        'introduction.md': 'Intro',
        'Volume 1 Lorem': {
            'introduction.md': 'Intro 2'
        }
    })


@mark.args({'debug': True})
def test_debug(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mp = mocker.patch('builtins.print')
    data = NovelData('Title', Type.CHAPTER_TITLE, 1, formatted='Chapter 1 Title', error='Error')
    directory_writer.accept(data)

    directory_writer.write()
    mp.assert_called_once_with('Error')
