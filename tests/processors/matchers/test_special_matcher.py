from pytest import fixture
from common import NovelData, Type
from processors.matchers.special_matcher import SpecialMatcher
from tests.helpers.utils import assert_data


@fixture
def simple_matcher():
    matcher = SpecialMatcher({
        'type': 'chapter_title',
        'affixes': ['Introduction', 'Prelude'],
        'regex': '^{affixes} (.+)$'
    })
    yield matcher
    matcher.cleanup()


@fixture
def group_matcher():
    matcher = SpecialMatcher({
        'type': 'chapter_title',
        'affixes': ['Introduction'],
        'regex': '^(.+) of {affixes}$',
        'affix_group': 1,
        'content_group': 0
    })
    yield matcher
    matcher.cleanup()


@fixture
def tag_matcher():
    matcher = SpecialMatcher({
        'type': 'chapter_title',
        'affixes': ['Introduction'],
        'regex': '^{affixes} (.+)$',
        'tag': 'special'
    })
    yield matcher
    matcher.cleanup()


def test_process(simple_matcher: SpecialMatcher):
    before = NovelData('Introduction Test')
    after = simple_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -1, affix='Introduction')

    before = NovelData('Prelude Test')
    after = simple_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -2, affix='Prelude')


def test_process_fail(simple_matcher: SpecialMatcher):
    before = NovelData('Foreword Test')
    after = simple_matcher.process(before)
    assert_data(after, 'Foreword Test', Type.UNRECOGNIZED, None)


def test_group(group_matcher: SpecialMatcher):
    before = NovelData('Test of Introduction')
    after = group_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -1, affix='Introduction')


def test_tag(tag_matcher: SpecialMatcher):
    before = NovelData('Introduction Test')
    after = tag_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -1, affix='Introduction', tag='special')
