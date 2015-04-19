from threading import Thread
import contextlib
import os
import unittest

import sublime
import sublime_plugin


class __vi_tests_write_buffer(sublime_plugin.TextCommand):
    """Replaces the buffer's content with the specified `text`.

       `text`: Text to be written to the buffer.
    """
    def run(self, edit, text=''):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)


class __vi_tests_erase_all(sublime_plugin.TextCommand):
    """Replaces the buffer's content with the specified `text`.
    """
    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))


class OutputPanel(object):
    def __init__(self, name,
            file_regex='',
            line_regex='',
            base_dir=None,
            word_wrap=False,
            line_numbers=False,
            gutter=False,
            scroll_past_end=False,
            syntax='',
            ):

        self.name = name
        self.window = sublime.active_window()

        if not hasattr(self, 'output_view'):
            # Try not to call get_output_panel until the regexes are assigned
            self.output_view = self.window.create_output_panel(self.name)

        # Default to the current file directory
        if (not base_dir and self.window.active_view() and
            self.window.active_view().file_name()):
                base_dir = os.path.dirname(
                        self.window.active_view().file_name()
                        )

        self.output_view.settings().set('result_file_regex', file_regex)
        self.output_view.settings().set('result_line_regex', line_regex)
        self.output_view.settings().set('result_base_dir', base_dir)
        self.output_view.settings().set('word_wrap', word_wrap)
        self.output_view.settings().set('line_numbers', line_numbers)
        self.output_view.settings().set('gutter', gutter)
        self.output_view.settings().set('scroll_past_end', scroll_past_end)
        self.output_view.settings().set('syntax', syntax)

        # Call create_output_panel a second time after assigning the above
        # settings, so that it'll be picked up as a result buffer
        self.window.create_output_panel(self.name)

    def write(self, s):
        f = lambda: self.output_view.run_command('append', {'characters': s})
        sublime.set_timeout(f, 0)

    def flush(self):
        pass

    def show(self):
        self.window.run_command(
                            'show_panel', {'panel': 'output.' + self.name}
                            )

    def close(self):
        pass


class RunVintageousTests(sublime_plugin.WindowCommand):
    '''
    Runs tests and displays the results.

    - Do not use Sublime Text while tests are running.

    @working_dir
      Required. Should be the parent of the top-level directory for `tests`.

    @loader_pattern
      Optional. Only run tests matching this glob.

    @tests_dir
      Name of the directory containing tests.

    @active_file_only
      Optional. Only run tests in the active file in ST. Shadows
      @loader_pattern.

    To use this runner conveniently, open the command palette and select one
    of the `Build: Vintageous - Test *` commands.
    '''

    def run(self, working_dir,
            loader_pattern="test*.py",
            tests_dir="tests",
            **kwargs):
        assert os.path.exists(working_dir), 'working_dir must exist'

        with self.chdir(working_dir):
            p = os.path.join(os.getcwd(), tests_dir)

            patt = loader_pattern
            # TODO(guillermooo): I can't get $file to expand in the build
            # system. It should be possible to make the following code simpler
            # with it.
            if kwargs.get('active_file_only') is True:
                patt = os.path.basename(self.window.active_view().file_name())
                # run text-based tests
                if patt.endswith(('.cmd-test', '.cmd-test-solo')):
                    patt = 'test_all_cmds.py'
            suite = unittest.TestLoader().discover(p, pattern=patt)

            file_regex = r'^\s*File\s*"([^.].*?)",\s*line\s*(\d+),.*$'
            display = OutputPanel('vintageous.tests',
                    file_regex=file_regex,
                    word_wrap=True
                    )

            display.show()
            runner = unittest.TextTestRunner(stream=display, verbosity=1)

            def run_and_display():
                runner.run(suite)
                # XXX: If we don't do this, custom mappings won't be available
                # after running the test suite.
                self.window.run_command('reset_vintageous')

            Thread(target=run_and_display).start()

    @contextlib.contextmanager
    def chdir(self, path=None):
        old_path = os.getcwd()
        if path:
            assert os.path.exists(path), "'path' is invalid {}".format(path)
            os.chdir(path)
        yield
        if path is not None:
            os.chdir(old_path)
