from pytest import fixture
from novel_tools.framework import NovelData, Type
from novel_tools.processors.transformers.type_transformer import TypeTransformer


@fixture
def type_transformer():
    return TypeTransformer({})


def test_process(type_transformer: TypeTransformer):
    before = NovelData('Title')
    after = type_transformer.process(before)
    assert after.type == Type.BOOK_TITLE

    before = NovelData('Intro')
    after = type_transformer.process(before)
    assert after.type == Type.BOOK_INTRO

    before = NovelData('Volume 1', Type.VOLUME_TITLE)
    type_transformer.process(before)

    before = NovelData('Intro')
    after = type_transformer.process(before)
    assert after.type == Type.VOLUME_INTRO

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE)
    type_transformer.process(before)

    before = NovelData('Content')
    after = type_transformer.process(before)
    assert after.type == Type.CHAPTER_CONTENT

    before = NovelData('', Type.CHAPTER_TITLE)
    after = type_transformer.process(before)
    assert after.type == Type.CHAPTER_TITLE


def test_process_no_volume(type_transformer: TypeTransformer):
    before = NovelData('Title')
    after = type_transformer.process(before)
    assert after.type == Type.BOOK_TITLE

    before = NovelData('Intro')
    after = type_transformer.process(before)
    assert after.type == Type.BOOK_INTRO

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE)
    type_transformer.process(before)

    before = NovelData('Content')
    after = type_transformer.process(before)
    assert after.type == Type.CHAPTER_CONTENT

    before = NovelData('', Type.CHAPTER_TITLE)
    after = type_transformer.process(before)
    assert after.type == Type.CHAPTER_TITLE
