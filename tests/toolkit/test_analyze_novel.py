import os
from pytest import mark
from pytest_mock import MockerFixture
from toolkit import analyze
from utils import get_config
from tests.helpers import assert_directory, assert_file


# Let us try the second workflow first: split -> struct_dir -> create_dir
@mark.slow
def test_split(directories: tuple[str, str], mocker: MockerFixture):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 1')
    mp = mocker.patch('builtins.print')
    analyze(get_config('split_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 1.txt'),
            out_dir=output_dir)

    assert_directory(os.path.join(data_dir, 'dir'), output_dir)
    mp.assert_any_call('Duplicate chapter in volume (index = 1, content = First Volume) - expected: 2, actual: '
                       'index = 1, content = Second Chapter	- Adjusted to Chapter 2 Second Chapter')
    mp.assert_any_call('Missing chapter in volume (index = -1, content = Extra Volume) - expected: 4, actual: '
                       'index = 5, content = Fourth Chapter	- Adjusted to Chapter 4 Fourth Chapter')


@mark.slow
def test_struct_dir(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 1')
    analyze(get_config('struct_dir_config.json', data_dir), in_dir=os.path.join(data_dir, 'dir'), out_dir=output_dir)

    assert_file(os.path.join(data_dir, 'dir_list.csv'), os.path.join(output_dir, 'list.csv'))
    assert_file(os.path.join(data_dir, 'dir_toc.txt'), os.path.join(output_dir, 'toc.txt'))


@mark.slow
def test_create_dir(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 1')
    analyze(get_config('create_dir_config.json', data_dir), in_dir=os.path.join(data_dir, 'dir'), out_dir=output_dir)

    assert_file(os.path.join(data_dir, 'Test 1.md'), os.path.join(output_dir, 'Test 1.md'))


# Then let's try the most common workflow (which deserves more tests): struct -> create
@mark.slow
def test_struct_2(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 2')
    analyze(get_config('struct_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 2.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(data_dir, 'toc.txt'), os.path.join(output_dir, 'toc.txt'))


@mark.slow
def test_create_2(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 2')
    analyze(get_config('create_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 2.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(data_dir, 'Novel 2.md'), os.path.join(output_dir, 'text.md'))


@mark.slow
def test_struct_3(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 3')
    analyze(get_config('struct_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 3.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(data_dir, 'list.csv'), os.path.join(output_dir, 'list.csv'))


@mark.slow
def test_create_3(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 3')
    analyze(get_config('create_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 3.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(data_dir, 'Novel 3.md'), os.path.join(output_dir, 'Test 3.md'))


@mark.slow
def test_struct_4(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 4')
    analyze(get_config('struct_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 4.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(data_dir, 'toc.txt'), os.path.join(output_dir, 'toc.txt'))
    assert_file(os.path.join(data_dir, 'list.csv'), os.path.join(output_dir, 'list.csv'))
