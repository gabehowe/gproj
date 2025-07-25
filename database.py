import argparse
import dataclasses
import os
import re
import shutil
import uuid
from datetime import datetime
from typing import List, Optional, Dict
import gzip
import yaml
import flask
from math import floor

from yaml import Loader, parse

app = flask.Flask(__name__, template_folder='web/templates', static_folder='web/static')

DEFAULT_IGNORE = ['.idea', 'venv', 'node_modules', 'src', 'build', '.git', 'lib$', 'library', 'libraries', 'release',
                  '.gradle',
                  'plugins', 'saved',
                  'depend', 'res', 'ports', 'download', 'servers', 'out$', 'run$', 'source', 'generated$', 'content$']


@dataclasses.dataclass
class GProj:
    title: str
    creation: datetime
    languages: List[str]
    categories: List[str]
    path: str
    id: str

    def stringinate(self):
        values = {'title': self.title,
                  'creation': self.creation.strftime("%Y-%m-%d") if isinstance(self.creation, datetime) else str(
                      self.creation),
                  'languages': "[ " + ",".join(self.languages) + " ]", 'categories': "[ " + ",".join(self.categories) + " ]", 'id': self.id}
        return values

    def serialize(self):
        values = {'title': self.title,
                  'creation': self.creation.strftime("%Y-%m-%d") if isinstance(self.creation, datetime) else str(
                      self.creation),
                  'languages': self.languages, 'categories': self.categories, 'id': str(self.id), 'path': self.path}
        return values

    @classmethod
    def from_path(cls, file_path: os.PathLike):
        with open(file_path, 'r+') as file:
            text = file.read().replace('#', '-sharp')
            text = text.replace('\t', '    ')
            data: Dict[str, str] = yaml.load(text, Loader=Loader)
            if 'GProj' not in str(type(data)):
                if 'id' not in data.keys():
                    id = uuid.uuid4()
                    data['id'] = str(id)
                    with open(i, 'w+') as file:
                        yaml.safe_dump(data, file)
                if 'path' not in data.keys():
                    data['path'] = os.path.abspath(file_path.removesuffix('.gproj'))
                proj = GProj(**data)
                proj.languages = sorted(proj.languages)
                proj.categories = sorted(proj.categories)
            else:
                proj = data
        file.close()
        return proj


projects: List[GProj] = []


def make_link(project: GProj, file_path: os.PathLike):
    database_loc = os.environ['PROJECT_DATABASE']
    link_title = project.title.replace(' ', '-')
    try:
        os.symlink(f'{database_loc}/{project.id}', f'{file_path}/{link_title}')
    except FileExistsError:
        os.symlink(f'{database_loc}/{project.id}', f'{file_path}/{link_title}-{project.id}')


def make_all_links(projects: List[GProj]):
    database_loc = os.environ['PROJECT_DATABASE']
    for i in projects:
        make_link(i, database_loc + '/../links')


def check_dir(dir_name, project_files) -> int:
    if any([re.search(fr'/{it}', dir_name.lower()) for it in IGNORE]):
        # print(f'{Fore.CYAN} ditching {subject}.{Style.RESET_ALL}')
        return 0
    if re.search('/.gproj$', dir_name):
        # print(f'{Fore.GREEN} found {dir_name}.{Style.RESET_ALL}')
        project_files.append(dir_name)
        return 0
    if not os.path.isdir(dir_name):
        return 0

    return 1


def breadth_first(directory):
    unchecked = os.listdir(directory)
    dirs = []
    project_files = []
    while len(unchecked) > 0:
        subject = unchecked[0]

        unchecked.remove(subject)
        if check_dir(directory + '/' + subject, project_files) == 0:
            continue

        dirs.append(subject)
        for i in os.listdir(directory + '/' + subject):
            if check_dir(f'{directory}/{subject}/{i}', project_files) == 0:
                continue
            unchecked.append(f'{subject}/{i}')
    # print(project_files)
    return project_files


def index_dir(directory):
    # print(dirs)
    dirs = breadth_first(directory)
    projects = []
    for i in dirs:
        proj = GProj.from_path(i)
        projects.append(proj)
    # print(projects)
    if os.path.exists(database_file):
        os.remove(database_file)
    with open(database_file, 'x+') as file:
        serialized = []
        for i in projects:
            serialized.append(i.serialize())
        file.write(yaml.safe_dump(serialized))

    return projects


