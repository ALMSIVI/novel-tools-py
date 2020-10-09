# Novel tools

## Why am I doing this

First I want to affirm that I do not support piracy. Please subscribe to the novels on their official websites/apps if possible. My tools are mainly used on novels that I subscribed.

However, websites like Qidian would censor some/all chapters of a novel, which is detrimental to reading. I have to rely on txt versions from the Internet. Plain text files have no format, and while some apps could auto match chapter names and generate a table of contents, some questions linger:

- No support for custom/irregular volume/chapter names;

- There might be duplicate or missing chapter numbers;

- The format of the chapter name might vary.

This is unacceptable if you want to put the novel to your collection. All novels have their unique problems and it is unlikely that a universal script will be developed to suit every need, but at least I can write something to automatically split them into individual chapters and then manually proofread them.

## Additional Libraries

You need `natsort` to sort the numbers in natural order (1, 2, ... 10, 11 instead of 1, 10, 11, ... 2).

```shell
pip3 install natsort
```

## Usage

- All scripts use `argparse`，so you can use the argument `-h` to refer to individual usages.

After you download the novel, remove the website ads/book name/intro/etc., leaving only the volume/chapter names and the contents themselves. Meanwhile, ensure that it is encoded in **utf-8** but not gb2312.

-----

Then, use `split.py` to break up the volumes and chapters within the txt file. If there are no volumes, all chapters will be output to a default main volume. It will also detect duplicate or missing volume/chapter names, and output them on the console. You can adjust the volume/chapter names based on the output.

Here is its usage:

```shell
python3 split.py -f FILENAME [-o OUT_DIR] [-d]  [-h]
```

`-f` is the name of the book file and is required. `-o` specifies the output directory and defaults to the book's directory; `-d` controls the title detection module whether to discard chapter ids between novels. Some novels will number their chapters continuously, while some would restart at Chapter 1 at the beginning of every volume.

`split.py` identifies volume and chapter names through different `Matcher`s. There are three `Matcher`s right now:

- `NumberedMatcher`: matches the given regular expression, identifies the number in the chapter name, and converts Chinese numbering to arabic numerals.

- `SpecialMatcher`: matches the given list of special names, like "Intro" and "Epilogue".

- `VolumeMatcher`: matches irregular volume names. You will need to generate a `volumes.json` to help the script identify the names. The format of the json is as follows:

```json
[
    {
        "name": "the directory of the volume (to be created by the script)",
        "volume": "the name of the volume (to be matched in the text file)"
    },
]
```

If you have semi-regular volume names that would still require manual sorting, then you can first run `split.py` to create all volume directories, and then use `generate_order.py` to generate this json automatically. This script accepts a `-d` argument that specifies the root directory for all volume subdirectories. If you have irregular volume names or naturla sort order does not apply, you need to manually generate `volumes.json` and sort the volumes.

-----

You can refer to `matchers.py` to create custom `Matcher`s. All `Matcher`s accept an `args` statement, and checks whether the line is a volume/chapter name with the `match()` method.

The script will fetch `Matcher`s and their arguments from `default_matchers.json`. If you need a more complicated setup, you can copy the file to the novel's directory, rename it to `matchers.json` and then modify it. The script will automatically find this file and create the corresponding `Matcher`s.

-----

If you book has volume intros, save them into the volume subdirectories as `_intro.txt`. Since chapters are sorted naturally, this underscore will ensure it will be read first when being concatenated. For book intro, save the `_intro.txt` in the main directory. The concatenate script will collect it if it detects this file.

----

After that, you can use `concatenate.py` to merge all the volumes/chapters into a unified Markdown file. 

Here is its usage:

```shell
python3 concatenate.py -i IN_DIR [-o OUT_DIR] [-t TITLE_HEADING] [-v VOLUME_HEADING] [-c CHAPTER_HEADING] [-a]
```

`-i` is the book's directory and is required, while the rest are optional. `-o` specifies the output directory and defaults to the book's directory; `-t`, `-v` and `-c` specifies the title format (h1-h6) of the book, volumes, and chapters, respectively; `-a` lets you control if the volume titles need to be added to the concatenated file. If there is no volume in the title, and the entire book is stored in the main directory, you can use this option. **Notice**: after you use this option, all chapter headings will be elevated by one level.

-----

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