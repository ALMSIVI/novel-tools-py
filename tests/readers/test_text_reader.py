from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from readers.text_reader import TextReader


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
    assert data == NovelData('line', Type.UNRECOGNIZED)

    data = text_reader.read()
    assert data == NovelData('', Type.UNRECOGNIZED)

    data = text_reader.read()
    assert data is None


@mark.data('line\n ', {'verbose': True})
def test_verbose(text_reader: TextReader):
    data = text_reader.read()
    assert data == NovelData('line', Type.UNRECOGNIZED, source='text.txt', line_num=1, raw='line')

    data = text_reader.read()
    assert data == NovelData('', Type.UNRECOGNIZED, source='text.txt', line_num=2, raw='')

    data = text_reader.read()
    assert data is None
