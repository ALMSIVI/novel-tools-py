from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from typing import Iterator
from common import NovelData, Type
from readers.metadata_json_reader import MetadataJsonReader


@fixture
def read(mocker: MockerFixture, request: FixtureRequest):
    text = request.node.get_closest_marker('data').args[0]
    mocker.patch('builtins.open', mocker.mock_open(read_data=text))
    return MetadataJsonReader({'in_dir': ''}).read()


@mark.data('{"title": "Test Title", "author": "Test Author"}')
def test_read(read: Iterator[NovelData]):
    assert next(read) == NovelData('Test Title', Type.BOOK_TITLE, author='Test Author')
    with raises(StopIteration):
        next(read)


def test_invalid(mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"author": "Test Author"}'))
    with raises(ValueError, match='Metadata does not contain "title" field.'):
        MetadataJsonReader({'in_dir': ''})
