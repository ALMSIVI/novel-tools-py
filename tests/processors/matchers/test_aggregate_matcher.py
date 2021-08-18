from pytest import fixture
from common import NovelData, Type
from processors.matchers.numbered_matcher import NumberedMatcher
from processors.matchers.special_matcher import SpecialMatcher
from processors.matchers.__aggregate_matcher__ import AggregateMatcher


@fixture
def aggregate_matcher():
    return AggregateMatcher([
        NumberedMatcher({'type': 'volume_title', 'regex': 'Volume (.+) (.+)'}),
        SpecialMatcher({'type': 'chapter_title', 'affixes': ['Introduction', 'Prelude'], 'regex': '^{affixes} (.+)$'})
    ])


def test_numbered(aggregate_matcher: AggregateMatcher):
    before = NovelData('Volume 1 Test')
    after = aggregate_matcher.process(before)
    assert after.data_type == Type.VOLUME_TITLE
    assert after.index == 1
    assert after.content == 'Test'


def test_special(aggregate_matcher: AggregateMatcher):
    before = NovelData('Introduction Test')
    after = aggregate_matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.index == -1
    assert after.content == 'Test'
