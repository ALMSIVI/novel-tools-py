import os
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.markdown_writer import MarkdownWriter


@fixture
def markdown_writer(request: FixtureRequest):
    args = request.node.get_closest_marker('args').args[0]
    return MarkdownWriter(args | {'out_dir': '.'})


@mark.args({
    'use_title': False,
})
def test_write(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

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
    m.assert_called_with(os.path.join('.', 'text.md'), 'wt')
    handle.assert_has_calls([
        mocker.call('# Title\n\n'),
        mocker.call('Book Intro'),
        mocker.call('\n\n'),
        mocker.call('## Volume\n\n'),
        mocker.call('Volume Intro'),
        mocker.call('\n\n'),
        mocker.call('### Chapter\n\n'),
        mocker.call('Chapter Content')
    ])


@mark.args({
    'use_title': False,
    'levels': {'volume_title': 1, 'chapter_title': 2}
})
def test_levels(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.accept(data)
    data = NovelData('Volume', Type.VOLUME_TITLE)
    markdown_writer.accept(data)
    data = NovelData('Title', Type.CHAPTER_TITLE, formatted='Chapter')
    markdown_writer.accept(data)

    markdown_writer.write()
    m.assert_called_with(os.path.join('.', 'text.md'), 'wt')
    handle.assert_has_calls([
        mocker.call('Title\n\n'),
        mocker.call('# Volume\n\n'),
        mocker.call('## Chapter\n\n')
    ])


@mark.args({
    'use_title': False,
    'write_newline': True
})
def test_newline(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Title', Type.CHAPTER_TITLE)
    markdown_writer.accept(data)

    data = NovelData('Test', Type.CHAPTER_CONTENT)
    markdown_writer.accept(data)

    data = NovelData('Test 2', Type.CHAPTER_CONTENT)
    markdown_writer.accept(data)

    markdown_writer.write()
    handle.assert_has_calls([
        mocker.call('### Title\n\n'),
        mocker.call('Test\n\nTest 2')
    ])


@mark.args({
    'use_title': True,
})
def test_use_title(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())

    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.accept(data)

    markdown_writer.write()
    m.assert_called_with(os.path.join('.', 'Title.md'), 'wt')


@mark.args({
    'use_title': False,
    'md_filename': 'markdown.md',
})
def test_custom_title(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())

    data = NovelData('Title', Type.BOOK_TITLE)
    markdown_writer.accept(data)

    markdown_writer.write()
    m.assert_called_with(os.path.join('.', 'markdown.md'), 'wt')


@mark.args({
    'use_title': False,
    'debug': True
})
def test_debug(markdown_writer: MarkdownWriter, mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open())
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.BOOK_TITLE, error='Error')
    markdown_writer.accept(data)

    markdown_writer.write()
    mp.assert_called_once_with('Error')
