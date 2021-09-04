from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from textwrap import dedent
from common import NovelData, Type
from processors.matchers.csv_matcher import CsvMatcher


def format_structure(structure: str) -> str:
    return dedent(structure).strip()


@fixture
def csv_matcher(mocker: MockerFixture, request: FixtureRequest):
    csv, args = request.node.get_closest_marker('data').args
    csv = format_structure(csv)
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    matcher = CsvMatcher(args | {'in_dir': ''})
    yield matcher
    matcher.cleanup()


@mark.data('''
    content
    Chapter 1 Lorem
    Chapter 2 Ipsum
''', {'data_type': 'chapter_title'})
def test_self_type(csv_matcher: CsvMatcher):
    before = NovelData('Chapter 1 Lorem')
    after = csv_matcher.process(before)
    assert after == NovelData('Chapter 1 Lorem', Type.CHAPTER_TITLE, 1, list_index=1, matched=True)

    before = NovelData('Chapter 3 dolor')
    after = csv_matcher.process(before)
    assert after == NovelData('Chapter 3 dolor', Type.UNRECOGNIZED, None)

    before = NovelData('Chapter 2 Ipsum')
    after = csv_matcher.process(before)
    assert after == NovelData('Chapter 2 Ipsum', Type.CHAPTER_TITLE, 2, list_index=2, matched=True)


@mark.data('''
    type,content
    volume_title,Volume 1 Lorem
    chapter_title,Chapter 1 Ipsum
''', {})
def test_list_type(csv_matcher: CsvMatcher):
    before = NovelData('Volume 1 Lorem')
    after = csv_matcher.process(before)
    assert after == NovelData('Volume 1 Lorem', Type.VOLUME_TITLE, 1, list_index=1, matched=True)

    before = NovelData('Chapter 1 Ipsum')
    after = csv_matcher.process(before)
    assert after == NovelData('Chapter 1 Ipsum', Type.CHAPTER_TITLE, 1, list_index=2, matched=True)


@mark.data('''
    content,raw
    Lorem,Chapter One Lorem
    Ipsum,Chapter Two Ipsum
''', {'data_type': 'chapter_title', 'fields': ['raw']})
def test_custom_field(csv_matcher: CsvMatcher):
    before = NovelData('Chapter One Lorem', raw='Chapter One Lorem')
    after = csv_matcher.process(before)
    assert after == NovelData('Lorem', Type.CHAPTER_TITLE, 1, list_index=1, matched=True, raw='Chapter One Lorem')

    before = NovelData('Chapter Two Ipsum', raw='Chapter Two Ipsum')
    after = csv_matcher.process(before)
    assert after == NovelData('Ipsum', Type.CHAPTER_TITLE, 2, list_index=2, matched=True, raw='Chapter Two Ipsum')


@mark.data('''
    content,index
    Chapter 10 Lorem,10
    Chapter 11 Ipsum,11
''', {'data_type': 'chapter_title'})
def test_index(csv_matcher: CsvMatcher):
    before = NovelData('Chapter 10 Lorem')
    after = csv_matcher.process(before)
    assert after == NovelData('Chapter 10 Lorem', Type.CHAPTER_TITLE, 10, list_index=1, matched=True)

    before = NovelData('Chapter 11 Ipsum')
    after = csv_matcher.process(before)
    assert after == NovelData('Chapter 11 Ipsum', Type.CHAPTER_TITLE, 11, list_index=2, matched=True)


def test_invalid(mocker: MockerFixture):
    csv = format_structure('''
            content
            Chapter 1 Lorem
            Chapter 2 Ipsum
        ''')
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    with raises(ValueError, match='Type of title is not specified in file or arguments.'):
        CsvMatcher({'in_dir': ''})
