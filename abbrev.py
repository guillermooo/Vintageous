"""
Abbreviations.
"""

import sublime
import sublime_plugin

import os
import json


def abbrevs_path():
    path = os.path.join(sublime.packages_path(),
                        'User/_vintageous_abbrev.sublime-completions')
    return os.path.normpath(path)


def get_json(path):
    decoded_json = None
    if os.path.exists(path):
        with open(path, 'r') as f:
            decoded_json = json.load(f)
    return decoded_json or {'completions': []}


def set_json(path, data):
    # TODO: Make entries temporary unless !mksession is used or something like that.
    # TODO: Enable contexts for abbrevs?
    with open(path, 'w') as f:
        decoded = json.dump(data, f)


class Store(object):
    def set(self, short, full):
        data = get_json(abbrevs_path())
        idx = self.contains(data, short)
        if idx is not None:
            data['completions'][idx] = dict(trigger=short, contents=full)
        else:
            data['completions'].append(dict(trigger=short, contents=full))
        set_json(abbrevs_path(), data)

    def get(self, short):
        raise NotImplementedError()

    def get_all(self):
        data = get_json(abbrevs_path())
        for item in data['completions']:
            yield item['trigger'] + ' --> ' + item['contents']

    def contains(self, data, short):
        for (i, completion) in enumerate(data['completions']):
            if completion['trigger'] == short:
                return i
        return None

    def erase(self, short):
        data = get_json(abbrevs_path())
        idx = self.contains(data, short)
        if idx is not None:
            del data['completions'][idx]
            set_json(abbrevs_path(), data)
