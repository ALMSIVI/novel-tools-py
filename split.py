import argparse
import re
import os
import json
from matchers import getMatcher


def split(filename: str, sort_volume: bool, out_dir: str) -> None:
    '''
    Split a whole txt file into individual chapters, with possible volume subdirectories.
    The input file is default to utf8 encoding. If it is encoded in GB2312 you need to convert it first.
    Ensure that the file starts directly with a volume/chapter name, without anything else.
    '''

    in_dir = os.path.dirname(filename)

    if out_dir is None:
        out_dir = in_dir

    # Generate all matchers
    matcher_filename = os.path.join(in_dir, 'matchers.json')
    if not os.path.isfile(matcher_filename):
        matcher_filename = os.path.join(os.curdir, 'default_matchers.json')

    with open(matcher_filename, 'rt') as f:
        matchers = json.load(f)

    if sort_volume:
        with open(os.path.join(in_dir, 'volumes.json'), 'rt') as f:
            volumes = json.load(f)
            volume_matchers = [getMatcher(
                'VolumeMatcher', {'volumes': volumes})]
    else:
        volume_matchers = [getMatcher(matcher['class'], matcher)
                           for matcher in matchers['volumes']]

    chapter_matchers = [getMatcher(matcher['class'], matcher)
                        for matcher in matchers['chapters']]

    with open(filename, 'rt', encoding='utf8') as file:
        chapter = None
        curr_dir = os.path.join(out_dir, '正文')  # default volume name
        for line in file:
            matched = False
            # First check volume name
            for matcher in volume_matchers:
                status, name = matcher.match(line)
                if status:
                    curr_dir = os.path.join(out_dir, name)
                    os.mkdir(curr_dir)
                    matched = True
                    break

            if matched:
                continue

            # Then check chapter name
            for matcher in chapter_matchers:
                status, name = matcher.match(line)
                if status:
                    # Close previous chapter file
                    if chapter is not None:
                        chapter.close()
                    if not os.path.isdir(curr_dir):
                        os.mkdir(curr_dir)

                    chapter = open(os.path.join(
                        curr_dir, name + '.md'), 'w', encoding='utf8')
                    chapter.write('# ' + line + '\n')
                    matched = True
                    break

            # Regular line
            if chapter is not None and not matched:
                chapter.write(line + '\n')

        chapter.close()


if (__name__ == '__main__'):
    parser = argparse.ArgumentParser(
        description='Split ebook file into individual chapters.')
    parser.add_argument('-f', '--filename',
                        help='Filename of the book file.')
    parser.add_argument('-s', '--sort_volume', action='store_true', default=False,
                        help='Whether volumes.json will be used to detect custom volumes. By default, regular volume names will be supported.')
    parser.add_argument('-o', '--out_dir', default=None,
                        help='Directory of the output files.')

    args = parser.parse_args()
    split(args.filename, args.sort_volume, args.out_dir)
