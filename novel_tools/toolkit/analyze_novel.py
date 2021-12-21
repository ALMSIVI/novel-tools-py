from pathlib import Path
from typing import Optional
from novel_tools.framework import Worker
from novel_tools.processors.matchers.__aggregate_matcher__ import AggregateMatcher
from novel_tools.utils import generate_objects, default_packages


def analyze(config: dict, *, filename: Optional[Path] = None, in_dir: Optional[Path] = None,
            out_dir: Optional[Path] = None):
    """
    Invokes a Worker instance to analyze the novel.

    A typical workflow to process a novel may include:

    1. Generate a structure file from the novel text. You can use `struct_config.json` as a template.
    2. Examine the structure file and scan for any errors or inconsistencies. Correct the structure and/or the novel
       text if necessary.
    3. Use the structure and the novel text, generate a formatted novel file. You can use `create_config.json` as a
       template.

    You can also do the following:

    1. Split the original txt into individual files, and/or structure files. You can use `split_config.json` as a
       template.
    2. Examine the individual files and proofread them. Correct the structure and/or the novel text if necessary.
    3. If you have not generate the structure files at step 1, you can generate the updated structure file based on the
       directory. This can also be useful if you changed so many titles that the original structure file may no longer
       work. You can use `struct_dir_config.json` as a template.
    4. Examine the new structure file and scan for any errors or inconsistencies. Since directories and filenames do not
       preserve their original order in the text file, you might need to shuffle some titles around. Additionally, you
       can include an `OrderTransformer` to record the "internal order" (that does not depend on the Matcher results) in
       the first step, and use that order to name your files.
    5. Use the structure and the individual files, generate a formatted novel file. You can use `create_dir_config.json`
       as a template.

    Args:
        config: The configuration for the Worker instance.
        filename: The novel's filename. If in_dir is not specified, it needs to include the full path. Required if using
                  a Reader that involves reading from a text file.
        in_dir: The input directory holding the novel and/or structure files. If it is not specified, it will use
                filename's directory.
        out_dir: The output directory. Defaults to in_dir.
    """
    if filename is None and in_dir is None:
        raise ValueError('Either filename or in_dir needs to be specified.')

    if in_dir is None:
        in_dir = filename.parent

    additional_args = {
        'in_dir': in_dir,
        'out_dir': out_dir or in_dir
    }

    if filename:
        additional_args['text_filename'] = filename

    objects = generate_objects(config, default_packages, additional_args)
    matcher = AggregateMatcher(objects.get('matchers', []))
    processors = [matcher] + objects.get('validators', []) + objects.get('transformers', [])
    worker = Worker(objects['readers'], processors, objects['writers'])
    worker.work()
