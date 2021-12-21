from pytest import fixture
from novel_tools.common import NovelData, Type
from novel_tools.processors.transformers.pattern_transformer import PatternTransformer


@fixture
def pattern_transformer():
    return PatternTransformer({
        'units': [
            {
                'filter': {
                    'type': 'chapter_content'
                },
                'subs': [
                    {
                        'pattern': '\\*{3,}',
                        'new': '---'
                    },
                    {
                        'pattern': '“(.+)”',
                        'new': '"{0}"'
                    }
                ]
            },
            {
                'filter': {
                    'type': 'volume_intro'
                },
                'subs': [
                    {
                        'pattern': '◇',
                        'new': '*'
                    }
                ]
            }
        ]
    })


def test_pattern(pattern_transformer: PatternTransformer):
    before = NovelData('******', Type.CHAPTER_CONTENT)
    after = pattern_transformer.process(before)
    assert after == NovelData('---', Type.CHAPTER_CONTENT)

    before = NovelData('“We want universal quotation marks.”', Type.CHAPTER_CONTENT)
    after = pattern_transformer.process(before)
    assert after == NovelData('"We want universal quotation marks."', Type.CHAPTER_CONTENT)

    before = NovelData('◇This needs to be highlighted◇', Type.VOLUME_INTRO)
    after = pattern_transformer.process(before)
    assert after == NovelData('*This needs to be highlighted*', Type.VOLUME_INTRO)
