import argparse
import os
from toolkit import analyze, listgen, create, add, convert, docgen

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Novel Tools command line interface.')
    subparsers = parser.add_subparsers(help='Tools provided by this package.', dest='command', required=True)

    # analyze
    analyze_parser = subparsers.add_parser('analyze', description='Analyzes the volume/chapter structure of the novel.')
    analyze_parser.add_argument('-f', '--filename', help='Filename of the book file.')
    analyze_parser.add_argument('-o', '--out_dir', default=None, help='Directory of the output file(s).')
    analyze_parser.add_argument('-c', '--config', default='analyze_config.json', help='Filename of the config file.')
    analyze_parser.set_defaults(func=lambda a: analyze(a.filename, a.out_dir, a.config))

    # generate_list
    generate_list_parser = subparsers.add_parser('generate_list',
                                                 description='Generates a list from the given directory.')
    generate_list_parser.add_argument('-i', '--in_dir', help='Directory of the novel.')
    generate_list_parser.add_argument('-o', '--out_dir', default=None, help='Directory of the output file.')
    generate_list_parser.add_argument('-c', '--config', default='list_config.json', help='Filename of the config file.')
    generate_list_parser.set_defaults(func=lambda a: listgen(a.in_dir, a.out_dir, a.config))

    # create
    create_parser = subparsers.add_parser('create', description='Recreates the novel from the cleaned up data.')
    create_parser.add_argument('-f', '--filename', help='Directory or filename of the novel.')
    create_parser.add_argument('-o', '--out_dir', default=None, help='Directory of the output file.')
    create_parser.add_argument('-c', '--config', default='create_config.json', help='Filename of the config file.')
    create_parser.set_defaults(func=lambda a: create(None, args.filename, args.out_dir, a.config) if os.path.isdir(
        a.filename) else create(args.filename, os.path.dirname(args.filename), args.out_dir, a.config))

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
    doc_parser = subparsers.add_parser('generate_docs', description='Generates documentation for framework classes.')
    doc_parser.add_argument('-c', '--config_filename', default=None,
                            help='Filename of the config which specifies additional packages.')
    doc_parser.add_argument('-d', '--doc_filename', default=None,
                            help='Filename of the output doc file.')
    doc_parser.set_defaults(func=lambda a: docgen(a.config_filename, a.doc_filename))

    args = parser.parse_args()
    args.func(args)
