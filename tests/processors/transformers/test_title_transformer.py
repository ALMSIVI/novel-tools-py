from pytest import fixture
from novel_tools.common import NovelData, Type
from novel_tools.processors.transformers.title_transformer import TitleTransformer


@fixture
def title_transformer():
    return TitleTransformer({
        'units': [
            {
                'filter': {
                    'type': 'chapter_title',
                    'tag': 'special'
                },
                'format': {
                    'formatted': 'Special {content}',
                    'filename': 'Chapter {content}'
                }
            },
            {
                'filter': {
                    'type': 'volume_title',
                    'tag': 'special'
                },
                'format': 'Special Volume {index} {content}'
            },
            {
                'filter': {
                    'type': 'volume_title',
                },
                'format': 'Volume {index} {content}'
            }
        ]
    })


def test_transform(title_transformer: TitleTransformer):
    before = NovelData('Book Title', Type.BOOK_TITLE)
    after = title_transformer.process(before)
    assert not after.has('formatted')

    before = NovelData('Lorem', Type.VOLUME_TITLE, 1)
    after = title_transformer.process(before)
    assert after.get('formatted') == 'Volume 1 Lorem'

    before = NovelData('Lorem', Type.VOLUME_TITLE, 1, tag='special')
    after = title_transformer.process(before)
    assert after.get('formatted') == 'Special Volume 1 Lorem'

    before = NovelData('Chapter title', Type.CHAPTER_TITLE, 1)
    after = title_transformer.process(before)
    assert not after.has('formatted')

    before = NovelData('Chapter title', Type.CHAPTER_TITLE, 1, tag='not special')
    after = title_transformer.process(before)
    assert not after.has('formatted')

    before = NovelData('Ipsum', Type.CHAPTER_TITLE, 1, tag='special')
    after = title_transformer.process(before)
    assert after.get('formatted') == 'Special Ipsum'
    assert after.get('filename') == 'Chapter Ipsum'
