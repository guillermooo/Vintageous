import sublime
import sublime_plugin

from itertools import chain
import io
import os
import unittest
import tempfile


# A tuple: (low level file_descriptor, path) as returned by `tempfile.mkstemp()`.
TEST_DATA_PATH = None


def make_temp_file():
    """Creates an new temporary file.
    """
    global TEST_DATA_PATH
    TEST_DATA_PATH = tempfile.mkstemp()


class TestsState(object):
    running = False
    view = None
    suite = None

    @staticmethod
    def reset():
        TestsState.view = None
        TestsState.suite = None

    @staticmethod
    def reset_view_state():
        TestsState.view.settings().set('vintage', {})
        TestsState.view.sel().clear()
        TestsState.view.sel().add(sublime.Region(0, 0))


TESTS_SETTINGS = 'Vintageous.tests.vi.test_settings'
TESTS_REGISTERS = 'Vintageous.tests.vi.test_registers'
TESTS_MARKS = 'Vintageous.tests.vi.test_marks'
TESTS_STATE = 'Vintageous.tests.test_state'
TESTS_CONSTANTS = 'Vintageous.tests.vi.test_constants'
TESTS_CMD_DATA = 'Vintageous.tests.vi.test_cmd_data'
TESTS_KEYMAP = 'Vintageous.tests.test_keymap'
TESTS_RUN = 'Vintageous.tests.test_run'

TESTS_CMDS_SET_ACTION = 'Vintageous.tests.commands.test_set_action'
TESTS_CMDS_SET_MOTION = 'Vintageous.tests.commands.test_set_motion'
TESTS_CMDS_MOTION_VI_L = 'Vintageous.tests.commands.test__vi_l'
TESTS_CMDS_MOTION_VI_H = 'Vintageous.tests.commands.test__vi_h'
TESTS_CMDS_MOTION_VI_BIG_G = 'Vintageous.tests.commands.test__vi_big_g'
TESTS_CMDS_MOTION_VI_DOLLAR = 'Vintageous.tests.commands.test__vi_dollar'
TESTS_CMDS_MOTION_VI_J = 'Vintageous.tests.commands.test__vi_j'
TESTS_CMDS_MOTION_VI_K = 'Vintageous.tests.commands.test__vi_k'
TESTS_CMDS_MOTION_VI_E = 'Vintageous.tests.commands.test__vi_e'
TESTS_CMDS_MOTION_VI_BIG_F = 'Vintageous.tests.commands.test__vi_big_f'
TESTS_CMDS_ACTION_CTRL_X = 'Vintageous.tests.commands.test__ctrl_x_and__ctrl_a'
TESTS_CMDS_ACTION_VI_CC = 'Vintageous.tests.commands.test__vi_cc'
TESTS_CMDS_ACTION_VI_BIG_S = 'Vintageous.tests.commands.test__vi_big_s'

TESTS_EX_CMDS_COPY = 'Vintageous.tests.ex.test_copy'
TESTS_EX_CMDS_MOVE = 'Vintageous.tests.ex.test_move'
TESTS_EX_CMDS_DELETE = 'Vintageous.tests.ex.test_delete'

TESTS_UNITS_WORD = 'Vintageous.tests.vi.test_word'
TESTS_UNITS_BIG_WORD = 'Vintageous.tests.vi.test_big_word'
TESTS_UNITS_WORD_END = 'Vintageous.tests.vi.test_word_end'

TESTS_CMDS_ALL_SUPPORT = [TESTS_CMDS_SET_ACTION, TESTS_CMDS_SET_MOTION]

TESTS_CMDS_ALL_ACTIONS = [TESTS_CMDS_ACTION_CTRL_X,
                          TESTS_CMDS_ACTION_VI_CC,
                          ]

TESTS_CMDS_ALL_MOTIONS = [TESTS_CMDS_MOTION_VI_L,
                          TESTS_CMDS_MOTION_VI_H,
                          TESTS_CMDS_MOTION_VI_BIG_G,
                          TESTS_CMDS_MOTION_VI_DOLLAR,
                          TESTS_CMDS_MOTION_VI_J,
                          TESTS_CMDS_MOTION_VI_K,
                          TESTS_CMDS_MOTION_VI_E,
                          TESTS_CMDS_MOTION_VI_BIG_F,
                          TESTS_CMDS_ACTION_VI_BIG_S,
                          ]

TESTS_EX_CMDS = [
    TESTS_EX_CMDS_COPY,
    TESTS_EX_CMDS_MOVE,
    TESTS_EX_CMDS_DELETE,
]

TESTS_UNITS_ALL = [TESTS_UNITS_WORD,
                   TESTS_UNITS_BIG_WORD,
                   TESTS_UNITS_WORD_END,
                  ]

TESTS_CMDS_ALL = TESTS_CMDS_ALL_MOTIONS + TESTS_CMDS_ALL_ACTIONS + TESTS_CMDS_ALL_SUPPORT


test_suites = {
        '_storage_': ['_pt_run_tests', [TESTS_MARKS, TESTS_SETTINGS, TESTS_REGISTERS, TESTS_CONSTANTS]],

        'settings': ['_pt_run_tests', [TESTS_SETTINGS]],
        'registers': ['_pt_run_tests', [TESTS_REGISTERS]],
        'marks': ['_pt_run_tests', [TESTS_MARKS]],

        'state': ['_pt_run_tests', [TESTS_STATE]],
        'run': ['_pt_run_tests', [TESTS_RUN]],

        'constants': ['_pt_run_tests', [TESTS_CONSTANTS]],

        'cmd_data': ['_pt_run_tests', [TESTS_CMD_DATA]],

        'keymap': ['_pt_run_tests', [TESTS_KEYMAP]],

        'commands': ['_pt_run_tests', TESTS_CMDS_ALL],

        'units': ['_pt_run_tests', TESTS_UNITS_ALL],

        'ex_cmds': ['_pt_run_tests', TESTS_EX_CMDS],
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
    """Displays a quick panel listing all available test stuites.
    """
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
        make_temp_file()
        # We open the file here, but Sublime Text loads it asynchronously, so we continue in an
        # event handler, once it's been fully loaded.
        self.window.open_file(TEST_DATA_PATH[1])


class _ptTestDataDispatcher(sublime_plugin.EventListener):
    def on_load(self, view):
        try:
            if (view.file_name() and view.file_name() == TEST_DATA_PATH[1] and
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
                    TestsState.view.set_scratch(True)
                    w.run_command('close')
                    w.run_command('next_view')
                    # Ugly hack to return focus to the results view.
                    w.run_command('show_panel', {'panel': 'console', 'toggle': True})
                    w.run_command('show_panel', {'panel': 'console', 'toggle': True})
        except Exception as e:
            print(e)
        finally:
            try:
                os.close(TEST_DATA_PATH[0])
            except Exception as e:
                print("Could not close temp file...")
                print(e)


class WriteToBuffer(sublime_plugin.TextCommand):
    """Replaces the buffer's content with the specified `text`.

       `text`: Text to be written to the buffer.
       `file_name`: If this file name does not match the receiving view's, abort.
    """
    def run(self, edit, file_name='', text=''):
        if not file_name:
            return

        if self.view.file_name().lower() == file_name.lower():
            self.view.replace(edit, sublime.Region(0, self.view.size()), text)
