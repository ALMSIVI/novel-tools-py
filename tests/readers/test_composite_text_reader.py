from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from readers.text_reader import TextReader
from readers.composite_text_reader import CompositeTextReader
from textwrap import dedent


def format_structure(structure: str) -> str:
    return dedent(structure).strip()


@fixture
def composite_reader(mocker: MockerFixture, request: FixtureRequest):
    args, text, texts = request.node.get_closest_marker('args').args
    structure = format_structure(texts)
    mocker.patch('builtins.open', mocker.mock_open(read_data=structure))

    # We can only mock one file at a time, so we will mock structure first, and plug the FileReader in later
    args = args | {'in_dir': '.'}
    reader = CompositeTextReader(args)
    mocker.patch('builtins.open', mocker.mock_open(read_data=text))
    args = args | {'verbose': True}
    reader.reader = TextReader(args)
    yield reader
    reader.cleanup()


@mark.args({'structure': 'csv'}, 'Test Volume One\nTest Chapter One', '''
    type,content,index,formatted
    volume_title,Test Volume,1,Test Volume One
    chapter_title,Test Chapter,1,Test Chapter One
''')
def test_csv(composite_reader: CompositeTextReader):
    data = composite_reader.read()
    assert data == NovelData('Test Volume', Type.VOLUME_TITLE, 1, formatted='Test Volume One')

    data = composite_reader.read()
    assert data == NovelData('Test Chapter', Type.CHAPTER_TITLE, 1, formatted='Test Chapter One')

    data = composite_reader.read()
    assert data is None


@mark.args({'structure': 'toc', 'has_volume': True, 'discard_chapters': False}, 'Test Volume One\nTest Chapter One',
           '''
               Test Volume\t1
               \tTest Chapter\t2
           ''')
def test_toc(composite_reader: CompositeTextReader):
    data = composite_reader.read()
    assert data == NovelData('Test Volume', Type.VOLUME_TITLE, 1, line_num=1)

    data = composite_reader.read()
    assert data == NovelData('Test Chapter', Type.CHAPTER_TITLE, 1, line_num=2)

    data = composite_reader.read()
    assert data is None
