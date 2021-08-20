from pytest import fixture
from common import NovelData, Type
from processors.validators.volume_validator import VolumeValidator


@fixture
def volume_validator():
    return VolumeValidator({})


@fixture
def special_validator():
    return VolumeValidator({'special_field': True})


def test_non_title(volume_validator: VolumeValidator, special_validator: VolumeValidator):
    before = NovelData('Non volume title', Type.CHAPTER_TITLE, 1)
    assert volume_validator.check(before) == False
    assert special_validator.check(before) == False


def test_special_title(volume_validator: VolumeValidator, special_validator: VolumeValidator):
    before = NovelData('Special title', Type.VOLUME_TITLE, -1, special_index=1)
    assert volume_validator.check(before) == False
    assert special_validator.check(before) == True


def test_regular_title(volume_validator: VolumeValidator, special_validator: VolumeValidator):
    before = NovelData('Volume title', Type.VOLUME_TITLE, 1)
    assert volume_validator.check(before) == True
    assert special_validator.check(before) == False


def test_messages(volume_validator: VolumeValidator):
    before = NovelData('Volume title', Type.VOLUME_TITLE, 1)
    volume_validator.process(before)

    before = NovelData('Duplicate volume 1', Type.VOLUME_TITLE, 1)
    after = volume_validator.process(before)
    assert after.get('error') == 'Duplicate volume - expected: 2, actual: index = 1, content = Duplicate volume 1'

    before = NovelData('Missing volume 3', Type.VOLUME_TITLE, 4)
    after = volume_validator.process(before)
    assert after.get('error') == 'Missing volume - expected: 3, actual: index = 4, content = Missing volume 3'


def test_special_messages(special_validator: VolumeValidator):
    before = NovelData('Volume title', Type.VOLUME_TITLE, -1, special_index=1)
    special_validator.process(before)

    before = NovelData('Duplicate volume 1', Type.VOLUME_TITLE, -1, special_index=1)
    after = special_validator.process(before)
    assert after.get('error') == 'Duplicate volume - expected: 2, actual: index = 1, content = Duplicate volume 1'

    before = NovelData('Missing volume 3', Type.VOLUME_TITLE, -1, special_index=4)
    after = special_validator.process(before)
    assert after.get('error') == 'Missing volume - expected: 3, actual: index = 4, content = Missing volume 3'
