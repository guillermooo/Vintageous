import sublime
import sublime_plugin

import os


def find_project_path(path):
    while True:
        if not path or os.path.exists(os.path.join(path,
            'Vintageous.sublime-project')):
                return path

        path = os.path.dirname(path)


class RunTestsForActiveViewCommand(sublime_plugin.WindowCommand):
    '''This command only exists because we can't expand ${project_path}
    in keymap files.
    '''
    def run(self):
        v = self.window.active_view()
        if v is None:
            return

        self.window.run_command('run_vintageous_tests', {
            'active_file_only': True,
            'working_dir': find_project_path(v.file_name())
            })


class RunAllTestsCommand(sublime_plugin.WindowCommand):
    '''This command only exists because we can't expand ${project_path}
    in keymap files.
    '''
    def run(self):
        v = self.window.active_view()
        if v is None:
            return

        self.window.run_command('run_vintageous_tests', {
            'working_dir': find_project_path(v.file_name())
            })
