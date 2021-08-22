from pytest import fixture
from common import NovelData, Type
from processors.validators.chapter_validator import ChapterValidator


@fixture
def no_discard_validator():
    validator = ChapterValidator({'discard_chapters': False})
    yield validator
    validator.cleanup()


@fixture
def discard_validator():
    validator = ChapterValidator({'discard_chapters': True})
    yield validator
    validator.cleanup()


@fixture
def tag_validator():
    validator = ChapterValidator({'discard_chapters': False, 'tag': 'extras'})
    yield validator
    validator.cleanup()


def test_non_title(no_discard_validator: ChapterValidator, discard_validator: ChapterValidator):
    before = NovelData('Non chapter title', Type.VOLUME_TITLE, 1)
    assert no_discard_validator.check(before) == False
    assert discard_validator.check(before) == False


def test_special_title(no_discard_validator: ChapterValidator, discard_validator: ChapterValidator):
    before = NovelData('Special Title', Type.CHAPTER_TITLE, -1)
    assert no_discard_validator.check(before) == False
    assert discard_validator.check(before) == False


def test_regular_title(no_discard_validator: ChapterValidator, discard_validator: ChapterValidator):
    before = NovelData('Chapter title', Type.CHAPTER_TITLE, 1)
    assert no_discard_validator.check(before) == True
    assert discard_validator.check(before) == True


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
    assert tag_validator.check(before) == False

    before = NovelData('Chapter 1', Type.CHAPTER_TITLE, 1, tag='extras')
    assert tag_validator.check(before) == True


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
