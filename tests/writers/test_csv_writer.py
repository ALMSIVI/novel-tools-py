from pathlib import Path
from pytest import fixture, FixtureRequest, mark
from common import NovelData, Type
from writers.csv_writer import CsvWriter


def assert_csv(csv_path: Path, expected: list[str]):
    assert csv_path.is_file()
    with csv_path.open('rt') as f:
        lines = f.readlines()
    assert len(lines) == len(expected)
    for i in range(len(lines)):
        assert lines[i].strip() == expected[i]


@fixture
def csv_writer(writer_directory: Path, request: FixtureRequest):
    node = request.node.get_closest_marker('args')
    custom_args = node.args[0] if node else {}
    return CsvWriter({'out_dir': writer_directory} | custom_args)


def test_write(csv_writer: CsvWriter, writer_directory: Path):
    data = NovelData('Title', Type.BOOK_TITLE)
    csv_writer.accept(data)
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem')
    csv_writer.accept(data)
    data = NovelData('Ipsum', Type.CHAPTER_TITLE, 2, formatted='Chapter 2. Ipsum')
    csv_writer.accept(data)

    csv_writer.write()
    csv_path = writer_directory / 'list.csv'
    assert_csv(csv_path, ['type,index,content,formatted',
                          'VOLUME_TITLE,1,Lorem,Volume 1. Lorem',
                          'CHAPTER_TITLE,2,Ipsum,Chapter 2. Ipsum'])


@mark.args({'csv_filename': 'custom.csv'})
def test_custom_name(csv_writer: CsvWriter, writer_directory: Path):
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem')
    csv_writer.accept(data)

    csv_writer.write()
    csv_path = writer_directory / 'custom.csv'
    assert_csv(csv_path, ['type,index,content,formatted',
                          'VOLUME_TITLE,1,Lorem,Volume 1. Lorem'])


@mark.args({'additional_fields': ['tag', 'raw']})
def test_additional_fields(csv_writer: CsvWriter, writer_directory: Path):
    data = NovelData('Lorem', Type.VOLUME_TITLE, 1, formatted='Volume 1. Lorem', tag='special', raw='Volume One Lorem')
    csv_writer.accept(data)

    csv_writer.write()
    csv_path = writer_directory / 'list.csv'
    assert_csv(csv_path, ['type,index,content,formatted,tag,raw',
                          'VOLUME_TITLE,1,Lorem,Volume 1. Lorem,special,Volume One Lorem'])
