import argparse
import os
from natsort import natsorted
import json


def concatenate(in_dir: str, out_dir: str, title_heading: int, volume_heading: int, chapter_heading: int, append_volume: bool) -> None:
    '''
    Concatenate chapters, including volume subdirectories.
    Input file should be of type <volume>/<chapter>.md
    '''

    # Read book metadata
    with open(os.path.join(in_dir, 'metadata.json'), 'rt') as metadata_file:
        metadata = json.load(metadata_file)
        book_name = metadata['title']

    # If no out_dir is specified, use in_dir
    if out_dir is None:
        out_dir = in_dir

    # If append_volume is false, decrement chapter_heading
    if not append_volume:
        chapter_heading -= 1

    with open(os.path.join(out_dir, book_name + '.md'), 'wt') as book_file:
        # Book title
        for i in range(title_heading):
            book_file.write('#')

        book_file.write(' ')
        book_file.write(book_name)
        book_file.write('\n\n')

        # Book intro (if it exists)
        intro_file = os.path.join(in_dir, '_intro.txt')
        if os.path.exists(intro_file):
            print('Intro file detected. Appending to book...')
            with open(intro_file, 'rt') as intro:
                for line in intro:
                    book_file.write(line)
            book_file.write('\n\n')

        # Custom volume order
        volumes_filename = os.path.join(in_dir, 'volumes.json')
        if os.path.isfile(volumes_filename):
            with open(volumes_filename, 'rt') as order_f:
                volumes = json.load(order_f)
        else:
            volumes = [{'name': volume, 'volume': volume}
                       for volume in natsorted(os.listdir(in_dir))
                       if os.path.isdir(os.path.join(in_dir, volume))]

        # Concatenate volume by volume
        for volume in volumes:
            volume_dir = os.path.join(in_dir, volume['name'])

            print('Appending volume {}'.format(volume['volume']))

            # Volume title
            if append_volume:
                for i in range(volume_heading):
                    book_file.write('#')

                book_file.write(' ')
                book_file.write(volume['volume'])
                book_file.write('\n\n')

            # Concatenate chapter by chapter
            chapters = natsorted(os.listdir(volume_dir))
            # Volume intro
            if '_intro.txt' in chapters:
                with open(os.path.join(volume_dir, '_intro.txt'), 'rt') as c:
                    for line in c:
                        if line == '\n':
                            continue

                        book_file.write(line)
                        book_file.write('\n')

                    book_file.write('\n')  # End of chapter
                chapters.remove('_intro.txt')

            for chapter in chapters:
                chapter_filename = os.path.join(volume_dir, chapter)
                with open(chapter_filename, 'rt') as c:
                    for line in c:
                        if line == '\n':
                            continue
                        if line.startswith('# '):  # Chapter header
                            for i in range(chapter_heading):
                                book_file.write('#')

                            book_file.write(line[line.index(' '):])
                        else:  # Regular line
                            book_file.write(line)
                        book_file.write('\n')

                    book_file.write('\n')  # End of chapter


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Concatenate chapter files to a single ebook text file.')
    parser.add_argument('-i', '--in_dir',
                        help='Directory for finding chapter files.')
    parser.add_argument('-o', '--out_dir', default=None,
                        help='Directory for outputing book file.')
    parser.add_argument('-t', '--title_heading', type=int,
                        default=1, help='Heading of book title.')
    parser.add_argument('-v', '--volume_heading', type=int,
                        default=2, help="Heading of volume.")
    parser.add_argument('-c', '--chapter_heading', type=int,
                        default=3, help='Heading of chapter titles.')
    parser.add_argument('-a', '--append_volume', action='store_false', default=True,
                        help='Set this argument if there are no volumes or if you do not want to include volume headings.')

    args = parser.parse_args()
    concatenate(args.in_dir, args.out_dir, args.title_heading,
                args.volume_heading, args.chapter_heading, args.append_volume)
