## Readers

### CompositeDirectoryReader

**Description:**

Reads from a directory, but uses another reader (csv or toc) to provide the structure (volume/chapter titles).
Additionally, could include a metadata reader for any additional information.
Since the directory doesn't have an explicit structure, the DirectoryReader needs to read everything first before it
can be matched against the structure. This might result in an extended initialization time.
- If csv is used, then it is preferred contain a "raw" column, instead "content".
- If toc is used, then the titles MUST match the directory/file names.

Notice that some arguments from DirectoryReader are not available:
- discard_chapters is not available; this will be automatically inferred from the structure provider.
- read_contents is not available; please use the structure reader directly if you don't want the contents.

**Arguments:**
- in_dir (str): The working directory. Should also include the structure file and the metadata file, if specified.
- structure (str): Structure provider. Currently supported structures are 'csv' and 'toc'.
- metadata (str | bool, optional, default=False): If it is not specified or False, then no metadata will be read. If it is True, then the reader will use the default filename (specified in the reader). If it is a string, then the filename will be provided to the reader.
- encoding (str, optional, default=utf-8): Encoding of the chapter/structure/metadata files.
- intro_filename (str, optional, default=_intro.txt): The filename of the book/volume introduction file(s).
- default_volume (str, optional, default=None): If the novel does not have volumes but all chapters are stored in a directory, then the variable would store the directory name.
- csv_filename (str, optional, default=list.csv): Filename of the csv list file. This file should be generated from `CsvWriter`, i.e., it must contain at least type, index and content.
- toc_filename (str, optional, default=toc.txt): Filename of the toc file. This file should be generated from `TocWriter`.
- has_volume (bool): Specifies whether the toc contains volumes.
- discard_chapters (bool): If set to True, will start from chapter 1 again when entering a new volume.

### CompositeTextReader

**Description:**

Reads from a text file, but uses another reader (csv or toc) to provide the structure (volume/chapter titles).
Additionally, could include a metadata reader for any additional information.
Since the text file has a natural order, a TextReader will be used.
- If csv is used, then it is preferred to contain either a "raw" column or a "line_num" column.
- If toc is used, then it is preferred to contain line numbers.

Notice that, unlike CompositeDirectoryReader, this reader will not not assign types other than titles. Consider
pairing this with a TypeTransformer in order to get detailed types.

Notice that some arguments from TextReader are not available:
- verbose is not available; raw and line_num are needed to effectively matched against the structure data.

**Arguments:**
- in_dir (str, optional): The directory to read the text file, structure file and metadata file (if it exists) from. Required if any of these filenames does not contain the path.
- structure (str): Structure provider. Currently supported structures are 'csv' and 'toc'.
- metadata (str | bool, optional, default=False): If it is not specified or False, then no metadata will be read. If it is True, then the reader will use the default filename (specified in the reader). If it is a string, then the filename will be provided to the reader.
- encoding (str, optional, default=utf-8): Encoding of the chapter/structure/metadata files.
- text_filename (str, optional, default=text.txt): Filename of the text file.
- csv_filename (str, optional, default=list.csv): Filename of the csv list file. This file should be generated from `CsvWriter`, i.e., it must contain at least type, index and content.
- toc_filename (str, optional, default=toc.txt): Filename of the toc file. This file should be generated from `TocWriter`.
- has_volume (bool): Specifies whether the toc contains volumes.
- discard_chapters (bool): If set to True, will start from chapter 1 again when entering a new volume.

### CsvReader

**Description:**

Recovers the novel structure from the csv list.

**Arguments:**
- csv_filename (str, optional, default=list.csv): Filename of the csv list file. This file should be generated from `CsvWriter`, i.e., it must contain at least type, index and content.
- in_dir (str, optional): The directory to read the csv file from. Required if the filename does not contain the path.
- encoding (str, optional, default=utf-8): Encoding of the csv file.

### DirectoryReader

**Description:**

Reads from a directory structure. This directory should be generated from FileWriter, as it will follow certain
conventions, such as the first line of the chapter file being the title.

**Arguments:**
- in_dir (str): The working directory.
- read_contents (bool): If set to True, will open the files to read the contents.
- discard_chapters (bool): If set to True, will start from chapter 1 again when entering a new volume.
- default_volume (str, optional, default=None): If the novel does not have volumes but all chapters are stored in a directory, then the variable would store the directory name.
- intro_filename (str, optional, default=_intro.txt): The filename of the book/volume introduction file(s).
- encoding (str, optional, default=utf-8): Encoding of the chapter file(s).

