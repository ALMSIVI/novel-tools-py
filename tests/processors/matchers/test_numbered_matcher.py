from typing import Optional
from pytest import fixture
from common import NovelData, Type
from processors.matchers.numbered_matcher import NumberedMatcher


def assert_data(data: NovelData, content: str, data_type: Type, index: Optional[int]):
    assert data.content == content
    assert data.data_type == data_type
    assert data.index == index


@fixture
def simple_matcher():
    matcher = NumberedMatcher({
        'type': 'volume_title',
        'regex': 'Volume (.+) (.+)'
    })
    yield matcher
    matcher.cleanup()


@fixture
def group_matcher():
    matcher = NumberedMatcher({
        'type': 'volume_title',
        'regex': '(.+) of Volume (.+)',
        'index_group': 1,
        'content_group': 0
    })
    yield matcher
    matcher.cleanup()


def test_process(simple_matcher: NumberedMatcher):
    before = NovelData('Volume 1 Test')
    after = simple_matcher.process(before)
    assert_data(after, 'Test', Type.VOLUME_TITLE, 1)


def test_process_fail(simple_matcher: NumberedMatcher):
    before = NovelData('Volume abc Test')
    after = simple_matcher.process(before)
    assert_data(after, 'Volume abc Test', Type.UNRECOGNIZED, None)


def test_process_chinese(simple_matcher: NumberedMatcher):
    before = NovelData('Volume 十一 测试')
    after = simple_matcher.process(before)
    assert_data(after, '测试', Type.VOLUME_TITLE, 11)


def test_process_chinese_fail(simple_matcher: NumberedMatcher):
    before = NovelData('Volume 十人 测试')
    after = simple_matcher.process(before)
    assert after.data_type == Type.UNRECOGNIZED
    assert after.index is None
    assert_data(after, 'Volume 十人 测试', Type.UNRECOGNIZED, None)


def test_process_group(group_matcher: NumberedMatcher):
    before = NovelData('Test of Volume 1')
    after = group_matcher.process(before)
    assert_data(after, 'Test', Type.VOLUME_TITLE, 1)
