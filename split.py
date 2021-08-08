import argparse
from split import split

if (__name__ == '__main__'):
    parser = argparse.ArgumentParser(
        description='Split ebook file into individual chapters.')
    parser.add_argument('-t', '--tool', default='list_generator',
                        help='Select which tool you want to use. Default is to generate a csv file.')
    parser.add_argument('-f', '--filename',
                        help='Filename of the book file.')
    parser.add_argument('-o', '--out_dir', default=None,
                        help='Directory of the output files.')

    args = parser.parse_args()
    split(args.filename, args.out_dir)