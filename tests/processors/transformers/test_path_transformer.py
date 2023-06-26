from pathlib import Path
from pytest import fixture
from novel_tools.framework import NovelData, Type
from novel_tools.processors.transformers.path_transformer import PathTransformer


@fixture
def path_transformer():
    return PathTransformer({
        'in_dir': Path('test'),
        'fields': ['source', 'filename']
    })


def test_path(path_transformer: PathTransformer):
    before = NovelData('Volume', Type.VOLUME_TITLE, source=Path('test', 'volume'))
    after = path_transformer.process(before)
    assert after.get('source') == Path('volume')

    before = NovelData('Volume', Type.VOLUME_TITLE, filename=Path('test', 'volume 1'))
    after = path_transformer.process(before)
    assert after.get('filename') == Path('volume 1')

    before = NovelData('Volume', Type.VOLUME_TITLE, source=Path('test', 'volume 2'), filename=Path('test', 'volume 3'))
    after = path_transformer.process(before)
    assert after.get('source') == Path('volume 2')
    assert after.get('filename') == Path('volume 3')

    before = NovelData('Volume', Type.VOLUME_TITLE, test=Path('test', 'volume 4'))
    after = path_transformer.process(before)
    assert after.get('test') == Path('test', 'volume 4')
