# Tests for analyze

Tests for `analyze` will be written as integration tests instead of unit tests because the function:

- is basically a Worker instance consisting of a Reader, one or several Processors, and one or several Writers. This composition makes it hard to write unit tests;
- involves a large number of I/O operations that would be a nightmare to mock one by one.

These integration tests demonstrate what kinds of input it can handle and what outputs it can generate. You can take a look at the test inputs under the `data` directory, and use them as examples to make your own configs.

For each novel, 

- Start from the `.txt` file. This is the source file that is unformatted and may contain errors in the title. 
- Then, take a look at the config `json` files to understand what each config means. Refer to [built-in class references](/docs/references.md) if you are confused about some particular setting. 
- After that, read through the structure files, either `list.csv` or `toc.txt`, to see if they make sense and if they match your expectations.
- Finally, take a look at the resulting `.md` file. This is a formatted Markdown file that marks all titles. These markdown files can be added directly to [Calibre](https://calibre-ebook.com/) and converted into epub.