# Novel tools

## Why am I doing this

First I want to affirm that I do not support piracy. Please subscribe to the novels on their official websites/apps if possible. My tools are mainly used on novels that I subscribed.

However, websites like Qidian would censor some/all chapters of a novel, which is detrimental to a smooth reading experience. When this happens, one has to rely on txt versions from the Internet. Plain text files have no format, and if you want a quick read, that would be fine. However, once you want to compile it into a format that is more friendly to e-readers (like epub), problems arise. While some apps could auto match chapter names and generate a table of contents, some questions linger:

- No support for custom/irregular volume/chapter names;

- There might be duplicate or missing chapter numbers;

- The format of the chapter name might vary.

This is unacceptable if you want to put the novel to your collection. All novels have their unique problems and there is unlikely that a universal script would suit every need, but at least I can write something to automatically split them into individual chapters and then manually proofread them.

## Dependencies

You need `natsort` to sort the numbers in natural order (1, 2, ... 10, 11 instead of 1, 10, 11, ... 2).

```shell
pip3 install natsort
```

## Usage

- All scripts use `argparse`，so you can use the argument `-h` to refer to individual usages.

After you download the novel, remove the website ads/book name/intro/etc., leaving only the volume/chapter names and the contents themselves. Meanwhile, ensure that it is encoded in **utf-8** but not gb2312.

### Splitting the text file

First, use `split.py` to break up the volumes and chapters within the txt file. If there are no volumes, all chapters will be output to a default main volume. It will also detect duplicate or missing volume/chapter names, and output them on the console. You can either use the `-c` command to have it automatically correct for you, or you can manually adjust the volume/chapter names based on the output.

Here is its usage:

```shell
python3 split.py -f FILENAME [-o OUT_DIR] [-d] [-c] [-h]
```

`-f` is the name of the book file and is required. The others are optional parameters. `-o` specifies the output directory and defaults to the book's directory; `-d` controls the title detection module whether to discard chapter ids between novels. Some novels will number their chapters continuously, while some would restart at Chapter 1 at the beginning of every volume. `-c` controls whether you want to automatically correct duplicate/missing indices.

`split.py` identifies volume and chapter names through different **Matchers**. During splitting, each line is passed into all the defined matchers, which will try to extract two parts: "index" and "title".

- For example, for the line "Chapter 5. A New Dawn", a properly configured `NumberedMatcher` will extract the index "5" (as an integer) and the title will be"A New Dawn".

Matchers also define two additional methods:

- `format()` takes a match result (index and title), and reformats the chapter/volume name. This is particularly useful for auto correction, where one needs to adjust the index due to duplicate/missing indices.
- `filename()` takes a match result (index and title), and outputs a valid filename. A bare-bones implementation would be to remove all illegal character names in the string returned by `format()`.

There are three default Matcher implementations right now, though you are welcome to add more for your own needs. When `split.py` runs, it will fetch `Matcher`s and their arguments from `default_matchers.json` from the working directory. If you need a to customize your matchers for a specific novel, you can copy the file to the novel's directory, rename it to `matchers.json` and then modify it. The script will automatically find this file and create the corresponding `Matcher`s.

- `NumberedMatcher`: matches the given regular expression, identifies the number in the chapter name, and converts Chinese numbering to arabic numerals (to improve sorting). The json specification is as follows:

```json
{
    "class": "NumberedMatcher", // Used by the script
    "regex": "^Chapter\s+(.+)\.(.+)$", // Requires two groups, first is index, second is title
    "format": "Chapter {index}. {title}", // You don't need both index and title
}
```

- `SpecialMatcher`: matches the given list of special prefixes, like "Intro" and "Epilogue". Once you specify the list of prefixes, the script will assign a negative index for each prefix (to avoid confusion with regular volume/chapters). Volumes/chapters with negative indices will **NOT** be validated or corrected even you have the `-c` option. The json specification is as follows:

```json
{
    "class": "SpecialMatcher", // Used by the script
    "prefixes": ["Intro", "Introduction", "Epilogue", "Afterword"],
    "regex": "^{prefixes}\.(.+)$", // The script will automatically generate the regex for prefixes, so you only need to group the title
    "format": "{prefix}. {title}", // You don't need both prefix and title
}
```

- `VolumeMatcher`: matches irregular volume names. You are not supposed to create this Matcher yourself; instead, you will create a `volumes.json` in the same directory as the novel's text file, and the script will automatically generate a Matcher.  When `volumes.json` is present, the script will **ignore** all default and/or user-defined volume Matchers. Below is the specification for a volume:

```json
[
    {
        "name": "the directory name for the volume", // to be created by the script
        "volume": "the name of the volume", // to be matched in the text file
        "volume_formatted": "Formatted volume title" // optional
    },
]
```

If you have semi-regular volume names that would could be matched, but would still require manual sorting, then you can first run `split.py` to create all volume directories, and then use `generate_order.py` to generate this json automatically. This script accepts a `-d` argument that specifies the root directory for all volume subdirectories. If you have irregular volume names or natural sort order does not apply, you need to manually generate `volumes.json` and sort the volumes.

-----

If you book has volume intros, save them into the volume subdirectories as `_intro.txt`. Since chapters are sorted naturally, this underscore will ensure it will be read first when being concatenated. For book intro, save the `_intro.txt` in the main directory. The concatenate script will collect it if it detects this file.

### Concatenate the volumes/chapters

After that, you can use `concatenate.py` to merge all the volumes/chapters into a unified Markdown file. 

Here is its usage:

```shell
python3 concatenate.py -i IN_DIR [-o OUT_DIR] [-t TITLE_HEADING] [-v VOLUME_HEADING] [-c CHAPTER_HEADING] [-a]
```

`-i` is the book's directory and is required, while the rest are optional. `-o` specifies the output directory and defaults to the book's directory; `-t`, `-v` and `-c` specifies the title format (h1-h6) of the book, volumes, and chapters, respectively; `-a` lets you control if the volume titles need to be added to the concatenated file. If there is no volume in the title, and the entire book is stored in the main directory, you can use this option. 

**Notice**: after you use this option, all chapter headings will be elevated by one level.

### Convert and add to Calibre

Now you can import the book into your favorite E-book management software, like Calibre. You can either do this manually or use `add_to_calibre.py` and `calibre_convert.py`. The two scripts accept a `-d` argument that specifies the book's directory. For the two scripts, You will need to download a cover for the book and save it as `cover.jpg`. You also need to manually generate a `metadata.json` file to store the metadata. Here is the template:

```json
{
    "title": "My Favorite Book",
    "author": "Best author in the world",
    "id": "isbn:1234567890",
    "tags": ["Fiction"],
    "publisher": "Hello World",
    "languages": ["English"]
}
```