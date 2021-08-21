from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from common import NovelData, Type
from readers.metadata_json_reader import MetadataJsonReader


def assert_data(data: NovelData, content: str, data_type: Type, **kwargs):
    assert data.content == content
    assert data.data_type == data_type
    for key, value in kwargs.items():
        assert data.get(key) == value


def create() -> MetadataJsonReader:
    return MetadataJsonReader({'in_dir': ''})


@fixture
def metadata_json_reader(mocker: MockerFixture, request: FixtureRequest):
    text = request.node.get_closest_marker('data').args[0]
    mocker.patch('builtins.open', mocker.mock_open(read_data=text))
    reader = create()
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
        create()
