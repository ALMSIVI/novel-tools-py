from pytest import fixture
from common import NovelData, Type
from processors.matchers.numbered_matcher import NumberedMatcher


@fixture
def simple_matcher():
    return NumberedMatcher({
        'type': 'volume_title',
        'regex': 'Volume (.+) (.+)'
    })


@fixture
def group_matcher():
    return NumberedMatcher({
        'type': 'volume_title',
        'regex': '(.+) of Volume (.+)',
        'index_group': 1,
        'content_group': 0
    })


def data(content):
    return NovelData(Type.UNRECOGNIZED, content)


def test_process(simple_matcher: NumberedMatcher):
    before = data('Volume 1 Test')
    after = simple_matcher.process(before)
    assert after.data_type == Type.VOLUME_TITLE
    assert after.index == 1
    assert after.content == 'Test'


def test_process_fail(simple_matcher: NumberedMatcher):
    before = data('Volume abc Test')
    after = simple_matcher.process(before)
    assert after.data_type == Type.UNRECOGNIZED
    assert after.index is None
    assert after.content == 'Volume abc Test'


def test_process_chinese(simple_matcher: NumberedMatcher):
    before = data('Volume 十一 测试')
    after = simple_matcher.process(before)
    assert after.data_type == Type.VOLUME_TITLE
    assert after.index == 11
    assert after.content == '测试'


def test_process_chinese_fail(simple_matcher: NumberedMatcher):
    before = data('Volume 十人 测试')
    after = simple_matcher.process(before)
    assert after.data_type == Type.UNRECOGNIZED
    assert after.index is None
    assert after.content == 'Volume 十人 测试'


def test_process_group(group_matcher: NumberedMatcher):
    before = data('Test of Volume 1')
    after = group_matcher.process(before)
    assert after.data_type == Type.VOLUME_TITLE
    assert after.index == 1
    assert after.content == 'Test'
