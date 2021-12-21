from pytest import fixture
from novel_tools.common import NovelData, Type
from novel_tools.processors.validators.validator import Validator


class StubValidator(Validator):
    def check(self, data: NovelData) -> bool:
        return True

    def _duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Duplicate - expected: {corrected_index}, actual: {data.index}'

    def _missing_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Missing - expected: {corrected_index}, actual: {data.index}'


@fixture
def overwrite_validator():
    return StubValidator({})


@fixture
def no_overwrite_validator():
    return StubValidator({'overwrite': False})


@fixture
def index_validator():
    return StubValidator({'begin_index': 128})


def test_duplicate(overwrite_validator: StubValidator, no_overwrite_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1 == NovelData('First', Type.VOLUME_TITLE, 1, original_index=1)
    assert after2 == NovelData('First', Type.VOLUME_TITLE, 1, corrected_index=1)

    before = NovelData('Duplicate First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1 == NovelData('Duplicate First', Type.VOLUME_TITLE, 2, original_index=1,
                               error='Duplicate - expected: 2, actual: 1')
    assert after2 == NovelData('Duplicate First', Type.VOLUME_TITLE, 1, corrected_index=2,
                               error='Duplicate - expected: 2, actual: 1')

    before = NovelData('Duplicate Second', Type.VOLUME_TITLE, 2)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1 == NovelData('Duplicate Second', Type.VOLUME_TITLE, 3, original_index=2,
                               error='Duplicate - expected: 3, actual: 2')
    assert after2 == NovelData('Duplicate Second', Type.VOLUME_TITLE, 2, corrected_index=3,
                               error='Duplicate - expected: 3, actual: 2')


def test_missing(overwrite_validator: StubValidator, no_overwrite_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1 == NovelData('First', Type.VOLUME_TITLE, 1, original_index=1)
    assert after2 == NovelData('First', Type.VOLUME_TITLE, 1, corrected_index=1)

    before = NovelData('Skipping Second', Type.VOLUME_TITLE, 3)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1 == NovelData('Skipping Second', Type.VOLUME_TITLE, 2, original_index=3,
                               error='Missing - expected: 2, actual: 3')
    assert after2 == NovelData('Skipping Second', Type.VOLUME_TITLE, 3, corrected_index=2,
                               error='Missing - expected: 2, actual: 3')

    before = NovelData('Skipping Third', Type.VOLUME_TITLE, 10)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1 == NovelData('Skipping Third', Type.VOLUME_TITLE, 3, original_index=10,
                               error='Missing - expected: 3, actual: 10')
    assert after2 == NovelData('Skipping Third', Type.VOLUME_TITLE, 10, corrected_index=3,
                               error='Missing - expected: 3, actual: 10')


def test_index(index_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, 1)
    after = index_validator.process(before)
    assert after == NovelData('First', Type.VOLUME_TITLE, 128, original_index=1,
                              error='Missing - expected: 128, actual: 1')
