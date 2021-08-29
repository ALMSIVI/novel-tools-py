from pytest import fixture
from common import NovelData, Type
from processors.validators.volume_validator import VolumeValidator


@fixture
def volume_validator():
    validator = VolumeValidator({})
    yield validator
    validator.cleanup()


@fixture
def tag_validator():
    validator = VolumeValidator({'tag': 'extras'})
    yield validator
    validator.cleanup()


def test_non_title(volume_validator: VolumeValidator):
    before = NovelData('Non volume title', Type.CHAPTER_TITLE, 1)
    assert volume_validator.check(before) is False


def test_regular_title(volume_validator: VolumeValidator):
    before = NovelData('Volume title', Type.VOLUME_TITLE, 1)
    assert volume_validator.check(before) is True


def test_special_title(volume_validator: VolumeValidator):
    before = NovelData('Special Volume Title', Type.VOLUME_TITLE, -1)
    assert volume_validator.check(before) is False


def test_tag(tag_validator: VolumeValidator):
    before = NovelData('Volume 1', Type.VOLUME_TITLE, 1)
    assert tag_validator.check(before) is False

    before = NovelData('Volume 1', Type.VOLUME_TITLE, 1, tag='extras')
    assert tag_validator.check(before) is True


def test_messages(volume_validator: VolumeValidator):
    before = NovelData('Volume title', Type.VOLUME_TITLE, 1)
    volume_validator.process(before)

    before = NovelData('Duplicate volume 1', Type.VOLUME_TITLE, 1)
    after = volume_validator.process(before)
    assert after.get('error') == 'Duplicate volume - expected: 2, actual: index = 1, content = Duplicate volume 1'

    before = NovelData('Missing volume 3', Type.VOLUME_TITLE, 4)
    after = volume_validator.process(before)
    assert after.get('error') == 'Missing volume - expected: 3, actual: index = 4, content = Missing volume 3'
