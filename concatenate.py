import argparse
import os
from natsort import natsorted

def concatenate(indir, outdir, title, filename, chapter):
    '''
    Concatenate pure chapters, without volume subdirectories.
    Input file should be of type <chapter>.md
    '''

    book_name = os.path.basename(indir)

    with open(os.path.join(outdir, book_name + '.md'), 'wt') as f:
        if title == 'yes':
            f.write(book_name)
            f.write('\n')

        f.write('\n')

        for part in natsorted(os.listdir(indir)):
            part_file = os.path.join(indir, part)
            if os.path.isdir(part_file) or not part_file.endswith('.md'):
                continue
            with open(part_file, 'rt') as c:
                if filename == 'yes' or filename == 'header':
                    part_name = part[:part.rindex('.')]
                    if filename == 'header':
                        f.write('# ')
                    f.write(part_name)
                    f.write('\n\n')
                for line in c:
                    if line.startswith('#'): # Header
                        if chapter == 'indent':
                            f.write('#')
                            f.write(line)
                        elif chapter == 'keep':
                            f.write(line)
                        else: # remove
                            f.write(line[line.index(' ') + 1:])
                    else:
                        f.write(line)
                    f.write('\n')
                f.write('\n')

if __name__ == '__main__':
    default_dir = os.curdir

    parser = argparse.ArgumentParser(description = 'Concatenate chapter files to a single ebook text file.')
    parser.add_argument('-i', '--indir',  default = default_dir, help = 'Directory for finding chapter files.')
    parser.add_argument('-o', '--outdir', default = default_dir, help = 'Directory for outputing chapter files.')
    parser.add_argument('-t', '--title', choices = ['no', 'yes'], default = 'no', help = 'If the title of the book should be included at the beginning of the book file.')
    parser.add_argument('-f', '--filename', choices = ['no', 'yes', 'header'], default = 'no', help = 'If chapter filename should be included in the book file, and, if included, whether a H1 header is needed.')
    parser.add_argument('-c', '--chapter', choices = ['indent', 'keep', 'remove'], default = 'keep', help = 'If titles/headers in each chapter file needs to be indented, kept or removed.')

    args = parser.parse_args()
    concatenate(args.indir, args.outdir, args.title, args.filename, args.chapter)