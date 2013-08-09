import sublime
import sublime_plugin

import glob
import os
import re

RX_CMD_LINE_CD = re.compile(r'^(?P<cmd>:\s*cd)\s+(?P<path>.*)$')
RX_CMD_LINE_WRITE = re.compile(r'^(?P<cmd>:\s*w)\s+(?P<path>.*)$')
RX_CMD_LINE_EDIT = re.compile(r'^(?P<cmd>:\s*e)\s+(?P<path>.*)$')

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


# class WriteFsCompletion(sublime_plugin.TextCommand):
#     def run(self, edit, cmd, completion):
#         OpenTestInputBox.receiving_user_input = False
#         self.view.sel().clear()
#         self.view.replace(edit, sublime.Region(0, self.view.size()),
#                           cmd + ' ' + escape(completion))
#         self.view.sel().add(sublime.Region(self.view.size()))


# class FsCompletion(sublime_plugin.TextCommand):
#     current_prefix = ''
#     must_recalculate = False
#     dirs = None

#     def run(self, edit):
#         if self.view.score_selector(0, 'text.excmdline') == 0:
#             return

#         cmd, prefix = parse(self.view.substr(self.view.line(0)))
#         if not cmd:
#             return
#         if not FsCompletion.current_prefix and prefix:
#             FsCompletion.current_prefix = prefix
#             FsCompletion.must_recalculate = True
#         elif not FsCompletion.current_prefix:
#             FsCompletion.current_prefix = os.getcwd() + '/'

#         if not FsCompletion.dirs or FsCompletion.must_recalculate:
#             FsCompletion.dirs = iter_paths(FsCompletion.current_prefix,
#                                            only_dirs=True)
#             FsCompletion.must_recalculate = False

#         try:
#             self.view.run_command('write_fs_completion',
#                                   { 'cmd': cmd,
#                                     'completion': next(FsCompletion.dirs)})
#         except StopIteration:
#             try:
#                 FsCompletion.dirs = iter_paths(FsCompletion.current_prefix,
#                                                only_dirs=True)
#                 self.view.run_command('write_fs_completion',
#                                       { 'cmd': cmd,
#                                         'completion': next(FsCompletion.dirs)})
#             except StopIteration:
#                 return


# class OpenTestInputBox(sublime_plugin.WindowCommand):
#     receiving_user_input = True
#     def run(self):
#         v = self.window.show_input_panel('Test', '',
#                                          None,
#                                          self.on_change,
#                                          None)
#         v.set_syntax_file('Packages/User/Dummy.tmLanguage')

#     def on_change(self, s):
#         print("FuCK")
#         if OpenTestInputBox.receiving_user_input:
#             cmd, prefix = parse(unescape(s))
#             if not cmd:
#                 return
#             FsCompletion.current_prefix = prefix
#             FsCompletion.must_recalculate = True
#             print("XXX", FsCompletion.current_prefix)
#         OpenTestInputBox.receiving_user_input = True
