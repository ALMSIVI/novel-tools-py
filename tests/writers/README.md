# Writer Tests

During testing, an `output` directory will be created under this one to hold the writer results. The filename and contents will then be verified in the tests.

This is necessary because it is impossible to mock `pathlib`, because `unittest.mock` cannot mock private variables within the `Path` class. 

## Epub Writer

Currently, no tests for [`EpubWriter`](/novel_tools/writers/epub_writer.py) will be provided. While one can verify the contents within an epub using the `zipfile` library, it is still difficult to test many of the options that the writer provides.