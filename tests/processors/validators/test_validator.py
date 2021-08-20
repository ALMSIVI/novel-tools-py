from pytest import fixture
from common import NovelData, Type
from processors.validators.validator import Validator


class StubValidator(Validator):
    def check(self, data: NovelData) -> bool:
        return True

    def duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Duplicate - expected: {corrected_index}, actual: {self.get_index(data)}'

    def missing_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Missing - expected: {corrected_index}, actual: {self.get_index(data)}'


@fixture
def overwrite_validator():
    return StubValidator({})


@fixture
def no_overwrite_validator():
    return StubValidator({'overwrite': False})


@fixture
def special_validator():
    return StubValidator({'special_field': True})


@fixture
def custom_special_validator():
    return StubValidator({'special_field': 'special'})


def test_duplicate(overwrite_validator: StubValidator, no_overwrite_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1.index == 1
    assert after2.index == 1

    before = NovelData('Duplicate First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1.index == 2
    assert after1.get('original_index') == 1
    assert after1.get('error') == 'Duplicate - expected: 2, actual: 1'
    assert after2.index == 1
    assert after2.get('corrected_index') == 2
    assert after1.get('error') == 'Duplicate - expected: 2, actual: 1'

    before = NovelData('Duplicate Second', Type.VOLUME_TITLE, 2)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1.index == 3
    assert after1.get('original_index') == 2
    assert after1.get('error') == 'Duplicate - expected: 3, actual: 2'
    assert after2.index == 2
    assert after2.get('corrected_index') == 3
    assert after1.get('error') == 'Duplicate - expected: 3, actual: 2'


def test_missing(overwrite_validator: StubValidator, no_overwrite_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1.index == 1
    assert after2.index == 1

    before = NovelData('Skipping Second', Type.VOLUME_TITLE, 3)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1.index == 2
    assert after1.get('original_index') == 3
    assert after1.get('error') == 'Missing - expected: 2, actual: 3'
    assert after2.index == 3
    assert after2.get('corrected_index') == 2
    assert after1.get('error') == 'Missing - expected: 2, actual: 3'

    before = NovelData('Skipping Third', Type.VOLUME_TITLE, 10)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert after1.index == 3
    assert after1.get('original_index') == 10
    assert after1.get('error') == 'Missing - expected: 3, actual: 10'
    assert after2.index == 10
    assert after2.get('corrected_index') == 3
    assert after1.get('error') == 'Missing - expected: 3, actual: 10'
    pass


def test_special(special_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, -1, special_index=1)
    after = special_validator.process(before)
    assert after.get('special_index') == 1

    before = NovelData('Duplicate First', Type.VOLUME_TITLE, -1, special_index=1)
    after = special_validator.process(before)
    assert after.get('special_index') == 2
    assert after.get('original_index') == 1
    assert after.get('error') == 'Duplicate - expected: 2, actual: 1'

    before = NovelData('Missing Third', Type.VOLUME_TITLE, -1, special_index=4)
    after = special_validator.process(before)
    assert after.get('special_index') == 3
    assert after.get('original_index') == 4
    assert after.get('error') == 'Missing - expected: 3, actual: 4'


def test_custom_special(custom_special_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, -1, special=1)
    after = custom_special_validator.process(before)
    assert after.get('special') == 1

    before = NovelData('Duplicate First', Type.VOLUME_TITLE, -1, special=1)
    after = custom_special_validator.process(before)
    assert after.get('special') == 2
    assert after.get('original_index') == 1
    assert after.get('error') == 'Duplicate - expected: 2, actual: 1'

    before = NovelData('Missing Third', Type.VOLUME_TITLE, -1, special=4)
    after = custom_special_validator.process(before)
    assert after.get('special') == 3
    assert after.get('original_index') == 4
    assert after.get('error') == 'Missing - expected: 3, actual: 4'
