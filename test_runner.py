import sublime
import sublime_plugin

import os
import unittest
import io

TEST_DATA_PATH = None
TEST_DATA_FILE_BASENAME = 'sample.txt'

def plugin_loaded():
    global TEST_DATA_PATH
    TEST_DATA_PATH = os.path.join(sublime.packages_path(), '_Package Testing/%s' % TEST_DATA_FILE_BASENAME)


class TestsState(object):
    view = None
    suite = None

    @staticmethod
    def reset():
        TestsState.view = None
        TestsState.suite = None

test_suites = {
        'settings': ['vintage_ex_run_data_file_based_tests', 'Vintageous.tests.settings.test_settings'],
        'registers': ['vintage_ex_run_data_file_based_tests', 'Vintageous.tests.vi.test_registers'],
        'marks': ['vintage_ex_run_data_file_based_tests', 'Vintageous.tests.vi.test_marks'],
        'state': ['vintage_ex_run_data_file_based_tests', 'Vintageous.tests.test_state'],
        'constants': ['vintage_ex_run_data_file_based_tests', 'Vintageous.tests.vi.test_constants'],
        'cmd_data': ['vintage_ex_run_data_file_based_tests', 'Vintageous.tests.vi.test_cmd_data'],
}


class PrintToBuffer(sublime_plugin.TextCommand):
    def run(self, edit, content):
        view = sublime.active_window().new_file()
        view.insert(edit, 0, content)
        view.set_scratch(True)


class ShowVintageousTestSuites(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_quick_panel(sorted(test_suites.keys()), self.run_suite)

    def run_suite(self, idx):
        suite_name = sorted(test_suites.keys())[idx]
        TestsState.suite = suite_name
        command_to_run, _ = test_suites[suite_name]

        self.window.run_command(command_to_run, dict(suite_name=suite_name))


class VintageExRunSimpleTestsCommand(sublime_plugin.WindowCommand):
    def run(self, suite_name):
        bucket = io.StringIO()
        _, suite = test_suites[suite_name]
        suite = unittest.defaultTestLoader.loadTestsFromName(suite)
        unittest.TextTestRunner(stream=bucket, verbosity=1).run(suite)

        self.window.active_view().run_command('print_to_buffer', {'content': bucket.getvalue()})


class VintageExRunDataFileBasedTests(sublime_plugin.WindowCommand):
    def run(self, suite_name):
        self.window.open_file(TEST_DATA_PATH)


class TestDataDispatcher(sublime_plugin.EventListener):
    def on_load(self, view):
        if view.file_name() and os.path.basename(view.file_name()) == TEST_DATA_FILE_BASENAME:
            TestsState.view = view

            _, suite_name = test_suites[TestsState.suite]
            suite = unittest.TestLoader().loadTestsFromName(suite_name)

            bucket = io.StringIO()
            unittest.TextTestRunner(stream=bucket, verbosity=1).run(suite)

            view.run_command('print_to_buffer', {'content': bucket.getvalue()})
            w = sublime.active_window()
            w.run_command('prev_view')
            w.run_command('close')
