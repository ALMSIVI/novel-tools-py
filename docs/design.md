# Project Structure

The entire project is built on the [framework](/novel_tools/framework) composed of 5 files: [Novel Data](/novel_tools/framework/data.py), [Reader](/novel_tools/framework/reader.py), [Processor](/novel_tools/framework/processor.py), [Writer](/novel_tools/framework/writer.py) and [Worker](/novel_tools/framework/worker.py).

If you consider the processes that the toolkit provides -- struct, split, create -- you may find out that they:

- **Read** from a source (be it a big text file, or the entire directory consisting of chapter files),
- **Process** the data that has been read,
- and **Write** the processed data to some file(s).

There can be multiple readers, in which the readers are consumed one by one; multiple Processors, in which the data goes through them one by one; and multiple Writers, in which the data is written into different formats. The **Worker** puts them together, creating a full work cycle. This is what the core tool, [**analyze**](/novel_tools/toolkit/analyze_novel.py), is based on.

Readers and writers are pretty simple; most of the magic happens within the processors. The toolkit needs to recognize, correct, and format the data, so at least three different kinds of processors are needed. They are named **Matcher**, **Validator**, and **Transformer**, respectively.

The novel data file contains all the data types, and the NovelData object that will be passed across all the units.

## Matchers

When we are analyzing the novel, the most important step is to figure out the location of volume and chapter titles. After we determine where these titles are, it would be much easier to deduce the types for the rest of the novel. So we will do just that at the very first step. A Matcher, as its name suggests, matches the current data against some predefined title format. Apart from deciding whether the data is a title or not, a Matcher will also parse the title and extract the index, content, and/or affix.

Matchers are different from the other two types of processors, in the sense that the data can only have one type. Therefore, an internal [Aggregate Matcher](/novel_tools/processors/matchers/__aggregate_matcher__.py) is created to short-circuit the matchers if there is a successful match.

There are mainly two ways to determine whether the data is a title:

- By manually matching it against a regular expression;
- By checking it against a list of titles (potentially copied from the web).

For the first method, [Numbered Matcher](/novel_tools/processors/matchers/numbered_matcher.py) is used to match regular titles, and [Special Matcher](/novel_tools/processors/matchers/special_matcher.py) is used to match special titles. For the second method, we have the [CSV Matcher](/novel_tools/processors/matchers/csv_matcher.py).

## Validators

After we get the titles, we need to verify if the indices are correct, i.e., there are no duplicate or missing indices. This is where Validators come in; they keep track of the current index and compares this internal index against the incoming data's index.

Validators only work on regular titles; special titles do not have indices, so they will always be skipped. Validators are also able to handle different sets of indices by "tagging". You can assign tags to specific titles in the Matchers, and set up separate Validators for these tags.

For volume titles, this is pretty straightforward. Chapter titles are a little different. Some books would reset chapter indices when starting a new volume. In this case, the first chapter in every volume is always Chapter 1. Other books will not reset; the first chapter in Volume 2 will be the index of the last chapter in Volume 1 plus 1. So for [Chapter Validator](/novel_tools/processors/validators/chapter_validator.py), there is an additional `discard_chapters` option, compared to [Volume Validator](/novel_tools/processors/validators/volume_validator.py).

## Transformers

Now that we have the correct titles, it is time to

- Figure out the type for the rest of the data;
- Format the title.

For the first process we have [Type Transformer](/novel_tools/processors/transformers/type_transformer.py). It assigns types by looking at where the data is located; if it is before the first volume/chapter title, then it is the book intro; if it is after a volume title but before a chapter title, then it is a volume intro; if it is after a chapter title, then it is a chapter content.

For the second process we have [Title Transformer](/novel_tools/processors/transformers/title_transformer.py). It will filter out the data based on type and tag, and then uses a format string to format the data.

Additionally, if you want to follow the second workflow, i.e., splitting the novel into individual files, you will notice that special titles will lose their original order in the novel, and when you try to generate the structure file, the order of the titles will be incorrect. If you want to avoid this, you can try adding an [Order Transformer](/novel_tools/processors/transformers/order_transformer.py) in between. It will keep the order that is passed in, and append that order to the data. You can then use the order as part of the filename.

If you want to do some batch processing, you can do so with [Pattern Transformer](/novel_tools/processors/transformers/pattern_transformer.py). It will replace patterns in the content with user-defined ones. It could be useful if the author does not use regular punctuation marks, or uses a different format for the divider line.

## Output structures

There are currently two supported "structure files": a csv list and a Table of Contents (toc). TOC is more human-readable, but lacks a lot of information about the data itself, so it is advised to use csv lists when you do the processing.

## Initializing the units

We will use config files to initialize these units. [Pydantic](https://pydantic.dev/) is used to parse these config files.
