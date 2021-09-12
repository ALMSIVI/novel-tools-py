from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from processors.matchers.toc_matcher import TocMatcher
from utils import format_text


@fixture
def toc_matcher(mocker: MockerFixture, request: FixtureRequest):
    toc, args = request.node.get_closest_marker('data').args
    toc = format_text(toc)
    mocker.patch('builtins.open', mocker.mock_open(read_data=toc))
    return TocMatcher(args | {'in_dir': ''})


@mark.data('''
    Volume 1
    \tChapter 1
''', {'has_volume': True, 'discard_chapters': False})
def test_content(toc_matcher: TocMatcher):
    before = NovelData('Volume 1')
    after = toc_matcher.process(before)
    assert after == NovelData('Volume 1', Type.VOLUME_TITLE, 1, list_index=1, matched=True)

    before = NovelData('Volume 2')
    after = toc_matcher.process(before)
    assert after == NovelData('Volume 2', Type.UNRECOGNIZED, None)

    before = NovelData('Chapter 1')
    after = toc_matcher.process(before)
    assert after == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, list_index=2, matched=True)


@mark.data('''
    Volume 1\t1
    \tChapter 1\t25
''', {'has_volume': True, 'discard_chapters': False})
def test_index(toc_matcher: TocMatcher):
    before = NovelData('Volume One', line_num=1)
    after = toc_matcher.process(before)
    assert after == NovelData('Volume 1', Type.VOLUME_TITLE, 1, line_num=1, list_index=1, matched=True)

    before = NovelData('Chapter One', line_num=25)
    after = toc_matcher.process(before)
    assert after == NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, line_num=25, list_index=2, matched=True)
