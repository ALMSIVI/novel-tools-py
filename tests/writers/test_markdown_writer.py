import os
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.markdown_writer import MarkdownWriter


@fixture
def markdown_writer(request: FixtureRequest):
    args = request.node.get_closest_marker('args').args[0]
    writer = MarkdownWriter(args | {'out_dir': '.'})
    yield writer
    writer.cleanup()


@mark.args({
    'use_title': False,
})
def test_write(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.write(data)
    m.assert_called_with(os.path.join('.', 'text.md'), 'wt')
    handle.write.assert_called_with('# Title\n')

    data = NovelData('Book Intro', Type.BOOK_INTRO)
    markdown_writer.write(data)
    handle.write.assert_called_with('Book Intro\n')

    data = NovelData('Volume', Type.VOLUME_TITLE)
    markdown_writer.write(data)
    handle.write.assert_called_with('## Volume\n')

    data = NovelData('Volume Intro', Type.VOLUME_INTRO)
    markdown_writer.write(data)
    handle.write.assert_called_with('Volume Intro\n')

    data = NovelData('Title', Type.CHAPTER_TITLE, formatted='Chapter')
    markdown_writer.write(data)
    handle.write.assert_called_with('### Chapter\n')

    data = NovelData('Chapter Content', Type.CHAPTER_CONTENT)
    markdown_writer.write(data)
    handle.write.assert_called_with('Chapter Content\n')

    data = NovelData('', Type.BLANK)
    markdown_writer.write(data)
    handle.write.assert_called_with('\n')


@mark.args({
    'use_title': False,
    'levels': {'volume_title': 1, 'chapter_title': 2}
})
def test_levels(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.write(data)
    m.assert_called_with(os.path.join('.', 'text.md'), 'wt')
    handle.write.assert_called_with('Title\n')

    data = NovelData('Volume', Type.VOLUME_TITLE)
    markdown_writer.write(data)
    handle.write.assert_called_with('# Volume\n')

    data = NovelData('Title', Type.CHAPTER_TITLE, formatted='Chapter')
    markdown_writer.write(data)
    handle.write.assert_called_with('## Chapter\n')


@mark.args({
    'use_title': False,
    'write_blank': False
})
def test_no_write_blank(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('', Type.BLANK)
    markdown_writer.write(data)
    handle.write.assert_not_called()


@mark.args({
    'use_title': True,
})
def test_use_title(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())

    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.write(data)
    m.assert_called_with(os.path.join('.', 'Title.md'), 'wt')


@mark.args({
    'use_title': False,
    'md_filename': 'markdown.md',
})
def test_custom_title(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())

    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.write(data)
    m.assert_called_with(os.path.join('.', 'markdown.md'), 'wt')


@mark.args({
    'use_title': False,
    'debug': True
})
def test_debug(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open())
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.BOOK_TITLE, error='Error')
    markdown_writer.write(data)
    mp.assert_called_once_with('Error')
