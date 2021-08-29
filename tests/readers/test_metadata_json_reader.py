from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from common import Type
from readers.metadata_json_reader import MetadataJsonReader
from tests.helpers import assert_data


@fixture
def metadata_json_reader(mocker: MockerFixture, request: FixtureRequest):
    text = request.node.get_closest_marker('data').args[0]
    mocker.patch('builtins.open', mocker.mock_open(read_data=text))
    reader = MetadataJsonReader({'in_dir': ''})
    yield reader
    reader.cleanup()


@mark.data('{"title": "Test Title", "author": "Test Author"}')
def test_read(metadata_json_reader: MetadataJsonReader):
    data = metadata_json_reader.read()
    assert_data(data, 'Test Title', Type.BOOK_TITLE, author='Test Author')

    data = metadata_json_reader.read()
    assert data is None


def test_invalid(mocker: MockerFixture):
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"author": "Test Author"}'))
    with raises(ValueError, match='Metadata does not contain "title" field.'):
        MetadataJsonReader({'in_dir': ''})
