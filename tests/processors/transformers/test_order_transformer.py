from pytest import fixture
from novel_tools.framework import NovelData, Type
from novel_tools.processors.transformers.order_transformer import OrderTransformer


@fixture
def order_transformer():
    return OrderTransformer({})


def test_process(order_transformer: OrderTransformer):
    before = NovelData('Chapter 1', Type.CHAPTER_TITLE)
    after = order_transformer.process(before)
    assert after.get('order') == 1

    before = NovelData('Chapter 2', Type.CHAPTER_TITLE)
    after = order_transformer.process(before)
    assert after.get('order') == 2

    before = NovelData('Volume 1', Type.VOLUME_TITLE)
    after = order_transformer.process(before)
    assert after.get('order') == 1
