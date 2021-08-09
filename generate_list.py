import argparse
from framework import Worker
from utils import generate_objects


def generate_list(in_dir: str, out_dir: str):
    """
    Generates a list from the given directory.
    Usually, after analyzing the novel and splitting it into individual chapter files, one would manually inspect the
    files and make necessary modifications. This process might change the novel structure, and the original list/toc
    files might no longer apply. Therefore, one would need to recreate the list from the directory.
    """
    additional_args = {'in_dir': in_dir}
    if out_dir:
        additional_args['out_dir'] = out_dir
    objects = generate_objects('list_config.json', 'list_config.json', in_dir, additional_args)
    worker = Worker(objects['readers'], [], objects['writers'])
    worker.work()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a list from the given directory.')
    parser.add_argument('-i', '--in_dir', help='Directory of the novel.')
    parser.add_argument('-o', '--out_dir', default=None, help='Directory of the output file.')

    args = parser.parse_args()
    generate_list(args.in_dir, args.out_dir)
