from pytest import fixture
from novel_tools.framework import NovelData, Type
from novel_tools.processors.validators.chapter_validator import ChapterValidator


@fixture
def no_discard_validator():
    return ChapterValidator({'discard_chapters': False})


@fixture
def discard_validator():
    return ChapterValidator({'discard_chapters': True})


@fixture
def tag_validator():
    return ChapterValidator({'discard_chapters': False, 'tag': 'extras'})


@fixture
def volume_tag_validator():
    return ChapterValidator({'discard_chapters': False, 'volume_tag': 'extras'})


def test_non_title(no_discard_validator: ChapterValidator, discard_validator: ChapterValidator):
    before = NovelData('Non chapter title', Type.VOLUME_TITLE, 1)
    assert no_discard_validator.check(before) is False
    assert discard_validator.check(before) is False


def test_special_title(no_discard_validator: ChapterValidator, discard_validator: ChapterValidator):
    before = NovelData('Special Title', Type.CHAPTER_TITLE, -1)
    assert no_discard_validator.check(before) is False
    assert discard_validator.check(before) is False


def test_regular_title(no_discard_validator: ChapterValidator, discard_validator: ChapterValidator):
    before = NovelData('Chapter title', Type.CHAPTER_TITLE, 1)
    assert no_discard_validator.check(before) is True
    assert discard_validator.check(before) is True


def test_discard(no_discard_validator: ChapterValidator, discard_validator: ChapterValidator):
    before = NovelData('Volume 1', Type.VOLUME_TITLE, 1)
    no_discard_validator.process(before)
    discard_validator.process(before)

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    no_discard_validator.process(before)
    discard_validator.process(before)

    before = NovelData('Volume 2', Type.VOLUME_TITLE, 2)
    no_discard_validator.process(before)
    discard_validator.process(before)

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    after1 = no_discard_validator.process(before)
    after2 = discard_validator.process(before)
    assert after1.index == 2
    assert after2.index == 1


def test_tag(tag_validator: ChapterValidator):
    before = NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    assert tag_validator.check(before) is False

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, tag='extras')
    assert tag_validator.check(before) is True


def test_volume_tag(volume_tag_validator: ChapterValidator):
    before = NovelData('Volume 1', Type.VOLUME_TITLE, 1)
    assert volume_tag_validator.check(before) is False

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    assert volume_tag_validator.check(before) is False

    before = NovelData('Volume 1', Type.VOLUME_TITLE, 1, tag='Test')
    assert volume_tag_validator.check(before) is False

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    assert volume_tag_validator.check(before) is False

    before = NovelData('Volume 1', Type.VOLUME_TITLE, 1, tag='extras')
    assert volume_tag_validator.check(before) is False

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE, 1)
    assert volume_tag_validator.check(before) is True


def test_no_volume_messages(no_discard_validator: ChapterValidator):
    before = NovelData('Chapter title', Type.CHAPTER_TITLE, 1)
    no_discard_validator.process(before)

    before = NovelData('Duplicate chapter 1', Type.CHAPTER_TITLE, 1)
    after = no_discard_validator.process(before)
    assert after.get('error') == 'Duplicate chapter - expected: 2, actual: index = 1, content = Duplicate chapter 1'

    before = NovelData('Missing chapter 3', Type.CHAPTER_TITLE, 4)
    after = no_discard_validator.process(before)
    assert after.get('error') == 'Missing chapter - expected: 3, actual: index = 4, content = Missing chapter 3'


def test_volume_messages(no_discard_validator: ChapterValidator):
    before = NovelData('Volume title', Type.VOLUME_TITLE, 1)
    no_discard_validator.process(before)

    before = NovelData('Chapter title', Type.CHAPTER_TITLE, 1)
    no_discard_validator.process(before)

    before = NovelData('Duplicate chapter 1', Type.CHAPTER_TITLE, 1)
    after = no_discard_validator.process(before)
    assert after.get('error') == 'Duplicate chapter in volume (index = 1, content = Volume title) - expected: 2, ' \
                                 'actual: index = 1, content = Duplicate chapter 1'

    before = NovelData('Missing chapter 3', Type.CHAPTER_TITLE, 4)
    after = no_discard_validator.process(before)
    assert after.get('error') == 'Missing chapter in volume (index = 1, content = Volume title) - expected: 3, ' \
                                 'actual: index = 4, content = Missing chapter 3'
