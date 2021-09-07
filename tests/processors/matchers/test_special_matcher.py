from pytest import fixture, mark, FixtureRequest
from common import NovelData, Type
from processors.matchers.special_matcher import SpecialMatcher


@fixture
def special_matcher(request: FixtureRequest):
    node = request.node.get_closest_marker('args')
    custom_args = node.args[0] if node else {}
    args = {
        'type': 'chapter_title',
        'affixes': ['Introduction', 'Prelude'],
        'regex': '^{affixes} (.+)$'
    }
    matcher = SpecialMatcher(args | custom_args)
    yield matcher
    matcher.cleanup()


def test_process(special_matcher: SpecialMatcher):
    before = NovelData('Introduction Test')
    after = special_matcher.process(before)
    assert after == NovelData('Test', Type.CHAPTER_TITLE, -1, affix='Introduction', tag='special', matched=True)

    before = NovelData('Prelude Test')
    after = special_matcher.process(before)
    assert after == NovelData('Test', Type.CHAPTER_TITLE, -2, affix='Prelude', tag='special', matched=True)


def test_process_fail(special_matcher: SpecialMatcher):
    before = NovelData('Foreword Test')
    after = special_matcher.process(before)
    assert after == NovelData('Foreword Test', Type.UNRECOGNIZED, None)


@mark.args({'regex': '^(.+) of {affixes}$', 'affix_group': 1, 'content_group': 0})
def test_group(special_matcher: SpecialMatcher):
    before = NovelData('Test of Introduction')
    after = special_matcher.process(before)
    assert after == NovelData('Test', Type.CHAPTER_TITLE, -1, affix='Introduction', tag='special', matched=True)


@mark.args({'regex': '^{affixes}$', 'content_group': -1})
def test_no_content(special_matcher: SpecialMatcher):
    before = NovelData('Introduction')
    after = special_matcher.process(before)
    assert after == NovelData('', Type.CHAPTER_TITLE, -1, affix='Introduction', tag='special', matched=True)


@mark.args({'regex': '^{affixes} (.+)$', 'tag': 'intro'})
def test_tag(special_matcher: SpecialMatcher):
    before = NovelData('Introduction Test')
    after = special_matcher.process(before)
    assert after == NovelData('Test', Type.CHAPTER_TITLE, -1, affix='Introduction', tag='intro', matched=True)
