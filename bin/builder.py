from fnmatch import fnmatch
from itertools import chain
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED
import argparse
import glob
import json
import os


THIS_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
RESERVED = ['manifest.json', 'dist']


parser = argparse.ArgumentParser(
                    description="Builds .sublime-package archives.")
parser.add_argument('-d', dest='target_dir', default='./dist',
                    help="output directory")
parser.add_argument('--release', dest='release', default='dev',
                    help="type of build (e.g. 'dev', 'release'...)")


def get_manifest():
    path = os.path.join(PROJECT_ROOT, 'manifest.json')
    with open(path) as f:
        return json.load(f)


def unwanted(fn, pats):
    return any(fnmatch(fn, pat) for pat in pats + RESERVED)


def ifind_files(patterns):
    for fn in (fn for (pat, exclude) in patterns
                                     for fn in glob.iglob(pat)
                                     if not unwanted(fn, exclude)):
        yield fn


def build(target_dir="dist", release="dev"):
    os.chdir(PROJECT_ROOT)
    manifest = get_manifest()
    name = manifest['name'] + '.sublime-package'

    target_dir = os.path.join(PROJECT_ROOT, target_dir)
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    target_file = os.path.join(target_dir, name)
    if os.path.exists(target_file):
        os.unlink(target_file)

    with ZipFile(target_file, 'a', compression=ZIP_DEFLATED) as package:
        for fn in ifind_files(manifest['include'][release]):
            package.write(fn)


if __name__ == '__main__':
    args = parser.parse_args()
    build(args.target_dir, args.release)