### MetadataJsonReader

**Description:**

Reads a json that contains the metadata of the book file. Will only generate a BOOK_TITLE, with the others field
populated with the other metadata.

**Arguments:**
- metadata_filename (str, optional, default=metadata.json): Filename of the metadata json file. The metadata MUST contain a 'title' field.
- in_dir (str, optional): The directory to read the metadata file from. Required if the filename does not contain the path.
- encoding (str, optional, default=utf-8): Encoding of the json file.

### TextReader

**Description:**
Reads from a plain text file.
**Arguments:**
- text_filename (str, optional, default=text.txt): The filename of the text.
- in_dir (str, optional): The directory to read the text file from. Required if the filename does not contain the path.
- encoding (str, optional, default=utf-8): The encoding of the file.
- verbose (bool, optional, default=False): If set to True, additional information, including line number and raw line info, will be added to the data object.

### TocReader

**Description:**
Reads from a table of contents (toc) file.
**Arguments:**
- toc_filename (str, optional, default=toc.txt): Filename of the toc file. This file should be generated from `TocWriter`.
- in_dir (str, optional): The directory to read the toc file from. Required if the filename does not contain the path.
- encoding (str, optional, default=utf-8): Encoding of the toc file.
- has_volume (bool): Specifies whether the toc contains volumes.
- discard_chapters (bool): If set to True, will start from chapter 1 again when entering a new volume.

## Matchers

### CsvMatcher

**Description:**

Accepts a line and matches titles by a given csv list. This matcher can be used in cases where the titles are
irregular or do not have an explicit index. Examples include "Volume 12.5" or "Tales of the Wind".
This does not have to be the list file generated from a CsvWriter; one might copy and paste the list from a website
without the type of the content. Therefore, one of the following fields is required to determine the type.

To determine the type of the line, the following three checks are done in order:
- If the csv list contains a "type" field, then it will be used;
- If a type is specified in the args, then all lines will be set to that specific type;
- If a regex is specified in the args, then the title will be matched against the regexes;
- If none of these is in the arguments, then an exception will be raised during construction.

An object in the list consists of 3 fields:
- type (optional): Type of the title,
- raw: Raw title (to be matched against),
- formatted (optional): Formatted title. If it is not present, the raw title will be used.

**Arguments:**
- csv_filename (str, optional, default=list.csv): Filename of the csv list file.
- in_dir (str, optional): The directory to read the csv file from. Required if the filename does not contain the path.
- encoding (str, optional, default=utf-8): Encoding of the csv list file.
- type (str, optional): If present, specifies the type of all the matches.
- regex (dict[str, str], optional): If present, specifies the regexes for each type.

### NumberedMatcher

**Description:**
Accepts a line in a book and matches a regular chapter/volume, with an index and/or a title.
**Arguments:**
- type (str): Specifies the type for this matcher.
- regex (str): The regex to match for. It will contain two groups: the first group is the index, the second (optional) is the title.
- index_group (int, optional, default=0): The group index for the title's order/index (starting from 0).
- content_group (int, optional, default=1): The group index for the title's content (starting from 0).
- tag (str, optional, default=None): The tag to append to matched data. Sometimes there may exist several independent sets of indices within the same book; for example, there might be two different Introductions by different authors before the first chapter, or there might be several interludes across the volume. In such case, one can attach a tag to the data, and have a special Validator that only checks for that tag.

### SpecialMatcher

**Description:**

Accepts a line in a book and matches a special title, whose affixes are in the given list. Examples of special
titles include Introduction, Foreword, or Conclusion.

As they usually don't have a regular index, they will be assigned negative values, depending on their order in the
list. The use of negative values is to avoid collision with regular titles in validators. Additionally, an "affix"
field will be attached to the object.

**Arguments:**
- type (str): Specifies the type for this matcher.
- affixes (list[str]): List of special names to match for.
- regex (str): The regex to match for. It will contain a "affixes" format, that will be replaced with the list of affixes. Example: ^{affixes}$ will match lines with any of the affixes.
- affix_group (int, optional, default=0): The group index for the title's affix (starting from 0).
- content_group (int, optional, default=1): The group index for the title's content (starting from 0).
- tag (str, optional, default=special): The tag to append to matched data. This can be used in TitleValidator for different formats.

