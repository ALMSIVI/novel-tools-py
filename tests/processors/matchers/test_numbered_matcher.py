from pytest import fixture, mark, FixtureRequest
from novel_tools.framework import NovelData, Type
from novel_tools.processors.matchers.numbered_matcher import NumberedMatcher


@fixture
def numbered_matcher(request: FixtureRequest):
    node = request.node.get_closest_marker('args')
    custom_args = node.args[0] if node else {}
    args = {
        'type': 'volume_title',
        'regex': '^Volume (.+) (.+)$'
    }
    return NumberedMatcher(args | custom_args)


def test_process(numbered_matcher: NumberedMatcher):
    before = NovelData('Volume 1 Test')
    after = numbered_matcher.process(before)
    assert after == NovelData('Test', Type.VOLUME_TITLE, 1, matched=True)


def test_process_fail(numbered_matcher: NumberedMatcher):
    before = NovelData('Volume abc Test')
    after = numbered_matcher.process(before)
    assert after == NovelData('Volume abc Test', Type.UNRECOGNIZED, None)


def test_process_chinese(numbered_matcher: NumberedMatcher):
    before = NovelData('Volume 十一 测试')
    after = numbered_matcher.process(before)
    assert after == NovelData('测试', Type.VOLUME_TITLE, 11, matched=True)


def test_process_chinese_fail(numbered_matcher: NumberedMatcher):
    before = NovelData('Volume 十人 测试')
    after = numbered_matcher.process(before)
    assert after == NovelData('Volume 十人 测试', Type.UNRECOGNIZED, None)


@mark.args({'regex': '^(.+) of Volume (.+)$', 'index_group': 1, 'content_group': 0})
def test_process_group(numbered_matcher: NumberedMatcher):
    before = NovelData('Test of Volume 1')
    after = numbered_matcher.process(before)
    assert after == NovelData('Test', Type.VOLUME_TITLE, 1, matched=True)


@mark.args({'regex': '^Volume (.+)$', 'content_group': -1})
def test_no_content(numbered_matcher: NumberedMatcher):
    before = NovelData('Volume 1')
    after = numbered_matcher.process(before)
    assert after == NovelData('', Type.VOLUME_TITLE, 1, matched=True)


@mark.args({'regex': '^Extra (.+) (.+)$', 'tag': 'extras'})
def test_tag(numbered_matcher: NumberedMatcher):
    before = NovelData('Extra 1 Test')
    after = numbered_matcher.process(before)
    assert after == NovelData('Test', Type.VOLUME_TITLE, 1, tag='extras', matched=True)
