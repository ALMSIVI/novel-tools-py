import argparse
import os
from natsort import natsorted
import json

def concatenate(indir, outdir, title, filename, chapter, volume_order):
    '''
    Concatenate chapters, including volume subdirectories.
    Input file should be of type <volume>/<chapter>.md
    '''

    book_name = os.path.basename(indir)

    with open(os.path.join(outdir, book_name + '.md'), 'wt') as f:
        if title == 'yes':
            f.write(book_name)
            f.write('\n')

        f.write('\n')

        if volume_order == 'yes':
            # Use custom sort order
            with open(os.path.join(indir, 'order.json'), 'rt') as order_f:
                volumes = json.load(order_f)
        else:
            volumes = [{'name': volume, 'volume': volume} for volume in natsorted(os.listdir(indir))]

        for volume in volumes:
            volume_dir = os.path.join(indir, volume['name'])
            if os.path.isdir(volume_dir):
                f.write('# ')
                f.write(volume['volume'])
                f.write('\n\n')

                for part in natsorted(os.listdir(volume_dir)):
                    part_dir = os.path.join(volume_dir, part)
                    if not part.endswith('.md'):
                        continue
                    with open(part_dir, 'rt') as c:
                        if filename == 'yes' or filename == 'header':
                            part_name = part[:part.rindex('.')]
                            if filename == 'header':
                                f.write('## ')
                            f.write(part_name)
                            f.write('\n\n')
                        for line in c:
                            if line == '\n':
                                continue
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
    parser.add_argument('-c', '--chapter', choices = ['indent', 'keep', 'remove'], default = 'indent', help = 'If titles/headers in each chapter file needs to be indented, kept or removed.')
    parser.add_argument('-v', '--volume', choices = ['no', 'yes'], default = 'no', help = 'If set to yes, the program will find a order.json file and use that as the order for the volumes. Otherwise, it uses natural sort.')

    args = parser.parse_args()
    concatenate(args.indir, args.outdir, args.title, args.filename, args.chapter, args.volume)