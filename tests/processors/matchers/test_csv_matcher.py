from textwrap import dedent
from pytest_mock import MockerFixture
from common import NovelData, Type
from processors.matchers.csv_matcher import CsvMatcher


def format_csv(csv):
    return dedent(csv).strip()


def create(args) -> CsvMatcher:
    return CsvMatcher(args | {'in_dir': ''})


def test_self_type(mocker: MockerFixture):
    csv = format_csv('''
        raw
        Chapter 1 Lorem
        Chapter 2 Ipsum
    ''')
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    matcher = create({'type': 'chapter_title'})

    before = NovelData(Type.UNRECOGNIZED, 'Chapter 1 Lorem')
    after = matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.content == 'Chapter 1 Lorem'

    before = NovelData(Type.UNRECOGNIZED, 'Chapter 3 dolor')
    after = matcher.process(before)
    assert after.data_type == Type.UNRECOGNIZED

    before = NovelData(Type.UNRECOGNIZED, 'Chapter 2 Ipsum')
    after = matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.content == 'Chapter 2 Ipsum'


def test_self_regex(mocker: MockerFixture):
    csv = format_csv('''
            raw
            Volume 1 Lorem
            Chapter 1 Ipsum
        ''')
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    matcher = create({'regex': {'volume_title': 'Volume \d+ .+', 'chapter_title': 'Chapter \d+ .+'}})

    before = NovelData(Type.UNRECOGNIZED, 'Volume 1 Lorem')
    after = matcher.process(before)
    assert after.data_type == Type.VOLUME_TITLE
    assert after.content == 'Volume 1 Lorem'

    before = NovelData(Type.UNRECOGNIZED, 'Chapter 1 Ipsum')
    after = matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.content == 'Chapter 1 Ipsum'


def test_list_type(mocker: MockerFixture):
    csv = format_csv('''
        type,raw
        volume_title,Volume 1 Lorem
        chapter_title,Chapter 1 Ipsum
    ''')
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    matcher = create({})

    before = NovelData(Type.UNRECOGNIZED, 'Volume 1 Lorem')
    after = matcher.process(before)
    assert after.data_type == Type.VOLUME_TITLE
    assert after.content == 'Volume 1 Lorem'

    before = NovelData(Type.UNRECOGNIZED, 'Chapter 1 Ipsum')
    after = matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.content == 'Chapter 1 Ipsum'


def test_format(mocker: MockerFixture):
    csv = format_csv('''
        raw,formatted
        Chapter One Lorem,Chapter 1 Lorem
    ''')
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    matcher = create({'type': 'chapter_title'})

    before = NovelData(Type.UNRECOGNIZED, 'Chapter One Lorem')
    after = matcher.process(before)
    assert after.content == 'Chapter 1 Lorem'
