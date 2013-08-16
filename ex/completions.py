import sublime
import sublime_plugin

import glob
import os
import re

RX_CMD_LINE_CD = re.compile(r'^(?P<cmd>:\s*cd!?)\s+(?P<path>.*)$')
RX_CMD_LINE_WRITE = re.compile(r'^(?P<cmd>:\s*w(?:write)?!?)\s+(?P<path>.*)$')
RX_CMD_LINE_EDIT = re.compile(r'^(?P<cmd>:\s*e(?:dit)?!?)\s+(?P<path>.*)$')

COMPLETIONS_FILE = 1
COMPLETIONS_DIRECTORY = 2

completion_types = [
    (RX_CMD_LINE_CD, True),
    (RX_CMD_LINE_WRITE, True),
    (RX_CMD_LINE_EDIT, False),
]


def iter_paths(prefix=None, only_dirs=False):
    start_at = os.path.expandvars(os.path.expanduser(prefix))
    stuff = glob.iglob(start_at + "*")
    for path in glob.iglob(start_at + '*'):
        if not only_dirs or os.path.isdir(path):
            yield path


def parse(text):
    found = None
    for (pattern, only_dirs) in completion_types:
        found = pattern.search(text)
        if found:
            return found.groupdict()['cmd'], found.groupdict()['path'], only_dirs
    return (None, None, None)


def escape(path):
    return path.replace(' ', '\\ ')


def unescape(path):
    return path.replace('\\ ', ' ')


def wants_fs_completions(text):
    return parse(text)[0] is not None
