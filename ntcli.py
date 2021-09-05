import argparse
import os
from toolkit import analyze, add, convert, docgen
from utils import get_config


def do_analyze(args):
    config_filename = args.toolkit + '_config.json'
    if os.path.isfile(args.input):
        in_dir = os.path.basename(args.input)
        config = get_config(config_filename, in_dir)
        analyze(config, filename=args.input, out_dir=args.output)
    else:
        config = get_config(config_filename, args.input)
        analyze(config, in_dir=args.input, out_dir=args.output)


def start():
    parser = argparse.ArgumentParser(description='Novel Tools command line interface.')
    subparsers = parser.add_subparsers(help='Tools provided by this package.', dest='command', required=True)

    # Framework functions #
    analyze_parser = subparsers.add_parser('analyze', description='Analyzes the novel file(s).')
    analyze_parser.add_argument('-t', '--toolkit',
                                help='The toolkit that will be executed. Built-in toolkits include'
                                     'struct, create, split, struct_dir, and create_dir. If a custom toolkit is given, '
                                     'make sure to have <toolkit>_config.json under the input directory.')
    analyze_parser.add_argument('-i', '--input',
                                help='Input filename or directory name. If it is a file, it will only be recognized by'
                                     ' TextReader, and it must contain the full path.')
    analyze_parser.add_argument('-o', '--output', default=None, help='Output directory name.')
    analyze_parser.set_defaults(func=do_analyze)

    # Other functions #
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
    doc_parser.add_argument('-c',
                            '--config_filename',
                            default=None,
                            help='Filename of the config which specifies additional packages.')
    doc_parser.add_argument('-d', '--doc_filename', default=None, help='Filename of the output doc file.')
    doc_parser.set_defaults(func=lambda a: docgen(a.config_filename, a.doc_filename))

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    start()
