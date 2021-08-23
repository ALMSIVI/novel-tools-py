from pytest import fixture
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.csv_writer import CsvWriter


@fixture
def csv_writer():
    writer = CsvWriter({'out_dir': '.'})
    yield writer
    writer.cleanup()


@fixture
def additional_fields_writer():
    writer = CsvWriter({'out_dir': '.', 'additional_fields': ['tag', 'raw']})
    yield writer
    writer.cleanup()


def test_write(csv_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Title', Type.BOOK_TITLE)
    csv_writer.write(data)
    handle.write.assert_not_called()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem')
    csv_writer.write(data)
    handle.write.assert_any_call('type,index,content,formatted\r\n')
    handle.write.assert_called_with('VOLUME_TITLE,1,Lorem,Volume 1. Lorem\r\n')

    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 2, formatted='Chapter 2. Ipsum')
    csv_writer.write(data)
    handle.write.assert_called_with('CHAPTER_TITLE,2,Ipsum,Chapter 2. Ipsum\r\n')


def test_additional_fields(additional_fields_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem', tag='special', raw='Volume One Lorem')
    additional_fields_writer.write(data)
    handle.write.assert_any_call('type,index,content,formatted,tag,raw\r\n')
    handle.write.assert_called_with('VOLUME_TITLE,1,Lorem,Volume 1. Lorem,special,Volume One Lorem\r\n')
