# Reader Tests

For most tests, we will mock `pathlib` to emulate reading. However, for some tests, especially DirectoryReader, mocking is not possible because pydantic checks for `FilePath` and `DirectoryPath` also rely on `pathlib` operations.

As a result, a dedicated `data` directory is created to help with testing.
