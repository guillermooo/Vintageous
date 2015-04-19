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
    '''
    Runs tests:

    - from a file with the name 'test_<active_file_basename>' if it exists,
    - from a file with the .cmd-test[-solo] extension,
    - else, from the active file.
    '''

    def run(self):
        v = self.window.active_view()
        if v is None:
            return

        proj_path = find_project_path(v.file_name())
        if not proj_path or not v.file_name().endswith(('.py', '.cmd-test', '.cmd-test-solo')):
            print(
                'Vintageous (Dev): Not a project, cmd-test or python file: '
                + v.file_name())
            return

        # If it's a test_* file, run it.
        if os.path.basename(v.file_name()).startswith('test_'):
            self.window.run_command('run_vintageous_tests', {
                'active_file_only': True,
                'working_dir': proj_path
                })
            return

        # If it's a normal file, try to find its tests.
        tail = os.path.join('tests', v.file_name()[len(proj_path) + 1:])
        full = os.path.join(proj_path, os.path.dirname(tail),
                            'test_' + os.path.basename(tail))
        if os.path.exists(full):
            self.window.run_command('run_vintageous_tests', {
                'loader_pattern': os.path.basename(full),
                'working_dir': proj_path
                })
            return

        # Otherwise just run it.
        self.window.run_command('run_vintageous_tests', {
            'active_file_only': True,
            'working_dir': proj_path
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
