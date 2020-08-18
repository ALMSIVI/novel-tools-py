import argparse
import re
import os
import json

# Chinese to Arabic number correspondings
num_dict = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
            '七': 7, '八': 8, '九': 9, '十': 10, '廿': 20, '卅': 30, '卌': 40, '百': 100, '千': 1000, '两': 2}
# Invalid filename format
valid_filenames = dict((ord(char), None) for char in '\/*?:"<>|')


def toNum(num: str) -> int:
    '''
    Converts a chinese string to a number.
    '''

    try:
        value = int(num)
    except:
        value = 0
        digit = 1

        for i in range(len(num)):
            v = num_dict[num[i]]
            if v >= 10:
                digit *= v
                value += digit
            elif i == len(num) - 1:
                value += v
            else:
                digit = v

    return value


def split(filename: str, sort_volume: bool, out_dir: str) -> None:
    '''
    Split a whole txt file into individual chapters, with possible volume subdirectories.
    The input file is default to utf8 encoding. If it is encoded in GB2312 you need to convert it first.
    Ensure that the file starts directly with a volume/chapter name, without anything else.
    '''

    in_dir = os.path.dirname(filename)

    if out_dir is None:
        out_dir = in_dir

    if sort_volume:
        with open(os.path.join(in_dir, 'volumes.json'), 'rt') as order_f:
            volumes = json.load(order_f)
    else:
        volumes = None

    with open(filename, 'rt', encoding='utf8') as file:
        chapter = None
        curr_dir = './'
        for line in file:
            is_special_line = False

            if volumes is not None:
                for volume in volumes:
                    if line.startswith(volume['volume']):
                        is_speical_line = True
                        os.mkdir(os.path.join(out_dir, volume['name']))
                        break
            else:
                if re.match(r'^第.+卷\s.*$', line):
                    is_special_line = True
                    end = line.index('卷')
                    number = str(toNum(line[1: end]))
                    curr_dir = '第' + number + line[end:-1]
                    os.mkdir(os.path.join(out_dir, curr_dir))

            if re.match(r'^第.+章\s.*$', line):
                is_special_line = True
                # Matches regular chapters with a proper name.
                if chapter is not None:
                    # New chapter, close previous chapter file
                    chapter.close()

                end = line.index('章')
                number = str(toNum(line[1: end]))
                line = '第' + number + line[end:-1]
                filename_line = line.translate(valid_filenames)
                chapter = open(os.path.join(out_dir, curr_dir,
                                            filename_line + '.md'), 'w', encoding='utf8')
                chapter.write('# ' + line + '\n')

            if re.match(r'^第.+章$', line):
                is_special_line = True
                # Matches chapters without a proper name
                if chapter is not None:
                    chapter.close()

                number = str(toNum(line[1: -2]))
                line = '第' + number + '章'
                chapter = open(os.path.join(out_dir, curr_dir,
                                            line + '.md'), 'w', encoding='utf8')
                chapter.write('# ' + line + '\n')

            if re.match(r'^(序章|楔子)\s.*$', line):
                is_special_line = True
                # Matches preface/intro chapters
                if chapter is not None:
                    chapter.close()

                filename_line = line.translate(valid_filenames)
                chapter = open(os.path.join(out_dir, curr_dir,
                                            filename_line + '.md'), 'w', encoding='utf8')
                chapter.write('# ' + line + '\n')

            # You may add more patterns here, like final chapters, etc.

            if chapter is not None and not is_special_line:
                # Regular chapter line
                chapter.write(line + '\n')

        chapter.close()


if (__name__ == '__main__'):
    parser = argparse.ArgumentParser(
        description='Split ebook file into individual chapters.')
    parser.add_argument('-f', '--filename', help='Filename of the book file.')
    parser.add_argument('-s', '--sort_volume', type=bool, default=False,
                        help='Whether volumes.json will be used to detect custom volumes. By default, regular volume names will be supported.')
    parser.add_argument('-o', '--out_dir', default=None,
                        help='Directory of the output files.')

    args = parser.parse_args()
    split(args.filename, args.sort_volume, args.out_dir)
