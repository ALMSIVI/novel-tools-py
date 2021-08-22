from pytest import fixture
from common import NovelData, Type
from processors.validators.validator import Validator
from tests.helpers.utils import assert_data


class StubValidator(Validator):
    def check(self, data: NovelData) -> bool:
        return True

    def duplicate_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Duplicate - expected: {corrected_index}, actual: {self.get_index(data)}'

    def missing_message(self, data: NovelData, corrected_index: int) -> str:
        return f'Missing - expected: {corrected_index}, actual: {self.get_index(data)}'


@fixture
def overwrite_validator():
    validator = StubValidator({})
    yield validator
    validator.cleanup()


@fixture
def no_overwrite_validator():
    validator = StubValidator({'overwrite': False})
    yield validator
    validator.cleanup()


@fixture
def special_validator():
    validator = StubValidator({'special_field': True})
    yield validator
    validator.cleanup()


@fixture
def custom_special_validator():
    validator = StubValidator({'special_field': 'special'})
    yield validator
    validator.cleanup()


def test_duplicate(overwrite_validator: StubValidator, no_overwrite_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert_data(after1, 'First', Type.VOLUME_TITLE, 1)
    assert_data(after2, 'First', Type.VOLUME_TITLE, 1)

    before = NovelData('Duplicate First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert_data(after1, 'Duplicate First', Type.VOLUME_TITLE, 2, original_index=1,
                error='Duplicate - expected: 2, actual: 1')
    assert_data(after2, 'Duplicate First', Type.VOLUME_TITLE, 1, corrected_index=2,
                error='Duplicate - expected: 2, actual: 1')

    before = NovelData('Duplicate Second', Type.VOLUME_TITLE, 2)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert_data(after1, 'Duplicate Second', Type.VOLUME_TITLE, 3, original_index=2,
                error='Duplicate - expected: 3, actual: 2')
    assert_data(after2, 'Duplicate Second', Type.VOLUME_TITLE, 2, corrected_index=3,
                error='Duplicate - expected: 3, actual: 2')


def test_missing(overwrite_validator: StubValidator, no_overwrite_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, 1)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert_data(after1, 'First', Type.VOLUME_TITLE, 1)
    assert_data(after2, 'First', Type.VOLUME_TITLE, 1)

    before = NovelData('Skipping Second', Type.VOLUME_TITLE, 3)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert_data(after1, 'Skipping Second', Type.VOLUME_TITLE, 2, original_index=3,
                error='Missing - expected: 2, actual: 3')
    assert_data(after2, 'Skipping Second', Type.VOLUME_TITLE, 3, corrected_index=2,
                error='Missing - expected: 2, actual: 3')

    before = NovelData('Skipping Third', Type.VOLUME_TITLE, 10)
    after1 = overwrite_validator.process(before)
    after2 = no_overwrite_validator.process(before)
    assert_data(after1, 'Skipping Third', Type.VOLUME_TITLE, 3, original_index=10,
                error='Missing - expected: 3, actual: 10')
    assert_data(after2, 'Skipping Third', Type.VOLUME_TITLE, 10, corrected_index=3,
                error='Missing - expected: 3, actual: 10')


def test_special(special_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, -1, special_index=1)
    after = special_validator.process(before)
    assert_data(after, 'First', Type.VOLUME_TITLE, -1, special_index=1)

    before = NovelData('Duplicate First', Type.VOLUME_TITLE, -1, special_index=1)
    after = special_validator.process(before)
    assert_data(after, 'Duplicate First', Type.VOLUME_TITLE, -1, special_index=2, original_index=1,
                error='Duplicate - expected: 2, actual: 1')

    before = NovelData('Missing Third', Type.VOLUME_TITLE, -1, special_index=4)
    after = special_validator.process(before)
    assert_data(after, 'Missing Third', Type.VOLUME_TITLE, -1, special_index=3, original_index=4,
                error='Missing - expected: 3, actual: 4')


def test_custom_special(custom_special_validator: StubValidator):
    before = NovelData('First', Type.VOLUME_TITLE, -1, special=1)
    after = custom_special_validator.process(before)
    assert_data(after, 'First', Type.VOLUME_TITLE, -1, special=1)

    before = NovelData('Duplicate First', Type.VOLUME_TITLE, -1, special=1)
    after = custom_special_validator.process(before)
    assert_data(after, 'Duplicate First', Type.VOLUME_TITLE, -1, special=2, original_index=1,
                error='Duplicate - expected: 2, actual: 1')

    before = NovelData('Missing Third', Type.VOLUME_TITLE, -1, special=4)
    after = custom_special_validator.process(before)
    assert_data(after, 'Missing Third', Type.VOLUME_TITLE, -1, special=3, original_index=4,
                error='Missing - expected: 3, actual: 4')