def create_table(data: List[List[str]]):
    try:
        cols, lines = os.get_terminal_size()
    except OSError:
        cols = 500
    lines = [[e[i] for e in data] for i in range(len(data[0]))]
    lengths = [max([len(e) for e in i]) for i in lines]
    overlength = 1
    total_length = sum(lengths) + 6 * 3
    if total_length > cols:
        overlength = cols / total_length
    for i in data:
        line_str = " | "
        for e in i:
            length = floor(lengths[i.index(e)] * (overlength * 0.9 if overlength < 1 else 1))
            cell = e.ljust(length)
            if len(cell) > length:
                if i.index(e) == 0:  # Chop down UUID the most
                    cell = cell[:length - 7] + "…"
                elif i.index(e) == 2:  # Don't chop down date
                    pass
                else:
                    cell = cell[:length - 1] + "…"
            line_str += cell + " | "
        print(line_str)


def print_table(projects: List[GProj]):
    data = [([f"UUID", f"Title", f"Date",
              f"Categories", f"Languages"])]

    data += list(
        map(lambda it: [it.id, it.title,
                        it.creation if isinstance(it.creation, str) else it.creation.strftime("%Y-%m-%d"),
                        it.categories if isinstance(it.categories, str) else ", ".join(it.categories),
                        it.languages if isinstance(it.languages,str) else ", ".join(it.languages)], projects))
    create_table(data)

    print(f'Project Count: {len(projects)}')
    print("GPROJ DATABASE TOOL")


def output_csv():
    text = ""
    for i in projects:
        text += f"{i.id}~{i.title}~{i.creation.strftime('%Y-%m-%d') if not isinstance(i.creation, str) else i.creation}~{','.join(i.categories)}~{','.join(i.languages)}\n"
    if os.path.exists('./out.csv'):
        os.remove('./out.csv')
    with open('out.csv', 'x+') as file:
        file.write(text)


@app.route("/")
def index():
    categories = []
    languages = []
    for i in projects:
        categories.extend(i.categories)
        languages.extend(i.languages)
    return flask.render_template('index.html', projects=projects, count=len(projects), categories=set(categories),
                                 languages=set(languages))


@app.route("/static/<path:path>")
def static_files(path):
    return flask.send_from_directory('web/static', path)


@app.route("/project/<path:path>")
def project(path):
    for i in projects:
        if path.lower() in i.title.lower():
            file = open(i.path, 'r+')
            text = file.read()
            return flask.render_template('project.html', body=text, path=os.path.abspath(i.path))


@app.route("/data")
def data():
    new_projects = projects.copy()
    for i in new_projects:
        if isinstance(i.creation, str):
            continue
        i.creation = i.creation.strftime("%Y-%m-%d")

    return flask.jsonify(projects)


def parse_file() -> List[GProj]:
    projects = []
    data = yaml.safe_load(open(database_file, 'r+'))
    for i in data:
        projects.append(GProj(**i))
    projects.sort(key=lambda it: it.serialize()['creation'])
    return projects


def web_server():
    parse_file()
    app.run(port=8000)


def pack():
    global projects
    os.mkdir('./temp')
    for i in projects:
        shutil.copytree(i.path.removesuffix('.gproj'), f'./temp/{i.id}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d',
                        help='Usage: -d [dir] to parse a directory to default file directory/index.gproj (set with -i)')
    parser.add_argument('-i', help='Sets the index file location')
    parser.add_argument('-s', help='Starts the web server', action='store_true')
    parser.add_argument('-t', help='Creates a command line table', action='store_true')
    parser.add_argument('-f', help='Outputs a csv', action='store_true')
    parser.add_argument('-p', help='Copies all projects into one place', action='store_true')
    parser.add_argument('--build-links', help='Creates file links for the project', action='store_true')

    args = parser.parse_args()

    database_file = './index.gproj' if not args.i else args.i
    if len(args._get_kwargs()) == 0:
        parser.print_help()
    if args.d is not None:
        if not os.path.exists(args.d):
            print(f"Directory {args.d} does not exist.")
            exit(1)

        if not args.i:
            database_file = args.d + '/index.gproj'

        if not os.path.exists(args.d + './ignore.gproj'):
            with open(args.d + 'ignore.gproj', 'w+') as file:
                file.write('\n'.join(DEFAULT_IGNORE))

        IGNORE = [i.strip() for i in open(args.d + 'ignore.gproj').readlines()]
        index = index_dir(args.d)
        projects = parse_file()
        print_table(index)
    elif args.t:
        projects = parse_file()
        print_table(projects)
    elif args.f:
        projects = parse_file()
        output_csv()
    elif args.p:
        projects = parse_file()
        pack()
    elif args.build_links:
        projects = parse_file()
        make_all_links(projects)

    if args.s:
        projects = parse_file()
        web_server()
