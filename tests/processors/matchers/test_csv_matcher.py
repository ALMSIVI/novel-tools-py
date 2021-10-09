from pathlib import Path
from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from common import NovelData, Type
from processors.matchers.csv_matcher import CsvMatcher
from utils import format_text


@fixture
def csv_matcher(mocker: MockerFixture, request: FixtureRequest):
    csv, args = request.node.get_closest_marker('data').args
    csv = format_text(csv)
    mocker.patch('pathlib.Path.open', mocker.mock_open(read_data=csv))
    return CsvMatcher(args | {'in_dir': Path()})


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
    content,source,line_num
    Lorem,test1.txt,1
    Ipsum,test2.txt,10
''', {'data_type': 'chapter_title'})
def test_source_line_num(csv_matcher: CsvMatcher):
    before = NovelData('Chapter One Lorem', source=Path('test1.txt'), line_num=1)
    after = csv_matcher.process(before)
    assert after == NovelData('Lorem', Type.CHAPTER_TITLE, 1, source=Path('test1.txt'), line_num=1, list_index=1,
                              matched=True)

    before = NovelData('Chapter Two Ipsum', source=Path('test2.txt'), line_num=1)
    after = csv_matcher.process(before)
    assert after == NovelData('Chapter Two Ipsum', source=Path('test2.txt'), line_num=1)

    before = NovelData('Chapter Two Ipsum', source=Path('test2.txt'), line_num=10)
    after = csv_matcher.process(before)
    assert after == NovelData('Ipsum', Type.CHAPTER_TITLE, 2, source=Path('test2.txt'), line_num=10, list_index=2,
                              matched=True)


@mark.data('''
    content,line_num
    Lorem,2
    Ipsum,5
''', {'data_type': 'chapter_title'})
def test_line_num(csv_matcher: CsvMatcher):
    before = NovelData('Chapter One Lorem', line_num=1)
    after = csv_matcher.process(before)
    assert after == NovelData('Chapter One Lorem', line_num=1)

    before = NovelData('Chapter One Lorem', line_num=2)
    after = csv_matcher.process(before)
    assert after == NovelData('Lorem', Type.CHAPTER_TITLE, 1, line_num=2, list_index=1, matched=True)

    before = NovelData('Chapter Two Ipsum', line_num=5)
    after = csv_matcher.process(before)
    assert after == NovelData('Ipsum', Type.CHAPTER_TITLE, 2, line_num=5, list_index=2, matched=True)


@mark.data('''
    content,raw
    Lorem,Chapter One Lorem
    Ipsum,Chapter Two Ipsum
''', {'data_type': 'chapter_title', 'fields': ['raw']})
def test_raw(csv_matcher: CsvMatcher):
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
    csv = format_text('''
            content
            Chapter 1 Lorem
            Chapter 2 Ipsum
        ''')
    mocker.patch('pathlib.Path.open', mocker.mock_open(read_data=csv))
    with raises(ValueError, match='Type of title is not specified in file or arguments.'):
        CsvMatcher({'in_dir': Path()})
