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

After you download the novel, remove the website ads/book name/intro/etc. that are not related to the novel itself, leaving only the volume/chapter names and the contents themselves. Meanwhile, ensure that it is encoded in **utf-8** but not gb2312. You need to convert the encoding if it is.

Then, use `split.py` to break up the chapters. This script can split a single txt file into individual markdown files. The titles will be **h1** and will be placed on the first line of the file. If there are volumes, the script can automatically identify volume names with simple formats, and place chapters of the same volume in separate directories.

For more complicated or irregular volume names, you will need to generate a `volumes.json` to help the script identify the names. The format of the json is as follows:

```json
[
    {
        "name": "the directory of the volume (to be created by the script)",
        "volume": "the name of the volume (to be matched in the text file)"
    },
]
```

After you split the chapters, you need to manually check the table of contents and volume information, to ensure that the number of chapters match the number of files.

If you have irregular volume names that cannot be naturally sorted, you need to sort them manually, by adjusting the order of volumes in `volumes.json`. Since you now have all the volume directories, you can use `generate_order.py` to generate this json automatically.

If you book has volume intros, save them into the volume subdirectories as `_intro.txt`. Since chapters are sorted naturally, this underscore will ensure it will be read first. For book intro, save the `_intro.txt` in the main directory. The concatenate script will collect it if it detects this file.

Even if the novel has no volumes, save all the individual chapters in a subdirectory. It will make your working directory much cleaner, since you separate the metadata and the individual chapter file themselves. Use the command line arguments to skip the volume name when concatenating the novel.

After that you can use `concatenate.py` to merge all the volumes/chapters into a unified Markdown file. 

Now you can import the book into your favorite E-book management software, like Calibre. You can either do this manually or use `add_to_calibre.py` and `calibre_convert.py`. For the two scripts, You will need to download a cover for the book and save it as `cover.jpg`. You also need to manually generate a `metadata.json` file to store the metadata. Here is the template:

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