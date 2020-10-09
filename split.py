import argparse
import re
import os
import json
from matchers import getMatcher


def split(filename: str, out_dir: str, discard_chapters: bool) -> None:
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

    volumes_filename = os.path.join(in_dir, 'volumes.json')
    if os.path.isfile(volumes_filename):
        with open(volumes_filename, 'rt') as f:
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
        volume_name = '正文'  # Default volume name
        curr_dir = os.path.join(out_dir, volume_name)

        # Record the positive ids for duplicate/missing title detection
        # No detection for special titles (those with negative ids)
        volume_ids = set()
        chapter_ids = set()
        curr_volume_id = 0
        curr_chapter_id = 0

        for line in file:
            matched = False
            # First check volume name
            for matcher in volume_matchers:
                status, name, volume_id = matcher.match(line)
                if status:
                    if volume_id in volume_ids:  # duplicate detection
                        print('Potential duplicate volume: {}'.format(name))

                    volume_ids.add(volume_id)

                    if volume_id > 0:
                        if curr_volume_id != 0 and curr_volume_id + 1 != volume_id:  # missing detection
                            print('Potential missing volume: {}'.format(
                                curr_volume_id + 1))

                            curr_volume_id = volume_id

                    # Discard chapter ids between volumes
                    if discard_chapters:
                        chapter_ids.clear()
                        curr_chapter_id = 0

                    volume_name = name
                    curr_dir = os.path.join(out_dir, name)
                    os.mkdir(curr_dir)
                    matched = True
                    break

            if matched:  # Early exit
                continue

            # Then check chapter name
            for matcher in chapter_matchers:
                status, name, chapter_id = matcher.match(line)
                if status:
                    if chapter_id in chapter_ids:  # duplicate detection
                        print('Potential duplicate chapter in volume {}: {}'.format(
                            volume_name, name))

                    chapter_ids.add(chapter_id)

                    if chapter_id > 0:
                        if curr_chapter_id != 0 and curr_chapter_id + 1 != chapter_id:  # missing detection
                            print('Potential missing chapter in volume {}: {}'.format(
                                volume_name, curr_chapter_id + 1))

                        curr_chapter_id = chapter_id

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
                chapter.write(line)
                if line != '\n' and line != '\r\n':
                    chapter.write('\n')

        chapter.close()


if (__name__ == '__main__'):
    parser = argparse.ArgumentParser(
        description='Split ebook file into individual chapters.')
    parser.add_argument('-f', '--filename',
                        help='Filename of the book file.')
    parser.add_argument('-o', '--out_dir', default=None,
                        help='Directory of the output files.')
    parser.add_argument('-d', '--discard_chapters', action='store_true', default=False,
                        help='Set this argument if you want to discard chapter ids between volumes during duplicate/missing chapter detection.')

    args = parser.parse_args()
    split(args.filename, args.out_dir, args.discard_chapters)
