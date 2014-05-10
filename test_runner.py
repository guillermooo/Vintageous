import sublime
import sublime_plugin

import os
import unittest
import contextlib


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
    def __init__(self, name, file_regex='', line_regex='', base_dir=None,
                 word_wrap=False, line_numbers=False, gutter=False,
                 scroll_past_end=False,
                 syntax='Packages/Text/Plain text.tmLanguage',
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

    @contextlib.contextmanager
    def chdir(self, path=None):
        old_path = os.getcwd()
        if path is not None:
            assert os.path.exists(path), "'path' is invalid"
            os.chdir(path)
        yield
        if path is not None:
            os.chdir(old_path)

    def run(self, **kwargs):
        with self.chdir(kwargs.get('working_dir')):
            p = os.path.join(os.getcwd(), 'tests/')
            suite = unittest.TestLoader().discover(p)

            file_regex = r'^\s*File\s*"([^.].*?)",\s*line\s*(\d+),.*$'
            display = OutputPanel('vintageous.tests', file_regex=file_regex)
            display.show()
            runner = unittest.TextTestRunner(stream=display, verbosity=1)

            def run_and_display():
                runner.run(suite)
                display.show()

            sublime.set_timeout_async(run_and_display, 0)
