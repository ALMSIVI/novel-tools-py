from pathlib import Path
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from novel_tools.common import NovelData, Type
from novel_tools.writers.text_writer import TextWriter


def assert_text(text_path: Path, expected: str):
    assert text_path.is_file()
    with text_path.open('rt') as f:
        assert f.read() == expected


@fixture
def text_writer(writer_directory: Path, request: FixtureRequest):
    args = request.node.get_closest_marker('args').args[0]
    return TextWriter(args | {'out_dir': writer_directory})


@mark.args({
    'use_title': False,
})
def test_write(text_writer: TextWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    text_writer.accept(data)
    data = NovelData('Book Intro', Type.BOOK_INTRO)
    text_writer.accept(data)
    data = NovelData('Volume', Type.VOLUME_TITLE)
    text_writer.accept(data)
    data = NovelData('Volume Intro', Type.VOLUME_INTRO)
    text_writer.accept(data)
    data = NovelData('Title', Type.CHAPTER_TITLE, formatted='Chapter')
    text_writer.accept(data)
    data = NovelData('Chapter Content', Type.CHAPTER_CONTENT)
    text_writer.accept(data)
    data = NovelData('', Type.CHAPTER_CONTENT)
    text_writer.accept(data)

    text_writer.write()
    text_path = writer_directory / 'text.txt'
    assert_text(text_path, 'Title\n\nBook Intro\n\nVolume\n\nVolume Intro\n\nChapter\n\nChapter Content')


@mark.args({
    'use_title': False,
    'levels': {'volume_title': 1, 'chapter_title': 2}
})
def test_levels(text_writer: TextWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    text_writer.accept(data)
    data = NovelData('Volume', Type.VOLUME_TITLE)
    text_writer.accept(data)
    data = NovelData('Title', Type.CHAPTER_TITLE, formatted='Chapter')
    text_writer.accept(data)

    text_writer.write()
    text_path = writer_directory / 'text.txt'
    assert_text(text_path, 'Title\n\nVolume\n\nChapter\n\n')


@mark.args({
    'use_title': True,
})
def test_use_title(text_writer: TextWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    text_writer.accept(data)

    text_writer.write()
    text_path = writer_directory / 'Title.txt'
    assert_text(text_path, 'Title\n\n')


@mark.args({
    'use_title': False,
    'text_filename': 'book.txt',
})
def test_custom_title(text_writer: TextWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    text_writer.accept(data)

    text_writer.write()
    text_path = writer_directory / 'book.txt'
    assert_text(text_path, 'Title\n\n')


@mark.args({
    'use_title': False,
    'debug': True
})
def test_debug(text_writer: TextWriter, writer_directory: Path, mocker: MockerFixture):
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.BOOK_TITLE, error='Error')
    text_writer.accept(data)

    text_writer.write()
    mp.assert_called_once_with('Error')
