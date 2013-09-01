import sublime
import sublime_plugin

import glob
import os
import re

RX_CMD_LINE_CD = re.compile(r'^(?P<cmd>:\s*cd!?)\s+(?P<path>.*)$')
RX_CMD_LINE_WRITE = re.compile(r'^(?P<cmd>:\s*w(?:rite)?!?)\s+(?P<path>.*)$')
RX_CMD_LINE_EDIT = re.compile(r'^(?P<cmd>:\s*e(?:dit)?!?)\s+(?P<path>.*)$')
RX_CMD_LINE_VSPLIT = re.compile(r'^(?P<cmd>:\s*vs(?:plit)?!?)\s+(?P<path>.*)$')


COMPLETIONS_FILE = 1
COMPLETIONS_DIRECTORY = 2

completion_types = [
    (RX_CMD_LINE_CD, True),
    (RX_CMD_LINE_WRITE, True),
    (RX_CMD_LINE_EDIT, False),
    (RX_CMD_LINE_VSPLIT, False),
]

RX_CMD_LINE_SET_LOCAL = re.compile(r'^(?P<cmd>:\s*setl(?:ocal)?\??)\s+(?P<setting>.*)$')
RX_CMD_LINE_SET_GLOBAL = re.compile(r'^(?P<cmd>:\s*se(?:t)?\??)\s+(?P<setting>.*)$')


completion_settings = [
    (RX_CMD_LINE_SET_LOCAL, None),
    (RX_CMD_LINE_SET_GLOBAL, None),
]


def iter_paths(prefix=None, from_dir=None, only_dirs=False):
    if prefix:
        start_at = os.path.expandvars(os.path.expanduser(prefix))
        # TODO: implement env var completion.
        if not prefix.startswith(('%', '$', '~')):
            start_at = os.path.join(from_dir, prefix)
            start_at = os.path.expandvars(os.path.expanduser(start_at))

        prefix_split = os.path.split(prefix)
        prefix_len = len(prefix_split[1])
        if ('/' in prefix and not prefix_split[0]):
            prefix_len = 0

        for path in glob.iglob(start_at + '*'):
            if not only_dirs or os.path.isdir(path):
                suffix = ('/' if os.path.isdir(path) else '')
                item = os.path.split(path)[1]
                yield prefix + (item + suffix)[prefix_len:]
    else:
        prefix = from_dir
        start_at = os.path.expandvars(os.path.expanduser(prefix))
        stuff = glob.iglob(start_at + "*")
        for path in glob.iglob(start_at + '*'):
            if not only_dirs or os.path.isdir(path):
                yield path[len(start_at):] + ('' if not os.path.isdir(path) else '/')


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


def parse_for_setting(text):
    found = None
    for (pattern, _) in completion_settings:
        found = pattern.search(text)
        if found:
            return found.groupdict()['cmd'], found.groupdict().get('setting'), None
    return (None, None, None)


def wants_setting_completions(text):
    return parse_for_setting(text)[0] is not None
