# Novel tools

## Why am I doing this

First I want to affirm that I do not support piracy. Please subscribe to the novels on their official websites/apps if possible. My tools are mainly used on novels that I subscribed.

However, websites like Qidian would censor some/all chapters of a novel, which is detrimental to reading. I have to rely on txt versions from the Internet. Plain text files have no format, and while some apps could auto match chapter names and generate a table of contents, some questions linger:

- No support for custom/irregular volume/chapter names;

- There might be duplicate or missing chapter numbering;

- The format of the chapter name might vary.

This is unacceptable if you want to put the novel to your collection. All novels have their unique problems and a universal script will never be developed to suit every need, but at least I can write something to automatically split them into individual chapters and then manually proofread them.

## Additional Libraries

You need `natsort` to sort the Chinese volume/chapter names.

```shell
pip install natsort
```

## Usage

- All scripts use `argparse`，so you can use the argument `-h` to refer to individual usages.

After you download the novel, remove the website ads/book name/intro/etc. that are not related to the novel itself, leaving only the volume/chapter names and the contents themselves. Meanwhile, ensure that it is encoded in **utf-8** but not gb2312. You need to convert the encoding if it is.

Then, use `split.py` to break up the chapters. This script can split a single txt file into individual markdown files. The titles will be **h1** and will be placed on the first line of the file. If there are volumes, the script can identify volume names with simple formats, and place chapters of the same volume in separate directories.

After you split the chapters, you need to manually check the table of contents and volume information, to ensure that the number of chapters match the number of files.

If you have irregular volume names that cannot be naturally sorted, you need to sort them manually. For this, a separate file is need to record your volume order. Use `generate_order.py` to generate a template file `order.json`, and then sort the volumes manually.

If there are no volumes, use `concatenate.py` to merge them into a unified Markdown file. If there are volumes, use `concatenate_volume.py` to merge them into a Markdown file with two layers of contents.

Then, you could import your novel into e-book management apps such as Calibre. You may convert it into epub format which is more suitable for e-ink devices.
