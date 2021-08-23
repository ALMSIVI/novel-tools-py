import os
import shutil
from pytest import fixture, MonkeyPatch


@fixture
def directories(monkeypatch: MonkeyPatch):
    """
    Generates the test directories.

    When one (or Github) runs tests from the terminal, the working directory is set to the project root. However, when
    one runs the tests from an IDE, the working directory is set to 'tests', one level under the root directory. This
    messes up with functions and classes that rely on 'os.curdir' (e.g., ClassFactory), as well as integration tests
    that need to compare contents between directories and files. To make tests work in this situation, we will monkey
    patch 'os.curdir' with 'os.pardir' when the current directory is 'tests'.
    """
    if os.getcwd().endswith('tests'):
        monkeypatch.setattr(os, 'curdir', os.pardir)

    test_dir = os.path.join(os.curdir, 'tests', 'toolkit')
    data_dir = os.path.join(test_dir, 'data')
    target_dir = os.path.join(test_dir, 'target')
    output_dir = os.path.join(test_dir, 'output')

    os.mkdir(output_dir)
    yield data_dir, target_dir, output_dir
    shutil.rmtree(output_dir)
