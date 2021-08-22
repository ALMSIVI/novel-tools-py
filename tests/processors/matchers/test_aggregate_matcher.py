from pytest import fixture
from common import NovelData, Type
from processors.matchers.numbered_matcher import NumberedMatcher
from processors.matchers.special_matcher import SpecialMatcher
from processors.matchers.__aggregate_matcher__ import AggregateMatcher
from tests.helpers.utils import assert_data


@fixture
def aggregate_matcher():
    matcher = AggregateMatcher([
        NumberedMatcher({'type': 'volume_title', 'regex': 'Volume (.+) (.+)'}),
        SpecialMatcher({'type': 'chapter_title', 'affixes': ['Introduction', 'Prelude'], 'regex': '^{affixes} (.+)$'})
    ])
    yield matcher
    matcher.cleanup()


def test_numbered(aggregate_matcher: AggregateMatcher):
    before = NovelData('Volume 1 Test')
    after = aggregate_matcher.process(before)
    assert_data(after, 'Test', Type.VOLUME_TITLE, 1)


def test_special(aggregate_matcher: AggregateMatcher):
    before = NovelData('Introduction Test')
    after = aggregate_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -1)
