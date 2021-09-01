# Project Structure

The entire project is built on the [framework](/framework) composed of 4 files: [Reader](/framework/reader.py), [Processor](/framework/processor.py), [Writer](/framework/writer.py) and [Worker](/framework/worker.py).

If you consider the processes that the toolkit provides -- struct, split, create -- you may find out that they:

- **Read** from a source (be it the source text file, entire directory, novel structures, or a combination of these),
- **Process** the data that has been read,
- and **Write** the processed data to some file(s).

While there can only be one source and one Reader, there can be multiple Processors, in which the data goes through them one by one, and multiple Writers, in which the data is written into different formats. The **Worker** puts them together, creating a full work cycle. This is what the core tool, [**Analyze**](/toolkit/analyze_novel.py), is based on.

Readers and writers are pretty simple; most of the magic happens within the processors. The toolkit needs to recognize, correct, and format the data, so at least three different kinds of processers are needed. They are named **Matcher**, **Validator**, and **Transformer**, respectively.

The data that we will be dealing with can be found [here](common/data.py). It defines all the data types, and the NovelData object that will be passed between all the units.

## Matchers

When we are analyzing the novel, the most important step is to figure out the volume and chapter titles. After we determine the location of these titles, it would be easy to deduce the what the other parts of the novel are. So we will do just that at the very first step with Matchers. Apart from deciding whether the data is a title or not, a Matcher will also assign the title and content (if any) to the title.

Matchers are different from the other two types of processors, in the sense that the data can only have one type. Therefore, an internal [Aggregate Matcher](/processors/matchers/aggregate_matcher.py) is created to short-circuit the matchers if there is a successful match.

There are mainly two ways to determine whether the data is a title:

- By manually matching it against a regular expression;
- By checking it against a list of titles (potentially copied from the web).

For the first method, [Numbered Matcher](/processors/matchers/numbered_matcher.py) is used to match regular titles, and [Special Matcher](/processors/matchers/special_matcher.py) is used to match special titles. For the second method, we have the [CSV Matcher](/processors/matchers/csv_matcher.py).

## Validators

After we get the titles, we need to verify if the indices are correct, i.e., there are no duplicate or missing indices. This is where Validators come in; they keep track of the current index and compares this index against the incoming data's index.

Validators only work on regular titles; special titles do not have indices, so they will always be skipped. Validators are also able to handle different sets of indices by "tagging". You can assign tags to specific titles in the Matchers, and set up separate Validators for these tags.

For volume titles, this is pretty straightforward. Chapter titles are a little bit different. Some books would reset chapter indices when starting a new volume. In this case, the first chapter in every volume is always Chapter 1. Other books will not reset; the first chapter in Volume 2 will be the index of the last chapter in Volume 1 plus 1. So for [Chapter Validator](/processors/validators/chapter_validator.py), there is an additional `discard_chapters` option, compared with [Volume Validator](/processors/validators/volume_validator.py).

## Transformers

Now that we have the correct titles, it is time to

- Figure out the type for the rest of the data;
- Format the title.

For the first process we have [Type Transformer](/processors/transformers/type_transformer.py). It assigns types by looking at where the data is located; if it is before the first volume/chapter title, then it is the book intro; if it is after a volume title but before a chapter title, then it is a volume intro; if it is after a chapter title, then it is a chapter content.

For the second process we have [Title Transformer](/processors/transformers/title_transformer.py). It will filter out the data based on type and tag, and then uses a format string to format the data.

Additionally, if you want to follow the second workflow, i.e., splitting the novel into individual files, you will notice that special titles will lose their original order in the novel, and when you try to generate the structure file, the order of the titles will be incorrect. If you want to avoid this, you can try adding an [Order Transformer](/processors/transformers/order_transformer.py) in between. It will keep the read order, and append that order to the data. You can then use that order as part of the filename.

## Output structures

There are currently two support "structure files": a csv list and a Table of Contents (toc). TOC is more human readable, but lacks a lot of information about the data itself, so it is advised to use csv lists if you can.

## Initializing the units

We will use config files to initialize these units. To extract the fields from the config json efficiently, a utility class [ACC](/common/acc.py) is created. ACC stands for **Argument-Constructed Class**. It will expose a static method called `required_fields`, which would detail all field names, types, default values, and other metadata. This has several uses:

- We can easily extract these fields from an `args` dict when we are initializing the unit;
- We can easily generate documentation using the metadata (see [docgen](/toolkit/generate_docs.py));
- If we want to make a GUI for the toolkit, we can take advantage of these metadata to dynamically generate config form fields.