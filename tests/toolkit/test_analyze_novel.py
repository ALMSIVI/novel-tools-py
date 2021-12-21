from pathlib import Path
from pytest import mark
from pytest_mock import MockerFixture
from novel_tools.toolkit import analyze
from novel_tools.utils import get_config


def assert_file(actual: Path, expected: Path):
    with actual.open('rt') as f:
        actual_content = f.read()

    with expected.open('rt') as f:
        expected_content = f.read()

    # In Windows, the path separator is `\\` while in *nix the separator is `/`. When comparing csv files that have the
    # 'source' field, this might become an issue. The expected csv will be using `/`, so to ensure the tests run on
    # Windows, a replacement is required.
    actual_content = actual_content.replace('\\', '/')

    assert actual_content == expected_content


def assert_directory(actual: Path, expected: Path):
    actual_list = sorted(actual.iterdir())
    expected_list = sorted(expected.iterdir())
    for i in range(len(actual_list)):
        actual_child = actual_list[i]
        expected_child = expected_list[i]
        assert actual_child.name == expected_child.name
        assert actual_child.is_file() == expected_child.is_file()
        if actual_child.is_file():
            assert_file(actual_child, expected_child)
        else:
            assert_directory(actual_child, expected_child)


# Let us try the second workflow first: split -> struct_dir -> create_dir
@mark.slow
def test_split(toolkit_directories: tuple[Path, Path], mocker: MockerFixture):
    data_dir, output_dir = toolkit_directories
    data_dir = data_dir / 'Novel 1'
    mp = mocker.patch('builtins.print')
    analyze(get_config('split_config.json', data_dir), filename=data_dir / 'Novel 1.txt', out_dir=output_dir)

    assert_directory(output_dir, data_dir / 'dir')
    mp.assert_has_calls([
        mocker.call('Duplicate chapter in volume (index = 1, content = First Volume) - expected: 2, actual: index = 1,'
                    ' content = Second Chapter'),
        mocker.call('Missing chapter in volume (index = -1, content = Extra Volume) - expected: 4, actual: index = 5,'
                    ' content = Fourth Chapter')
    ])


@mark.slow
def test_struct_dir(toolkit_directories: tuple[Path, Path]):
    data_dir, output_dir = toolkit_directories
    data_dir = data_dir / 'Novel 1'
    analyze(get_config('struct_dir_config.json', data_dir), in_dir=data_dir / 'dir', out_dir=output_dir)

    assert_file(output_dir / 'list.csv', data_dir / 'list.csv')
    assert_file(output_dir / 'toc.txt', data_dir / 'toc.txt')


@mark.slow
def test_create_dir(toolkit_directories: tuple[Path, Path]):
    data_dir, output_dir = toolkit_directories
    data_dir = data_dir / 'Novel 1'
    analyze(get_config('create_dir_config.json', data_dir), in_dir=data_dir / 'dir', out_dir=output_dir)

    assert_file(output_dir / 'Test 1.md', data_dir / 'Test 1.md')


# Then let's try the most common workflow (which deserves more tests): struct -> create
@mark.slow
def test_struct_2(toolkit_directories: tuple[Path, Path]):
    data_dir, output_dir = toolkit_directories
    data_dir = data_dir / 'Novel 2'
    analyze(get_config('struct_config.json', data_dir), filename=data_dir / 'Novel 2.txt', out_dir=output_dir)

    assert_file(output_dir / 'toc.txt', data_dir / 'toc.txt')


@mark.slow
def test_create_2(toolkit_directories: tuple[Path, Path]):
    data_dir, output_dir = toolkit_directories
    data_dir = data_dir / 'Novel 2'
    analyze(get_config('create_config.json', data_dir), filename=data_dir / 'Novel 2.txt', out_dir=output_dir)

    assert_file(output_dir / 'text.md', data_dir / 'Novel 2.md')


@mark.slow
def test_struct_3(toolkit_directories: tuple[Path, Path]):
    data_dir, output_dir = toolkit_directories
    data_dir = data_dir / 'Novel 3'
    analyze(get_config('struct_config.json', data_dir), filename=data_dir / 'Novel 3.txt', out_dir=output_dir)

    assert_file(output_dir / 'list.csv', data_dir / 'list.csv')


@mark.slow
def test_create_3(toolkit_directories: tuple[Path, Path]):
    data_dir, output_dir = toolkit_directories
    data_dir = data_dir / 'Novel 3'
    analyze(get_config('create_config.json', data_dir), filename=data_dir / 'Novel 3.txt', out_dir=output_dir)

    assert_file(output_dir / 'Test 3.md', data_dir / 'Novel 3.md')


@mark.slow
def test_struct_4(toolkit_directories: tuple[Path, Path]):
    data_dir, output_dir = toolkit_directories
    data_dir = data_dir / 'Novel 4'
    analyze(get_config('struct_config.json', data_dir), filename=data_dir / 'Novel 4.txt', out_dir=output_dir)

    assert_file(output_dir / 'toc.txt', data_dir / 'toc.txt')
    assert_file(output_dir / 'list.csv', data_dir / 'list.csv')
