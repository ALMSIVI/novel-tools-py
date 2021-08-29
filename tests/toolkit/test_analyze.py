import os
from pytest import mark
from pytest_mock import MockerFixture
from toolkit import analyze
from utils import get_config
from tests.helpers import assert_directory, assert_file


@mark.slow
def test_struct_1(directories: tuple[str, str], mocker: MockerFixture):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 1')
    mp = mocker.patch('builtins.print')
    analyze(get_config('analyze_1.json', data_dir), filename=os.path.join(data_dir, 'Novel 1.txt'), out_dir=output_dir)

    assert_directory(output_dir, os.path.join(data_dir, 'dir'))
    mp.assert_any_call('Duplicate chapter in volume (index = 1, content = First Volume) - expected: 2, actual: '
                       'index = 1, content = Second Chapter	- Adjusted to Chapter 2 Second Chapter')
    mp.assert_any_call('Missing chapter in volume (index = -1, content = Extra Volume) - expected: 4, actual: '
                       'index = 5, content = Fourth Chapter	- Adjusted to Chapter 4 Fourth Chapter')


@mark.slow
def test_struct_2(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 2')
    analyze(get_config('analyze_2.json', data_dir), filename=os.path.join(data_dir, 'Novel 2.txt'), out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'toc.txt'), os.path.join(data_dir, 'Novel 2 TOC.txt'))


@mark.slow
def test_struct_3(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 3')
    analyze(get_config('analyze_3.json', data_dir), filename=os.path.join(data_dir, 'Novel 3.txt'), out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'list.csv'), os.path.join(data_dir, 'Novel 3 CSV.csv'))


@mark.slow
def test_struct_4(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 4')
    analyze(get_config('analyze_4.json', data_dir), filename=os.path.join(data_dir, 'Novel 4.txt'), out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'list.csv'), os.path.join(data_dir, 'Novel 4 CSV.csv'))
    assert_file(os.path.join(output_dir, 'toc.txt'), os.path.join(data_dir, 'Novel 4 TOC.txt'))
