from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from readers.text_reader import TextReader


def assert_data(data: NovelData, content: str, data_type: Type, **kwargs):
    assert data.content == content
    assert data.data_type == data_type
    for key, value in kwargs.items():
        assert data.get(key) == value


@fixture
def text_reader(mocker: MockerFixture, request: FixtureRequest):
    text, args = request.node.get_closest_marker('data').args
    mocker.patch('builtins.open', mocker.mock_open(read_data=text))
    reader = TextReader(args | {'filename': 'text.txt', 'in_dir': ''})
    yield reader
    reader.cleanup()


@mark.data('line\n ', {})
def test_read(text_reader: TextReader):
    data = text_reader.read()
    assert_data(data, 'line', Type.UNRECOGNIZED)

    data = text_reader.read()
    assert_data(data, '', Type.UNRECOGNIZED)

    data = text_reader.read()
    assert data is None


@mark.data('line\n ', {'verbose': True})
def test_verbose(text_reader: TextReader):
    data = text_reader.read()
    assert_data(data, 'line', Type.UNRECOGNIZED, line_num=1, raw='line')

    data = text_reader.read()
    assert_data(data, '', Type.UNRECOGNIZED, line_num=2, raw='')

    data = text_reader.read()
    assert data is None
