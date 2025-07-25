import argparse
import shutil
import sys


import colorama
from colorama import Style
from colorama import Fore

import database
import os

def filter_for_term(term, options):
    last_options = options.copy()
    options = list(filter(lambda it: term in (" ".join(it.stringinate().values())).lower(), options))
    unfound = term if len(options) == 0 else None
    if unfound:
        options = last_options
    return options, unfound

if __name__ == '__main__':
    print(Style.BRIGHT + "Welcome to Project Finder!" + Style.RESET_ALL)
    database.database_file = '/home/gabri/dev/database/index.gproj'
    options = database.parse_file()
    unfound = False
    if len(sys.argv) > 1:
        for i in sys.argv[1:]:
            options = filter_for_term(i, options)

    while len(options) > 1:
        database.print_table(options)
        if unfound:
            print(colorama.Fore.RED + f"No results for {unfound}." + colorama.Fore.RESET)
            unfound = None
        term = input("term: ").lower()
        options, unfound = filter_for_term(term, options)

    # os.system(f'cd /home/gabri/dev/database/temp/{options[0].id}')
    print(f'{ options[0].title }/{options[0].creation}')
    tf_loc = "/tmp/searchtempfile"
    if os.path.exists(tf_loc):
        os.remove(tf_loc)
    with open(tf_loc, 'x+') as tempfile:
        tempfile.write(f'{os.environ["PROJECT_DATABASE"]}/{options[0].id}')
