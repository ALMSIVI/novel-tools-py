# Tests for analyze

Tests for `analyze` will be written as integration tests instead of unit tests because the function:

- is basically a Worker instance consisting of a Reader, one or several Processors, and one or several Writers. This
  composition makes it hard to write unit tests;
- involves a large number of I/O operations that would be a nightmare to mock one by one.

These integration tests demonstrate what kinds of input it can handle and what outputs it can generate. You can take a
look at the test inputs under the `data` directory, and use them as examples to make your own configs.