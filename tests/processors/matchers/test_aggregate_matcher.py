from pytest import fixture
from common import Type
from processors.matchers.numbered_matcher import NumberedMatcher
from processors.matchers.special_matcher import SpecialMatcher
from processors.matchers.__aggregate_matcher__ import AggregateMatcher
from tests.utils import data


@fixture
def aggregate_matcher():
    return AggregateMatcher([
        NumberedMatcher({'type': 'volume_title', 'regex': 'Volume (.+) (.+)'}),
        SpecialMatcher({'type': 'chapter_title', 'affixes': ['Introduction', 'Prelude'], 'regex': '^{affixes} (.+)$'})
    ])


def test_numbered(aggregate_matcher: AggregateMatcher):
    before = data('Volume 1 Test')
    after = aggregate_matcher.process(before)
    assert after.data_type == Type.VOLUME_TITLE
    assert after.index == 1
    assert after.content == 'Test'


def test_special(aggregate_matcher: AggregateMatcher):
    before = data('Introduction Test')
    after = aggregate_matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.index == -1
    assert after.content == 'Test'