## Validators

### Validator

**Description:**

Validates whether the title indices are continuous, i.e., whether there exist duplicate of missing chapter indices.

**Arguments:**
- overwrite (bool, optional, default=True): If set to True, will overwrite the old index with the corrected one, and keep the original index in the 'original_index' field. If set to False, the corrected index will be stored in the 'corrected_index' field. In either case, a field called 'error' will be created if a validation error occurs.
- tag (str, optional, default=None): Only validate on the given tag. Sometimes there may exist several independent sets of indices within the same book; for example, there might be two different Introductions by different authors before the first chapter, or there might be several interludes across the volume. In such case, one can attach a tag to the data, and have a special Validator that only checks for that tag.

## Transformers

### OrderTransformer

**Description:**

Assigns an order to the data. This could be useful for file writers, since the filenames won't keep the original
order of reading. For example, one can append this order before all volume and chapter filenames to maintain
ordering.

**Arguments:**


### TitleTransformer

**Description:**

Formats the title, using the necessary information in the data.

To reduce the number of required transformers, this class will use a list of "unit" processors. Each unit contains a
"filter" and one or two format strings. One can filter based on any attribute of the given data, the most important
of which include type and tag. If one format string is given, then it will be used to fill the "formatted" field. If
a dict is given, then it will use the values to fill the custom key fields.

Be careful if you want to use this on non-title data, for most writers use 'formatted' to determine whether the data
is a title.

**Arguments:**
- units (list[{filter: dict[str, str], format: str | dict[str, str]}]): The list of processing units. The filter is a dictionary with the fields as the key. The format can be either a string or a dict containing the format strings for each custom field. Please put the units with the most specific filters first, and leave the most generic last, to avoid short circuiting.

### TypeTransformer

**Description:**
Determines the true type for all data with UNRECOGNIZED type.
**Arguments:**


## Writers

### CsvWriter

**Description:**

Generates a volume/chapter list as a csv file.
It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled.

**Arguments:**
- csv_filename (str, optional, default=list.csv): Filename of the output csv file.
- out_dir (str): The directory to write the csv file to.
- additional_fields (list[str], optional, default=[]): Specifies additional fields to be included to the csv file.

### DirectoryWriter

**Description:**

Generates volume directories and chapter files. If there is no volume, a default volume will be created.
It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled. One
can also use the same transformer to attach a 'filename' field, and the writer will prioritize this field.

**Arguments:**
- out_dir (str): The working directory.
- debug (bool, optional, default=False): If set to True, will print the error message to the terminal.
- default_volume (str, optional, default=default): If the volume doesn't have volumes, specify the directory name to place the chapter files.
- intro_filename (str, optional, default=_intro.txt): The filename of the book/volume introduction file(s).
- write_blank (bool, optional, default=True): If set to True, will write blank lines to the files. Sometimes blank lines serve as separators in novels, and we want to keep them.

### MarkdownWriter

**Description:**

Writes the entire novel to a Markdown file.
If a title field has been passed from a TitleTransformer and has the 'formatted' field filled, then the field will
be prioritized.

**Arguments:**
- md_filename (str, optional, default=text.md): Filename of the output Markdown file, if use_title is False.
- out_dir (str): The directory to write the markdown file to.
- use_title (bool): If set to True, will use the book title (if specified) as the Markdown filename.
- levels (dict[str, int], optional, default={'book_title': 1, 'volume_title': 2, 'chapter_title': 3}): Specifies what level the header should be for each type.
- write_blank (bool, optional, default=True): If set to True, will write blank lines to the files. Sometimes blank lines serve as separators in novels, and we want to keep them.
- debug (bool, optional, default=False): If set to True, will print the error message to the terminal.

### TocWriter

**Description:**

Lists the table of contents without actually splitting the file. Useful for debugging.
If out_dir is empty, the table will be printed to the terminal.
It is assumed that the title data has been passed from a TitleTransformer and has the 'formatted' field filled.

**Arguments:**
- toc_filename (str, optional, default=toc.txt): Filename of the output toc file.
- out_dir (str): The directory to write the toc file to.
- debug (bool, optional, default=False): If set to True, will write error information to the table of contents.

