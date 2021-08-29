import argparse
import os
from toolkit import analyze, add, convert, docgen
from utils import get_config

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Novel Tools command line interface.')
    subparsers = parser.add_subparsers(help='Tools provided by this package.', dest='command', required=True)

    # struct
    analyze_parser = subparsers.add_parser('struct', description='Generates the structure from the text file.')
    analyze_parser.add_argument('-f', '--filename', help='Filename of the book file.')
    analyze_parser.add_argument('-o', '--out_dir', default=None, help='Directory of the output file(s).')
    analyze_parser.add_argument('-c', '--config', default='analyze_config.json', help='Filename of the config file.')
    analyze_parser.set_defaults(func=lambda a: analyze(get_config(a.config, os.path.dirname(a.filename),
                                                                  os.path.join('config', 'struct_config.json')),
                                                       filename=a.filename,
                                                       out_dir=a.out_dir))

    # add_to_calibre
    add_parser = subparsers.add_parser('add', description='Add a book file to Calibre database.')
    add_parser.add_argument('-d', '--dir', help='Directory for book and metadata files.')
    add_parser.set_defaults(func=lambda a: add(a.dir))

    # calibre_convert
    convert_parser = subparsers.add_parser('convert',
                                           description='Convert a file to epub using calibre\'s built-in tool.')
    convert_parser.add_argument('-d', '--dir', help='Directory for book and metadata files.')
    convert_parser.set_defaults(func=lambda a: convert(a.dir))

    # generate_docs
    doc_parser = subparsers.add_parser('docgen', description='Generates documentation for framework classes.')
    doc_parser.add_argument('-c', '--config_filename', default=None,
                            help='Filename of the config which specifies additional packages.')
    doc_parser.add_argument('-d', '--doc_filename', default=None, help='Filename of the output doc file.')
    doc_parser.set_defaults(func=lambda a: docgen(a.config_filename, a.doc_filename))

    args = parser.parse_args()
    args.func(args)
