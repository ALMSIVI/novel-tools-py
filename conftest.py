import shutil
from pathlib import Path
from pytest import fixture


# When one (or GitHub) runs tests from the terminal, the working directory is set to the project root. However, when
# one runs the tests from an IDE (without changing run/debug configurations) , the working directory is set to
# 'tests' one level under the root directory. This messes up with functions and classes that rely on the current working
# directory, as well as integration tests that need to compare contents between directories and files.
#
# Therefore, before running your tests in the IDE, check that for all your tests, the working directory is NOT the
# 'test' directory, but the project root.


@fixture
def writer_directory():
    """
    Generates the test directories for the writer.
    """
    output_dir = Path('tests', 'writers', 'output')
    if not output_dir.is_dir():
        output_dir.mkdir()
    yield output_dir
    shutil.rmtree(output_dir)


@fixture
def toolkit_directories():
    """
    Generates the test directories for the toolkit.
    """

    test_dir = Path('tests', 'toolkit')
    data_dir = Path(test_dir, 'data')
    output_dir = Path(test_dir, 'output')

    if not output_dir.is_dir():
        output_dir.mkdir()
    yield data_dir, output_dir
    shutil.rmtree(output_dir)
