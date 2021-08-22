import platform
from pytest import fixture, FixtureRequest, mark
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.csv_writer import CsvWriter


def ends(x: str) -> str:
    return x + ('\r\n' if platform.system() == 'Windows' else '\n')


@fixture
def csv_writer(request: FixtureRequest):
    args = request.node.get_closest_marker('args').args[0]
    writer = CsvWriter(args | {
        'out_dir': '.',
        'formats': {
            'volume_title': 'Volume {index}. {content}',
            'chapter_title': 'Chapter {index}. {content}'
        }
    })
    yield writer
    writer.cleanup()


@mark.args({'correct': False})
def test_write(csv_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Title', Type.BOOK_TITLE)
    csv_writer.write(data)
    handle.write.assert_not_called()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1)
    csv_writer.write(data)
    handle.write.assert_any_call(ends('type,index,content,formatted'))
    handle.write.assert_called_with(ends('VOLUME_TITLE,1,Lorem,Volume 1. Lorem'))

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 2)
    csv_writer.write(data)
    handle.write.assert_called_with(ends('CHAPTER_TITLE,2,Ipsum,Chapter 2. Ipsum'))


@mark.args({'correct': True})
def test_correct(csv_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, original_index=2)
    csv_writer.write(data)
    handle.write.assert_any_call(ends('type,index,content,formatted,original_index,original_formatted'))
    handle.write.assert_called_with(ends('VOLUME_TITLE,1,Lorem,Volume 1. Lorem,2,Volume 2. Lorem'))


@mark.args({'correct': False, 'debug': True})
def test_debug(csv_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, error='Error')
    csv_writer.write(data)
    handle.write.assert_any_call(ends('type,index,content,formatted,error'))
    handle.write.assert_called_with(ends('VOLUME_TITLE,1,Lorem,Volume 1. Lorem,Error'))


@mark.args({'correct': False, 'additional_fields': ['raw']})
def test_additional_fields(csv_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, raw='Volume One Lorem')
    csv_writer.write(data)
    handle.write.assert_any_call(ends('type,index,content,formatted,raw'))
    handle.write.assert_called_with(ends('VOLUME_TITLE,1,Lorem,Volume 1. Lorem,Volume One Lorem'))


@mark.args({'correct': True, 'debug': True, 'additional_fields': ['raw']})
def test_everything(csv_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, original_index=2, error='Error', raw='Volume One Lorem')
    csv_writer.write(data)
    handle.write.assert_any_call(ends('type,index,content,formatted,original_index,original_formatted,error,raw'))
    handle.write.assert_called_with(
        ends('VOLUME_TITLE,1,Lorem,Volume 1. Lorem,2,Volume 2. Lorem,Error,Volume One Lorem'))
