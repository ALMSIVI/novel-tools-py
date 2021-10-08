from pytest import fixture
from common import NovelData, Type
from processors.matchers.numbered_matcher import NumberedMatcher
from processors.matchers.special_matcher import SpecialMatcher
from processors.matchers.__aggregate_matcher import AggregateMatcher


@fixture
def aggregate_matcher():
    return AggregateMatcher([
        NumberedMatcher({'type': 'volume_title', 'regex': 'Volume (.+) (.+)'}),
        SpecialMatcher({'type': 'chapter_title', 'affixes': ['Introduction', 'Prelude'], 'regex': '^{affixes} (.+)$'})
    ])


def test_numbered(aggregate_matcher: AggregateMatcher):
    before = NovelData('Volume 1 Test')
    after = aggregate_matcher.process(before)
    assert after == NovelData('Test', Type.VOLUME_TITLE, 1)


def test_special(aggregate_matcher: AggregateMatcher):
    before = NovelData('Introduction Test')
    after = aggregate_matcher.process(before)
    assert after == NovelData('Test', Type.CHAPTER_TITLE, -1, affix='Introduction', tag='special')
