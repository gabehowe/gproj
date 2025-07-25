import argparse
import shutil
import sys

import colorama

import database
import os


def filter_func(it, term):
    val = term in (" ".join(it.stringinate().values())).lower()
    return val


def filter_for_term(term, options):
    filtered_options = list(filter(lambda it: filter_func(it, term), options))
    return filtered_options


if __name__ == '__main__':
    database.database_file = '/home/gabri/dev/database/index.gproj'
    # TODO: make this an env variable
    options = database.parse_file()
    unfound = False
    if len(sys.argv) > 1:
        for i in sys.argv[1:]:
            options = filter_for_term(i.removesuffix('"').removeprefix('"'), options)

    if len(options) > 1:
        print("Too ambiguous!", file=sys.stderr)
        sys.exit(-1)
    elif len(options) == 0:
        print("Couldn't find", file=sys.stderr)
        sys.exit(-1)

    print(f'{os.environ["PROJECT_DATABASE"]}/{options[0].id}')
