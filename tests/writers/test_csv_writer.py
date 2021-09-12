from pytest import fixture
from pytest_mock import MockerFixture
from common import NovelData, Type
from writers.csv_writer import CsvWriter


@fixture
def csv_writer():
    return CsvWriter({'out_dir': '.'})


@fixture
def additional_fields_writer():
    return CsvWriter({'out_dir': '.', 'additional_fields': ['tag', 'raw']})


def test_write(csv_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Title', Type.BOOK_TITLE)
    csv_writer.accept(data)
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem')
    csv_writer.accept(data)
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 2, formatted='Chapter 2. Ipsum')
    csv_writer.accept(data)

    csv_writer.write()
    handle.assert_has_calls([
        mocker.call('type,index,content,formatted\r\n'),
        mocker.call('VOLUME_TITLE,1,Lorem,Volume 1. Lorem\r\n'),
        mocker.call('CHAPTER_TITLE,2,Ipsum,Chapter 2. Ipsum\r\n')
    ])


def test_additional_fields(additional_fields_writer: CsvWriter, mocker: MockerFixture):
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem', tag='special', raw='Volume One Lorem')
    additional_fields_writer.accept(data)

    additional_fields_writer.write()
    handle.assert_has_calls([
        mocker.call('type,index,content,formatted,tag,raw\r\n'),
        mocker.call('VOLUME_TITLE,1,Lorem,Volume 1. Lorem,special,Volume One Lorem\r\n')
    ])
