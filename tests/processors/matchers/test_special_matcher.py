from typing import Optional
from pytest import fixture
from common import NovelData, Type
from processors.matchers.special_matcher import SpecialMatcher


def assert_data(data: NovelData, content: str, data_type: Type, index: Optional[int], **kwargs):
    assert data.content == content
    assert data.data_type == data_type
    assert data.index == index
    for key, value in kwargs.items():
        assert data.get(key) == value


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
def group_index_matcher():
    matcher = SpecialMatcher({
        'type': 'chapter_title',
        'affixes': ['Introduction'],
        'regex': '^{affixes} (.+)\\. (.+)$',
        'index_group': 1,
        'content_group': 2
    })
    yield matcher
    matcher.cleanup()


def test_process(simple_matcher: SpecialMatcher):
    before = NovelData('Introduction Test')
    after = simple_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -1)

    before = NovelData('Prelude Test')
    after = simple_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -2)


def test_process_fail(simple_matcher: SpecialMatcher):
    before = NovelData('Foreword Test')
    after = simple_matcher.process(before)
    assert_data(after, 'Foreword Test', Type.UNRECOGNIZED, None)


def test_group(group_matcher: SpecialMatcher):
    before = NovelData('Test of Introduction')
    after = group_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -1)


def test_group_index(group_index_matcher: SpecialMatcher):
    before = NovelData('Introduction 1. Test')
    after = group_index_matcher.process(before)
    assert_data(after, 'Test', Type.CHAPTER_TITLE, -1, special_index=1)
