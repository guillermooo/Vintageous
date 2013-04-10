import sublime
import sublime_plugin

from itertools import chain
import io
import os
import unittest


TEST_DATA_PATH = None
TEST_DATA_FILE_BASENAME = 'sample.txt'

def plugin_loaded():
    global TEST_DATA_PATH
    TEST_DATA_PATH = os.path.join(sublime.packages_path(), '_Package Testing/%s' % TEST_DATA_FILE_BASENAME)


class TestsState(object):
    running = False
    view = None
    suite = None

    @staticmethod
    def reset():
        TestsState.view = None
        TestsState.suite = None


TESTS_SETTINGS = 'Vintageous.tests.vi.test_settings'
TESTS_REGISTERS = 'Vintageous.tests.vi.test_registers'
TESTS_MARKS = 'Vintageous.tests.vi.test_marks'
TESTS_STATE = 'Vintageous.tests.test_state'
TESTS_CONSTANTS = 'Vintageous.tests.vi.test_constants'
TESTS_CMD_DATA = 'Vintageous.tests.vi.test_cmd_data'


test_suites = {
        '_storage_': ['_pt_run_tests', [TESTS_MARKS, TESTS_SETTINGS, TESTS_REGISTERS, TESTS_CONSTANTS]],

        'settings': ['_pt_run_tests', [TESTS_SETTINGS]],
        'registers': ['_pt_run_tests', [TESTS_REGISTERS]],
        'marks': ['_pt_run_tests', [TESTS_MARKS]],

        'state': ['_pt_run_tests', [TESTS_STATE]],

        'constants': ['_pt_run_tests', [TESTS_CONSTANTS]],

        'cmd_data': ['_pt_run_tests', [TESTS_CMD_DATA]],
}


# Combine all tests under one key for convenience. Ignore keys starting with an underscore. Use
# these for subsets of all the remaining tests that you don't want repeated under '_all_'.
# Convert to list so the 'chain' doesn't get exhausted after the first use.
all_tests = list(chain(*[data[1] for (key, data) in test_suites.items() if not key.startswith('_')]))
test_suites['_all_'] = ['_pt_run_tests', all_tests]


class _ptPrintResults(sublime_plugin.TextCommand):
    def run(self, edit, content):
        view = sublime.active_window().new_file()
        view.insert(edit, 0, content)
        view.set_scratch(True)


class ShowVintageousTestSuites(sublime_plugin.WindowCommand):
    def run(self):
        TestsState.running = True
        self.window.show_quick_panel(sorted(test_suites.keys()), self.run_suite)

    def run_suite(self, idx):
        suite_name = sorted(test_suites.keys())[idx]
        TestsState.suite = suite_name
        command_to_run, _ = test_suites[suite_name]

        self.window.run_command(command_to_run, dict(suite_name=suite_name))


class _ptRunTests(sublime_plugin.WindowCommand):
    def run(self, suite_name):
        self.window.open_file(TEST_DATA_PATH)


class _ptTestDataDispatcher(sublime_plugin.EventListener):
    def on_load(self, view):
        if (view.file_name() and
            os.path.basename(view.file_name()) == TEST_DATA_FILE_BASENAME and
            TestsState.running):

                TestsState.running = False
                TestsState.view = view

                _, suite_names = test_suites[TestsState.suite]
                suite = unittest.TestLoader().loadTestsFromNames(suite_names)

                bucket = io.StringIO()
                unittest.TextTestRunner(stream=bucket, verbosity=1).run(suite)

                view.run_command('_pt_print_results', {'content': bucket.getvalue()})
                w = sublime.active_window()
                # Close data view.
                w.run_command('prev_view')
                w.run_command('close')
                # Ugly hack to return focus to the results view.
                w.run_command('show_panel', {'panel': 'console', 'toggle': True})
                w.run_command('show_panel', {'panel': 'console', 'toggle': True})
