from pytest import fixture
from common import NovelData, Type
from processors.transformers.pattern_transformer import PatternTransformer


@fixture
def pattern_transformer():
    transformer = PatternTransformer({
        'units': [
            {
                'filter': {
                    'type': 'chapter_content'
                },
                'subs': [
                    {
                        'pattern': '\*{3,}',
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
    yield transformer
    transformer.cleanup()


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