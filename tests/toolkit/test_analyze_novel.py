import os
from pytest import mark
from pytest_mock import MockerFixture
from toolkit import analyze
from utils import get_config


def assert_file(actual: str, expected: str):
    with open(actual, 'rt') as f:
        actual_content = f.read()

    with open(expected, 'rt') as f:
        expected_content = f.read()

    assert actual_content == expected_content


def assert_directory(actual: str, expected: str):
    actual_list = os.listdir(actual)
    expected_list = os.listdir(expected)
    assert sorted(actual_list) == sorted(expected_list)

    for name in actual_list:
        actual_name = os.path.join(actual, name)
        expected_name = os.path.join(expected, name)
        if os.path.isfile(actual_name):
            assert_file(actual_name, expected_name)
        else:
            assert_directory(actual_name, expected_name)


# Let us try the second workflow first: split -> struct_dir -> create_dir
@mark.slow
def test_split(directories: tuple[str, str], mocker: MockerFixture):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 1')
    mp = mocker.patch('builtins.print')
    analyze(get_config('split_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 1.txt'),
            out_dir=output_dir)

    assert_directory(output_dir, os.path.join(data_dir, 'dir'))
    mp.assert_has_calls([
        mocker.call('Duplicate chapter in volume (index = 1, content = First Volume) - expected: 2, actual: index = 1,'
                    ' content = Second Chapter'),
        mocker.call('Missing chapter in volume (index = -1, content = Extra Volume) - expected: 4, actual: index = 5,'
                    ' content = Fourth Chapter')
    ])


@mark.slow
def test_struct_dir(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 1')
    analyze(get_config('struct_dir_config.json', data_dir), in_dir=os.path.join(data_dir, 'dir'), out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'list.csv'), os.path.join(data_dir, 'list.csv'))
    assert_file(os.path.join(output_dir, 'toc.txt'), os.path.join(data_dir, 'toc.txt'))


@mark.slow
def test_create_dir(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 1')
    analyze(get_config('create_dir_config.json', data_dir), in_dir=os.path.join(data_dir, 'dir'), out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'Test 1.md'), os.path.join(data_dir, 'Test 1.md'))


# Then let's try the most common workflow (which deserves more tests): struct -> create
@mark.slow
def test_struct_2(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 2')
    analyze(get_config('struct_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 2.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'toc.txt'), os.path.join(data_dir, 'toc.txt'))


@mark.slow
def test_create_2(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 2')
    analyze(get_config('create_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 2.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'text.md'), os.path.join(data_dir, 'Novel 2.md'))


@mark.slow
def test_struct_3(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 3')
    analyze(get_config('struct_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 3.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'list.csv'), os.path.join(data_dir, 'list.csv'))


@mark.slow
def test_create_3(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 3')
    analyze(get_config('create_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 3.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'Test 3.md'), os.path.join(data_dir, 'Novel 3.md'))


@mark.slow
def test_struct_4(directories: tuple[str, str]):
    data_dir, output_dir = directories
    data_dir = os.path.join(data_dir, 'Novel 4')
    analyze(get_config('struct_config.json', data_dir), filename=os.path.join(data_dir, 'Novel 4.txt'),
            out_dir=output_dir)

    assert_file(os.path.join(output_dir, 'toc.txt'), os.path.join(data_dir, 'toc.txt'))
    assert_file(os.path.join(output_dir, 'list.csv'), os.path.join(data_dir, 'list.csv'))
