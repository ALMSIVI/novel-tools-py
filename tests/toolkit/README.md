# Toolkit tests

Most Toolkit functions (excluding those that interact with Calibre):
- are basically a Worker instance consisting of a Reader, one or several Processors, and one or several Writers. This composition makes it hard to write unit tests;
- involve a large number of I/O operations that would be a nightmare to mock one by one.

Due to these limitations, all toolkits that involve framework classes will be written as integration tests instead of unit tests.

These integration tests demonstrate what each tool is about, and what kind of inputs it can handle. Take a look at the test inputs, change some of the configs, and play with them!
- All test inputs will be put under the `data` directory;
- All target files (will be compared against the output) will be put under the `target` directory;
- All test outputs will go to `output`. After each integration test, the output directory will be removed.