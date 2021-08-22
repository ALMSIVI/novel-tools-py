import os
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.directory_writer import DirectoryWriter


@fixture
def directory_writer(request: FixtureRequest):
    args = request.node.get_closest_marker('args').args[0]
    writer = DirectoryWriter(args | {'out_dir': '.'})
    yield writer
    writer.cleanup()


@mark.args({
    'formats': {
        'volume_title': 'Volume {index} {content}',
        'chapter_title': 'Chapter {index} {content}'
    },
    'correct': True})
def test_write(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Title', Type.BOOK_TITLE)
    directory_writer.write(data)
    mo.assert_called_with(os.path.join('.', '_intro.txt'), 'wt')
    handle.write.assert_called_with('Title\n')

    data = NovelData('Intro', Type.BOOK_INTRO)
    directory_writer.write(data)
    handle.write.assert_called_with('Intro\n')

    data = NovelData('Intro 2', Type.BOOK_INTRO)
    directory_writer.write(data)
    handle.write.assert_called_with('Intro 2\n')

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1)
    directory_writer.write(data)
    mm.assert_called_with(os.path.join('.', 'Volume 1 Lorem'))

    data = NovelData('Intro', Type.VOLUME_INTRO)
    directory_writer.write(data)
    handle.close.assert_called_once()
    mo.assert_called_with(os.path.join('.', 'Volume 1 Lorem', '_intro.txt'), 'wt')
    handle.write.assert_called_with('Intro\n')

    data = NovelData('Intro 2', Type.VOLUME_INTRO)
    directory_writer.write(data)
    handle.write.assert_called_with('Intro 2\n')

    handle.reset_mock()
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1)
    directory_writer.write(data)
    handle.close.assert_called_once()
    mo.assert_called_with(os.path.join('.', 'Volume 1 Lorem', 'Chapter 1 Ipsum.txt'), 'wt')
    handle.write.assert_called_with('Chapter 1 Ipsum\n')

    data = NovelData('Content', Type.CHAPTER_CONTENT)
    directory_writer.write(data)
    handle.write.assert_called_with('Content\n')

    data = NovelData('Content 2', Type.CHAPTER_CONTENT)
    directory_writer.write(data)
    handle.write.assert_called_with('Content 2\n')

    handle.reset_mock()
    data = NovelData('Dolor', Type.CHAPTER_TITLE, 2, original_index=3)
    directory_writer.write(data)
    handle.close.assert_called_once()
    mo.assert_called_with(os.path.join('.', 'Volume 1 Lorem', 'Chapter 2 Dolor.txt'), 'wt')
    handle.write.assert_called_with('Chapter 2 Dolor\n')

    handle.reset_mock()
    data = NovelData('Amet', Type.VOLUME_TITLE, 2, original_index=2)
    directory_writer.write(data)
    handle.close.assert_called_once()
    mm.assert_called_with(os.path.join('.', 'Volume 2 Amet'))


@mark.args({
    'formats': {
        'volume_title': 'Volume {index} {content}',
        'chapter_title': 'Chapter {index} {content}'
    },
    'correct': False
})
def test_no_correct(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, original_index=2)
    directory_writer.write(data)
    mm.assert_called_with(os.path.join('.', 'Volume 2 Lorem'))

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, original_index=3)
    directory_writer.write(data)
    mo.assert_called_with(os.path.join('.', 'Volume 2 Lorem', 'Chapter 3 Ipsum.txt'), 'wt')
    handle.write.assert_called_with('Chapter 3 Ipsum\n')


@mark.args({
    'formats': {
        'volume_title': 'Volume {index} {content}',
        'chapter_title': 'Chapter {index} {content}'
    },
    'correct': True
})
def test_default_volume(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('os.path.isdir', return_value=False)

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1)
    directory_writer.write(data)
    mm.assert_called_once_with(os.path.join('.', 'default'))
    mo.assert_called_with(os.path.join('.', 'default', 'Chapter 1 Ipsum.txt'), 'wt')


@mark.args({
    'formats': {
        'volume_title': 'Volume {index} {content}',
        'chapter_title': 'Chapter {index} {content}'
    },
    'correct': True,
    'default_volume': 'No Volume'
})
def test_custom_default_volume(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('os.path.isdir', return_value=False)

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1)
    directory_writer.write(data)
    mm.assert_called_once_with(os.path.join('.', 'No Volume'))
    mo.assert_called_with(os.path.join('.', 'No Volume', 'Chapter 1 Ipsum.txt'), 'wt')


@mark.args({
    'formats': {
        'volume_title': 'Volume {index} {content}',
        'chapter_title': 'Chapter {index} {content}'
    },
    'correct': False,
    'intro_filename': 'introduction.md'
})
def test_intro(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Title', Type.BOOK_TITLE)
    directory_writer.write(data)
    mo.assert_called_with(os.path.join('.', 'introduction.md'), 'wt')

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1)
    directory_writer.write(data)

    data = NovelData('Intro', Type.VOLUME_INTRO)
    directory_writer.write(data)
    handle.close.assert_called_once()
    mo.assert_called_with(os.path.join('.', 'Volume 1 Lorem', 'introduction.md'), 'wt')


@mark.args({
    'formats': {
        'volume_title': 'Volume {index} {content}',
        'chapter_title': 'Chapter {index} {content}'
    },
    'correct': False,
    'debug': True
})
def test_debug(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open())
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.CHAPTER_TITLE, error='Error')
    directory_writer.write(data)
    mp.assert_called_once_with('Error')


@mark.args({
    'formats': {
        'volume_title': 'Volume {index} {content}',
        'chapter_title': 'Chapter {index} {content}'
    },
    'correct': True,
    'debug': True
})
def test_debug_correct(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open())
    mp = mocker.patch('builtins.print')

    data = NovelData('Title', Type.CHAPTER_TITLE, 1, error='Error')
    directory_writer.write(data)
    mp.assert_any_call('Error')
    mp.assert_called_with('\t- Adjusted to Chapter 1 Title')


@mark.args({
    'formats': {
        'volume_title': 'Volume {index} {content}',
        'chapter_title': 'Chapter {index} {content}'
    },
    'correct': False,
    'write_blank': False
})
def test_write_blank(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Title', Type.BOOK_TITLE)
    directory_writer.write(data)

    handle.reset_mock()
    data = NovelData('', Type.BLANK)
    directory_writer.write(data)
    handle.write.assert_not_called()


@mark.args({
    'formats': {
        'volume_title': {'filename': 'v_{index}', 'title': 'Volume {index} {content}'},
        'chapter_title': {'filename': 'c_{index}', 'title': 'Chapter {index} {content}'}
    },
    'correct': True,
})
def test_separate_format(directory_writer: DirectoryWriter, mocker: MockerFixture):
    mm = mocker.patch('os.mkdir')
    mo = mocker.patch('builtins.open', mocker.mock_open())
    handle = mo()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1)
    directory_writer.write(data)
    mm.assert_called_with(os.path.join('.', 'v_1'))

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 1)
    directory_writer.write(data)
    mo.assert_called_with(os.path.join('.', 'v_1', 'c_1.txt'), 'wt')
    handle.write.assert_called_with('Chapter 1 Ipsum\n')
