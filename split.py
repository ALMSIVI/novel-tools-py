import argparse
import re
import os

# Chinese to Arabic number correspondings
num_dict = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100, '千': 1000, '两': 2}
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


def split(filename):
    '''
    Split a whole txt file into individual chapters, with possible volume subdirectories.
    The input file is default to utf8 encoding. If it is encoded in GB2312 you need to convert it first.
    Ensure that the file starts directly with a volume/chapter name, without anything else.
    '''

    dirname = os.path.dirname(filename)
    with open(filename, 'rt', encoding='utf8') as file:
        chapter = None
        folder = './'
        for line in file.read().splitlines():
            if re.match(r'^第.+卷\s.*$', line):
                # Only regular volume names are supported. You need to manually sort out the irregular ones.
                end = line.index('卷')
                number = str(toNum(line[1: end]))
                folder = '第' + number + line[end:]
                os.mkdir(os.path.join(dirname, folder))
            elif re.match(r'^第.+章\s.*$', line):
                # Matches regular chapters with a proper name.
                if chapter != None:
                    # New chapter, close previous chapter file
                    chapter.close()

                end = line.index('章')
                number = str(toNum(line[1: end]))
                line = '第' + number + line[end:]
                filename_line = line.translate(valid_filenames)
                chapter = open(os.path.join(dirname, folder, filename_line + '.md'), 'w', encoding='utf8')
                chapter.write('# ' + line + '\n')
            elif re.match(r'^第.+章$', line):
                # Matches chapters without a proper name
                if chapter != None:
                    chapter.close()

                number = str(toNum(line[1: -1]))
                line = '第' + number + '章'
                chapter = open(os.path.join(dirname, folder, line + '.md'), 'w', encoding='utf8')
                chapter.write('# ' + line + '\n')
            elif re.match(r'^(序章|楔子)\s.*$', line):
                # Matches preface/intro chapters
                if chapter != None:
                    chapter.close()

                filename_line = line.translate(valid_filenames)
                chapter = open(os.path.join(dirname, folder, filename_line + '.md'), 'w', encoding='utf8')
                chapter.write('# ' + line + '\n')
                # You may add more patterns here, like final chapters, etc.
            elif chapter != None:
                # Regular chapter line
                chapter.write(line + '\n')
        
        chapter.close()

if (__name__ == '__main__'):
    parser = argparse.ArgumentParser(description = 'Split ebook file into individual chapters.')
    parser.add_argument('-f', '--filename', help = 'Filename of the book file.')

    args = parser.parse_args()
    split(args.filename)
