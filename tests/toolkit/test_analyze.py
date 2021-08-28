import os
from pytest import mark
from pytest_mock import MockerFixture
from toolkit.analyze import analyze
from tests.helpers.integrations import assert_directory


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
