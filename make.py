import datetime
import os
import uuid

import yaml

import database
from database import GProj
import sys

if __name__ == '__main__':
    database_loc = os.environ['PROJECT_DATABASE']
    title = input('title: ')
    database.database_file = '/home/gabri/dev/database/index.gproj'
    projects = database.parse_file()
    categories = []
    languages = []
    for i in projects:
        categories += i.categories
        languages += i.languages
    categories = set(categories)
    languages = set(languages)
    print(", ".join(categories))
    categories = [i.strip() for i in input("categories (comma sep): ").strip().split(',')]

    print(", ".join(languages))
    languages = [i.strip() for i in input("languages (comma sep): ").split(',')]
    id = str(uuid.uuid4())
    path = f'{database_loc}/{id}'
    os.mkdir(path)
    obj = GProj(title, datetime.datetime.now(), languages, categories, path + '/.gproj', id)

    print(f'{title} {obj.creation.strftime("%Y-%m-d")} {categories} {languages} {id}')
    with open(f'{database_loc}/{id}/.gproj', 'x+') as file:
        yaml.dump(obj.stringinate(), file) # Might cause issues -- if so, stop using stringinate.

    with open(f'/home/gabri/dev/database/index.gproj', 'r+') as file:
        index = yaml.safe_load(file)
        index.append(obj.serialize())
    with open(f'/home/gabri/dev/database/index.gproj', 'w+') as file:
        yaml.dump(index, file)

    if len(sys.argv) > 1:
        tf_loc = sys.argv[1]
        with open(tf_loc, 'w+') as tempfile:
            tempfile.write(path)
