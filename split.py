import argparse
import re
import os
import json
from matchers import getMatcher, Matcher, MatchResult
from validators import VolumeValidator, ChapterValidator


def generate_matchers(in_dir: str):
    matcher_filename = os.path.join(in_dir, 'matchers.json')
    if not os.path.isfile(matcher_filename):
        matcher_filename = os.path.join(os.curdir, 'default_matchers.json')

    with open(matcher_filename, 'rt') as f:
        matchers = json.load(f)

    # Check if we need custom volume matchers
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

    return volume_matchers, chapter_matchers


def split(filename: str, out_dir: str, discard_chapters: bool) -> None:
    '''
    Split a whole txt file into individual chapters, with possible volume subdirectories.
    The input file is default to utf8 encoding. If it is encoded in GB2312 you need to convert it first.
    Ensure that the file starts directly with a volume/chapter name, without anything else.
    '''

    in_dir = os.path.dirname(filename)

    if out_dir is None:
        out_dir = in_dir

    volume_matchers, chapter_matchers = generate_matchers(in_dir)

    with open(filename, 'rt', encoding='utf8') as file:
        chapter = None
        curr_dir = os.path.join(out_dir, '正文')  # Default volume name

        # Create chapter and volume validators
        volume_validator = VolumeValidator()
        chapter_validator = ChapterValidator()

        for line in file:
            line = line.strip()
            matched = False
            # First check volume name
            for matcher in volume_matchers:
                result = matcher.match(line)
                if result.status:
                    volume_validator.validate(matcher, result)

                    curr_dir = os.path.join(out_dir, matcher.filename(result))
                    if not os.path.isdir(curr_dir):
                        os.mkdir(curr_dir)

                    # Discard chapter ids between volumes
                    if discard_chapters:
                        chapter_validator.clear()

                    chapter_validator.curr_volume = matcher.format(result)

                    if chapter is not None:
                        chapter.close()  # Close current chapter
                        chapter = None

                    matched = True
                    break

            if matched:  # Volume matched, go to next line
                continue

            # Then check chapter name
            for matcher in chapter_matchers:
                result = matcher.match(line)
                if result.status:
                    chapter_validator.validate(matcher, result)

                    # Close previous chapter file
                    if chapter is not None:
                        chapter.close()
                    if not os.path.isdir(curr_dir):
                        os.mkdir(curr_dir)

                    chapter = open(os.path.join(
                        curr_dir, matcher.filename(result) + '.md'), 'w', encoding='utf8')
                    chapter.write('# ' + matcher.format(result) + '\n')
                    matched = True
                    break

            # Regular line
            if chapter is not None and not matched:
                chapter.write(line)
                if line != '':
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
