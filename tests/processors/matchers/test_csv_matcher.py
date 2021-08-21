from textwrap import dedent
from typing import Optional
from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from common import NovelData, Type
from processors.matchers.csv_matcher import CsvMatcher


def assert_data(data: NovelData, content: str, data_type: Type, index: Optional[int], **kwargs):
    assert data.content == content
    assert data.data_type == data_type
    assert data.index == index
    for key, value in kwargs.items():
        assert data.get(key) == value


def format_csv(csv: str):
    return dedent(csv).strip()


def create(args):
    return CsvMatcher(args | {'in_dir': ''})


@fixture
def csv_matcher(mocker: MockerFixture, request: FixtureRequest):
    csv, args = request.node.get_closest_marker('data').args
    csv = format_csv(csv)
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    matcher = create(args)
    yield matcher
    matcher.cleanup()


@mark.data('''
    raw
    Chapter 1 Lorem
    Chapter 2 Ipsum
''', {'type': 'chapter_title'})
def test_self_type(csv_matcher: CsvMatcher):
    before = NovelData('Chapter 1 Lorem')
    after = csv_matcher.process(before)
    assert_data(after, 'Chapter 1 Lorem', Type.CHAPTER_TITLE, 1, list_index=1)

    before = NovelData('Chapter 3 dolor')
    after = csv_matcher.process(before)
    assert_data(after, 'Chapter 3 dolor', Type.UNRECOGNIZED, None)

    before = NovelData('Chapter 2 Ipsum')
    after = csv_matcher.process(before)
    assert_data(after, 'Chapter 2 Ipsum', Type.CHAPTER_TITLE, 2, list_index=2)


@mark.data('''
    raw
    Volume 1 Lorem
    Chapter 1 Ipsum
''', {'regex': {'volume_title': 'Volume \\d+ .+', 'chapter_title': 'Chapter \\d+ .+'}})
def test_self_regex(csv_matcher: CsvMatcher):
    before = NovelData('Volume 1 Lorem')
    after = csv_matcher.process(before)
    assert_data(after, 'Volume 1 Lorem', Type.VOLUME_TITLE, 1, list_index=1)

    before = NovelData('Chapter 1 Ipsum')
    after = csv_matcher.process(before)
    assert_data(after, 'Chapter 1 Ipsum', Type.CHAPTER_TITLE, 1, list_index=2)


@mark.data('''
    type,raw
    volume_title,Volume 1 Lorem
    chapter_title,Chapter 1 Ipsum
''', {})
def test_list_type(csv_matcher: CsvMatcher):
    before = NovelData('Volume 1 Lorem')
    after = csv_matcher.process(before)
    assert_data(after, 'Volume 1 Lorem', Type.VOLUME_TITLE, 1, list_index=1)

    before = NovelData('Chapter 1 Ipsum')
    after = csv_matcher.process(before)
    assert_data(after, 'Chapter 1 Ipsum', Type.CHAPTER_TITLE, 1, list_index=2)


@mark.data('''
    raw,formatted
    Chapter One Lorem,Chapter 1 Lorem
''', {'type': 'chapter_title'})
def test_format(csv_matcher: CsvMatcher):
    before = NovelData('Chapter One Lorem')
    after = csv_matcher.process(before)
    assert_data(after, 'Chapter 1 Lorem', Type.CHAPTER_TITLE, 1, list_index=1)


def test_invalid(mocker: MockerFixture):
    csv = format_csv('''
            raw
            Chapter 1 Lorem
            Chapter 2 Ipsum
        ''')
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    with raises(ValueError, match='Type of title is not specified in file or arguments.'):
        create({})
