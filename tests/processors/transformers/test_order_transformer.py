from pytest import fixture
from common import NovelData, Type
from processors.transformers.order_transformer import OrderTransformer


@fixture
def order_transformer():
    transformer = OrderTransformer({})
    yield transformer
    transformer.cleanup()


def test_process(order_transformer):
    before = NovelData('Chapter 1', Type.CHAPTER_TITLE)
    after = order_transformer.process(before)
    assert after.get('order') == 1

    before = NovelData('Chapter 2', Type.CHAPTER_TITLE)
    after = order_transformer.process(before)
    assert after.get('order') == 2

    before = NovelData('Volume 1', Type.VOLUME_TITLE)
    after = order_transformer.process(before)
    assert after.get('order') == 1
