## Readers

### CsvReader

**Description:**

Recovers the novel structure from the csv list. The csv is required to contain a "content" column, but it does not
have to contain the other fields from a NovelData.

**Arguments:**
- csv_filename (str, optional, default=list.csv): Filename of the csv list file. This file should be generated from `CsvWriter`, i.e., it must contain at least type, index and content.
- in_dir (str, optional): The directory to read the csv file from. Required if the filename does not contain the path.
- encoding (str, optional, default=utf-8): Encoding of the csv file.
- types (dict, optional, default={'line_num': 'int'}): Type of each additional field to be fetched. Currently str, int and bool are supported.

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

Matches data by a given csv list. This matcher can be used in cases where the titles are irregular or do not have
an explicit index. Examples include "Volume 12.5" or "Tales of the Wind".

This csv file does not have to be generated from a CsvWriter; one might copy and paste the list from a website
without the type of the content. In such cases, it might not contain certain fields, such as `line_num` or `type`.
Therefore, we will set up some rules to match the content and determine the type of the data:

To make a successful match, the user will specify a list of fields to compare. The Matcher will return True if one
of the fields matches.

To determine the type of the line, the following three checks are done in order:
- If the csv list contains a "type" field, then it will be used;
- If a type is specified in the args, then all lines will be set to that specific type;
- If none of these is in the arguments, then an exception will be raised during construction.

**Arguments:**
- csv_filename (str, optional, default=list.csv): Filename of the csv list file.
- in_dir (str, optional): The directory to read the csv file from. Required if the filename does not contain the path.
- encoding (str, optional, default=utf-8): Encoding of the csv list file.
- types (dict, optional, default={'line_num': 'int'}): Type of each additional field to be fetched. Currently str, int and bool are supported.
- data_type (str, optional): If present, specifies the type of all the titles.
- fields (list[str], optional, default=['line_num', 'formatted', 'raw', 'content']): The fields to compare to when matching.

### NumberedMatcher

**Description:**
Matches a regular chapter/volume, with an index and/or a title.
**Arguments:**
- type (str): Specifies the type for this matcher.
- regex (str): The regex to match for. It will contain two groups: the first group is the index, the second (optional) is the title.
- index_group (int, optional, default=0): The group index for the title's order/index (starting from 0).
- content_group (int, optional, default=1): The group index for the title's content (starting from 0). Use 0 if there is no content, in which case the entire title will be used as content.
- tag (str, optional, default=None): The tag to append to matched data. Sometimes there may exist several independent sets of indices within the same book; for example, there might be two different Introductions by different authors before the first chapter, or there might be several interludes across the volume. In such case, one can attach a tag to the data, and have a special Validator that only checks for that tag.

### SpecialMatcher

**Description:**

Matches a special title, whose affixes are in the given list. Examples of special
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

### TocMatcher

**Description:**

Matches data by a given Table of Contents (TOC) file. It is not advised to use toc files as a matcher; while the
file is better human readable, it contains less information than csv files and will not provide as many options as
a csv file does.

**Arguments:**
- toc_filename (str, optional, default=toc.txt): Filename of the toc file. This file should be generated from `TocWriter`.
- in_dir (str, optional): The directory to read the toc file from. Required if the filename does not contain the path.
- encoding (str, optional, default=utf-8): Encoding of the toc file.
- has_volume (bool): Specifies whether the toc contains volumes.
- discard_chapters (bool): If set to True, will start from chapter 1 again when entering a new volume.

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

This class uses a list of "unit" processors. Each unit contains a "filter" and one or two format strings. One can
filter based on any attribute of the given data, the most important of which include type and tag. If one format
string is given, then it will be used to fill the "formatted" field. If a dict is given, then it will use the values
to fill the custom key fields.

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

