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
    database.database_file = database_loc + '/index.gproj'
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
    obj = GProj(title, datetime.datetime.now(), languages, categories, path, id)

    print(f'{title} {obj.creation.strftime("%Y-%m-d")} {categories} {languages} {id}')
    with open(path + '/.gproj', 'x+') as file:
        yaml.dump(obj.serialize(), file) # Might cause issues -- if so, stop using stringinate.

    with open(database.database_file, 'r+') as file:
        index = yaml.safe_load(file)
        index.append(obj.serialize())
    with open(database.database_file, 'w+') as file:
        yaml.dump(index, file)

    if len(sys.argv) > 1:
        tf_loc = sys.argv[1]
        with open(tf_loc, 'w+') as tempfile:
            tempfile.write(path)
