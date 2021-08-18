from pytest import fixture
from common import Type
from processors.matchers.special_matcher import SpecialMatcher
from tests.utils import data


@fixture
def simple_matcher():
    return SpecialMatcher({
        'type': 'chapter_title',
        'affixes': ['Introduction', 'Prelude'],
        'regex': '^{affixes} (.+)$'
    })


@fixture
def group_matcher():
    return SpecialMatcher({
        'type': 'chapter_title',
        'affixes': ['Introduction'],
        'regex': '^(.+) of {affixes}$',
        'affix_group': 1,
        'content_group': 0
    })


@fixture
def group_index_matcher():
    return SpecialMatcher({
        'type': 'chapter_title',
        'affixes': ['Introduction'],
        'regex': '^{affixes} (.+)\. (.+)$',
        'index_group': 1,
        'content_group': 2
    })


def test_process(simple_matcher: SpecialMatcher):
    before = data('Introduction Test')
    after = simple_matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.index == -1
    assert after.content == 'Test'

    before = data('Prelude Test')
    after = simple_matcher.process(before)
    assert after.index == -2


def test_process_fail(simple_matcher: SpecialMatcher):
    before = data('Foreword Test')
    after = simple_matcher.process(before)
    assert after.data_type == Type.UNRECOGNIZED


def test_group(group_matcher: SpecialMatcher):
    before = data('Test of Introduction')
    after = group_matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.index == -1
    assert after.content == 'Test'


def test_group_index(group_index_matcher: SpecialMatcher):
    before = data('Introduction 1. Test')
    after = group_index_matcher.process(before)
    assert after.data_type == Type.CHAPTER_TITLE
    assert after.index == -1
    assert after.content == 'Test'
    assert after.get('special_index') == 1
