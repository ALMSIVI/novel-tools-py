import os
from pytest import mark
from pytest_mock import MockerFixture
from toolkit.analyze_novel import analyze
from tests.helpers.integrations import assert_directory, assert_file


@mark.slow
def test_analyze_1(directories: tuple[str, str, str], mocker: MockerFixture):
    data_dir, target_dir, output_dir = directories
    mp = mocker.patch('builtins.print')
    analyze(os.path.join(data_dir, 'Novel 1.txt'), output_dir, 'analyze_1.json')

    assert_directory(output_dir, os.path.join(target_dir, 'Novel 1'))
    mp.assert_any_call('Duplicate chapter in volume (index = 1, content = First Volume) - expected: 2, actual: '
                       'index = 1, content = Second Chapter	- Adjusted to Chapter 2 Second Chapter')
    mp.assert_any_call('Missing chapter in volume (index = -1, content = Extra Volume) - expected: 4, actual: '
                       'index = 5, content = Fourth Chapter	- Adjusted to Chapter 4 Fourth Chapter')


@mark.slow
def test_analyze_2(directories: tuple[str, str, str]):
    data_dir, target_dir, output_dir = directories
    analyze(os.path.join(data_dir, 'Novel 2.txt'), output_dir, 'analyze_2.json')

    assert_file(os.path.join(output_dir, 'toc.txt'), os.path.join(target_dir, 'Novel 2 TOC.txt'))


@mark.slow
def test_analyze_3(directories: tuple[str, str, str]):
    data_dir, target_dir, output_dir = directories
    analyze(os.path.join(data_dir, 'Novel 3.txt'), output_dir, 'analyze_3.json')

    assert_file(os.path.join(output_dir, 'list.csv'), os.path.join(target_dir, 'Novel 3 CSV.csv'))


@mark.slow
def test_analyze_4(directories: tuple[str, str, str]):
    data_dir, target_dir, output_dir = directories
    analyze(os.path.join(data_dir, 'Novel 4.txt'), output_dir, 'analyze_4.json')

    assert_file(os.path.join(output_dir, 'list.csv'), os.path.join(target_dir, 'Novel 4 CSV.csv'))
    assert_file(os.path.join(output_dir, 'toc.txt'), os.path.join(target_dir, 'Novel 4 TOC.txt'))
