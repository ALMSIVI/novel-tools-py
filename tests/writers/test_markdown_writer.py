from pathlib import Path
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from novel_tools.framework import NovelData, Type
from novel_tools.writers.markdown_writer import MarkdownWriter


def assert_md(md_path: Path, expected: str):
    assert md_path.is_file()
    with md_path.open('rt') as f:
        assert f.read() == expected


@fixture
def markdown_writer(writer_directory: Path, request: FixtureRequest):
    args = request.node.get_closest_marker('args').args[0]
    return MarkdownWriter(args | {'out_dir': writer_directory})


@mark.args({
    'use_title': False,
})
def test_write(markdown_writer: MarkdownWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.accept(data)
    data = NovelData('Book Intro', Type.BOOK_INTRO)
    markdown_writer.accept(data)
    data = NovelData('Volume', Type.VOLUME_TITLE)
    markdown_writer.accept(data)
    data = NovelData('Volume Intro', Type.VOLUME_INTRO)
    markdown_writer.accept(data)
    data = NovelData('Title', Type.CHAPTER_TITLE, formatted='Chapter')
    markdown_writer.accept(data)
    data = NovelData('Chapter Content', Type.CHAPTER_CONTENT)
    markdown_writer.accept(data)
    data = NovelData('', Type.CHAPTER_CONTENT)
    markdown_writer.accept(data)

    markdown_writer.write()
    md_path = writer_directory / 'text.md'
    assert_md(md_path, '# Title\n\nBook Intro\n\n## Volume\n\nVolume Intro\n\n### Chapter\n\nChapter Content')


@mark.args({
    'use_title': False,
    'levels': {'volume_title': 1, 'chapter_title': 2}
})
def test_levels(markdown_writer: MarkdownWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.accept(data)
    data = NovelData('Volume', Type.VOLUME_TITLE)
    markdown_writer.accept(data)
    data = NovelData('Title', Type.CHAPTER_TITLE, formatted='Chapter')
    markdown_writer.accept(data)

    markdown_writer.write()
    md_path = writer_directory / 'text.md'
    assert_md(md_path, 'Title\n\n# Volume\n\n## Chapter\n\n')


@mark.args({
    'use_title': False,
    'write_newline': True
})
def test_newline(markdown_writer: MarkdownWriter, writer_directory: Path):
    data = NovelData('Title', Type.CHAPTER_TITLE)
    markdown_writer.accept(data)

    data = NovelData('Test', Type.CHAPTER_CONTENT)
    markdown_writer.accept(data)

    data = NovelData('Test 2', Type.CHAPTER_CONTENT)
    markdown_writer.accept(data)

    markdown_writer.write()
    md_path = writer_directory / 'text.md'
    assert_md(md_path, '### Title\n\nTest\n\nTest 2')


@mark.args({
    'use_title': True,
})
def test_use_title(markdown_writer: MarkdownWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.accept(data)

    markdown_writer.write()
    md_path = writer_directory / 'Title.md'
    assert_md(md_path, '# Title\n\n')


@mark.args({
    'use_title': False,
    'md_filename': 'markdown.md',
})
def test_custom_title(markdown_writer: MarkdownWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.accept(data)

    markdown_writer.write()
    md_path = writer_directory / 'markdown.md'
    assert_md(md_path, '# Title\n\n')


@mark.args({
    'use_title': False,
    'debug': True
})
def test_debug(markdown_writer: MarkdownWriter, writer_directory: Path, mocker: MockerFixture):
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.BOOK_TITLE, error='Error')
    markdown_writer.accept(data)

    markdown_writer.write()
    mp.assert_called_once_with('Error')
