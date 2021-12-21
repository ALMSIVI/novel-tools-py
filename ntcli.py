import argparse
from pathlib import Path
from novel_tools.toolkit import analyze, docgen
from novel_tools.utils import get_config


def do_analyze(args):
    config_filename = args.toolkit + '_config.json'
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output is not None else None
    if input_path.is_file():
        in_dir = input_path.parent
        config = get_config(config_filename, in_dir)
        analyze(config, filename=input_path, out_dir=output_path)
    else:
        config = get_config(config_filename, input_path)
        analyze(config, in_dir=input_path, out_dir=output_path)


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

    # generate_docs
    doc_parser = subparsers.add_parser('docgen', description='Generates documentation for framework classes.')
    doc_parser.add_argument('-c', '--config_filename', default=None,
                            help='Filename of the config which specifies additional packages.')
    doc_parser.add_argument('-d', '--doc_filename', default=None, help='Filename of the output doc file.')
    doc_parser.set_defaults(func=lambda a: docgen(a.config_filename, a.doc_filename))

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    start()
