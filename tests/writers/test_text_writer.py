import os
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.text_writer import TextWriter


@fixture
def text_writer(request: FixtureRequest):
    args = request.node.get_closest_marker('args').args[0]
    return TextWriter(args | {'out_dir': '.'})


@mark.args({
    'use_title': False,
})
def test_write(text_writer: TextWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

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
    m.assert_called_with(os.path.join('.', 'text.txt'), 'wt')
    handle.assert_has_calls([
        mocker.call('Title\n\n'),
        mocker.call('Book Intro'),
        mocker.call('\n\n'),
        mocker.call('Volume\n\n'),
        mocker.call('Volume Intro'),
        mocker.call('\n\n'),
        mocker.call('Chapter\n\n'),
        mocker.call('Chapter Content')
    ])


@mark.args({
    'use_title': False,
    'levels': {'volume_title': 1, 'chapter_title': 2}
})
def test_levels(text_writer: TextWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Title', Type.BOOK_TITLE)
    text_writer.accept(data)
    data = NovelData('Volume', Type.VOLUME_TITLE)
    text_writer.accept(data)
    data = NovelData('Title', Type.CHAPTER_TITLE, formatted='Chapter')
    text_writer.accept(data)

    text_writer.write()
    m.assert_called_with(os.path.join('.', 'text.txt'), 'wt')
    handle.assert_has_calls([
        mocker.call('Title\n\n'),
        mocker.call('Volume\n\n'),
        mocker.call('Chapter\n\n')
    ])


@mark.args({
    'use_title': False,
    'write_newline': True
})
def test_newline(text_writer: TextWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Title', Type.CHAPTER_TITLE)
    text_writer.accept(data)

    data = NovelData('Test', Type.CHAPTER_CONTENT)
    text_writer.accept(data)

    data = NovelData('Test 2', Type.CHAPTER_CONTENT)
    text_writer.accept(data)

    text_writer.write()
    handle.assert_has_calls([
        mocker.call('Title\n\n'),
        mocker.call('Test\n\nTest 2')
    ])


@mark.args({
    'use_title': True,
})
def test_use_title(text_writer: TextWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())

    data = NovelData('Title', Type.BOOK_TITLE)
    text_writer.accept(data)

    text_writer.write()
    m.assert_called_with(os.path.join('.', 'Title.txt'), 'wt')


@mark.args({
    'use_title': False,
    'text_filename': 'book.txt',
})
def test_custom_title(text_writer: TextWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())

    data = NovelData('Title', Type.BOOK_TITLE)
    text_writer.accept(data)

    text_writer.write()
    m.assert_called_with(os.path.join('.', 'book.txt'), 'wt')


@mark.args({
    'use_title': False,
    'debug': True
})
def test_debug(text_writer: TextWriter, mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open())
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.BOOK_TITLE, error='Error')
    text_writer.accept(data)

    text_writer.write()
    mp.assert_called_once_with('Error')
