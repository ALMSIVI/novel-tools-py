import argparse
from utils import import_class

if (__name__ == '__main__'):
    parser = argparse.ArgumentParser(
        description='Split ebook file into individual chapters.')
    parser.add_argument('-t', '--tool', default='list_generator',
                        help='Select which tool you want to use. Default is to generate a csv file.')
    parser.add_argument('-f', '--filename',
                        help='Filename of the book file.')
    parser.add_argument('-o', '--out_dir', default=None,
                        help='Directory of the output files.')
    parser.add_argument('-d', '--discard_chapters', action='store_true', default=False,
                        help='Set this argument if you want to discard chapter ids between volumes during duplicate/missing chapter detection.')
    parser.add_argument('-c', '--correct', action='store_true', default=False,
                        help='Set this argument if you want to automatically correct missing or duplicate chapters.')
    parser.add_argument('-v', '--debug', action='store_true', default=False, 
                        help='Set this argument if you want extended debug information in the csv file. This could be helpful if you use this script on a new file, or if you know there are problems with the file.')

    args = parser.parse_args()
    
    tool = import_class(args.tool, 'split')
    tool(args.filename, args.out_dir, args.discard_chapters, args.correct, args.debug).split()