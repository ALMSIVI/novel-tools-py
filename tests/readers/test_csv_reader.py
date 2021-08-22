from textwrap import dedent
from pytest import fixture, FixtureRequest, mark, raises
from pytest_mock import MockerFixture
from common import Type
from readers.csv_reader import CsvReader
from tests.helpers.utils import assert_data


def format_csv(csv: str):
    return dedent(csv).strip()


@fixture
def csv_reader(mocker: MockerFixture, request: FixtureRequest):
    csv = request.node.get_closest_marker('data').args[0]
    csv = format_csv(csv)
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    reader = CsvReader({'in_dir': ''})
    yield reader
    reader.cleanup()


@mark.data('''
    type,content,index,formatted
    volume_title,Test Volume,1,Test
    chapter_title,Test Chapter,1,Test
''')
def test_read(csv_reader: CsvReader):
    data = csv_reader.read()
    assert_data(data, 'Test Volume', Type.VOLUME_TITLE, 1, formatted='Test')

    data = csv_reader.read()
    assert_data(data, 'Test Chapter', Type.CHAPTER_TITLE, 1, formatted='Test')

    data = csv_reader.read()
    assert data is None


def test_invalid(mocker: MockerFixture):
    csv = format_csv('''
    type,content
    volume_title, Test Volume
    ''')
    mocker.patch('builtins.open', mocker.mock_open(read_data=csv))
    with raises(ValueError, match='csv does not contain valid columns.'):
        CsvReader({'in_dir': ''})