import os
import sys
from typing import Callable

import colorama
from colorama import Style

import database
import find_bare

# TODO: replace with generator
def try_term(term: Callable[[], str], options, interactive: bool = False):
    """
    try to filter options based on term.
    """
    try:
        term_val = term()
    except StopIteration:
        return options

    filtered_options = find_bare.filter_for_term(term_val, options)
    if len(filtered_options) == 0:
        if interactive:
            database.print_table(options)
        print(colorama.Fore.RED + f"No results for {term_val}." + colorama.Fore.RESET)
        return try_term(term, options, interactive)

    if len(filtered_options) > 1:
        if interactive:
            database.print_table(filtered_options)
        return try_term(term, filtered_options, interactive)

    return filtered_options

# try to filter each pre-option
# if pre-option doesn't filter, restore old state and try to filter with next pre-option
# then, ask user

if __name__ == '__main__':
    print(Style.BRIGHT + "Welcome to Project Finder!" + Style.RESET_ALL)
    # TODO: throw error if PROJECT_DATABASE is not set
    database.database_file = os.environ["PROJECT_DATABASE"] + '/index.gproj'
    options = database.parse_file()
    unfound = False
    # prefilter based on command line arguments
    if len(sys.argv) > 2:
        itr = iter(sys.argv[2:])
        options = try_term(itr.__next__, options, False)
    database.print_table(options)

    if len(options) > 1:
        options = try_term(lambda: input("term: ").lower(), options, True)

    print(f'{ options[0].title }/{options[0].creation}')
    if len(sys.argv) > 1:
        tf_loc = sys.argv[1]
        with open(tf_loc, 'w+') as tempfile:
            tempfile.write(f'{options[0].path}')
