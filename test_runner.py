import sublime
import sublime_plugin

from itertools import chain
import io
import os
import unittest
import tempfile
import contextlib


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
TESTS_KEYS = 'Vintageous.tests.vi.test_keys'
TESTS_MAPPINGS = 'Vintageous.tests.vi.test_mappings'

TESTS_TEXT_OBJECTS = 'Vintageous.tests.vi.test_text_objects'
TESTS_TEXT_OBJECTS_A_WORD = 'Vintageous.tests.vi.test_a_word'
TESTS_TEXT_OBJECTS_PARAGRAPH = 'Vintageous.tests.vi.test_find_paragraph_text_object'

TESTS_CMDS_SET_MOTION = 'Vintageous.tests.commands.test_set_motion'
TESTS_CMDS_MOTION_VI_L = 'Vintageous.tests.commands.test__vi_l'
TESTS_CMDS_MOTION_VI_H = 'Vintageous.tests.commands.test__vi_h'
TESTS_CMDS_MOTION_VI_BIG_G = 'Vintageous.tests.commands.test__vi_big_g'
TESTS_CMDS_MOTION_VI_G_G = 'Vintageous.tests.commands.test__vi_g_g'
TESTS_CMDS_MOTION_VI_DOLLAR = 'Vintageous.tests.commands.test__vi_dollar'
TESTS_CMDS_MOTION_VI_J = 'Vintageous.tests.commands.test__vi_j'
TESTS_CMDS_MOTION_VI_K = 'Vintageous.tests.commands.test__vi_k'
TESTS_CMDS_MOTION_VI_E = 'Vintageous.tests.commands.test__vi_e'
TESTS_CMDS_MOTION_VI_BIG_F = 'Vintageous.tests.commands.test__vi_big_f'
TESTS_CMDS_MOTION_VI_PERCENT = 'Vintageous.tests.commands.test__vi_percent'
TESTS_CMDS_MOTION_VI_ANTILAMBDA = 'Vintageous.tests.commands.test__vi_antilambda'
TESTS_CMDS_MOTION_VI_ZERO = 'Vintageous.tests.commands.test__vi_zero'
TESTS_CMDS_ACTION_CTRL_X = 'Vintageous.tests.commands.test__ctrl_x_and__ctrl_a'
TESTS_CMDS_ACTION_VI_S = 'Vintageous.tests.commands.test__vi_s'
TESTS_CMDS_ACTION_VI_BIG_I = 'Vintageous.tests.commands.test__vi_big_i'
TESTS_CMDS_ACTION_VI_BIG_A = 'Vintageous.tests.commands.test__vi_big_a'
TESTS_CMDS_ACTION_VI_CC = 'Vintageous.tests.commands.test__vi_cc'
TESTS_CMDS_ACTION_VI_BIG_S = 'Vintageous.tests.commands.test__vi_big_s'
TESTS_CMDS_MOTION_VI_VISUAL_O = 'Vintageous.tests.commands.test__vi_visual_o'
TESTS_CMDS_ACTION_VI_DD = 'Vintageous.tests.commands.test__vi_dd'
TESTS_CMDS_ACTION_VI_BIG_J = 'Vintageous.tests.commands.test__vi_big_j'

TESTS_EX_CMDS_COPY = 'Vintageous.tests.ex.test_copy'
TESTS_EX_CMDS_MOVE = 'Vintageous.tests.ex.test_move'
# TESTS_EX_CMDS_DELETE = 'Vintageous.tests.ex.test_delete'
# TESTS_EX_CMDS_SHELL_OUT = 'Vintageous.tests.ex.test_shell_out'

TESTS_UNITS_WORD = 'Vintageous.tests.vi.test_word'
TESTS_UNITS_BIG_WORD = 'Vintageous.tests.vi.test_big_word'
TESTS_UNITS_WORD_END = 'Vintageous.tests.vi.test_word_end'

TESTS_CMDS_ALL_SUPPORT = [TESTS_CMDS_SET_MOTION]

TESTS_CMDS_ALL_ACTIONS = [
    TESTS_CMDS_ACTION_CTRL_X,
    TESTS_CMDS_ACTION_VI_CC,
    # TESTS_CMDS_ACTION_VI_S,
    TESTS_CMDS_ACTION_VI_BIG_I,
    TESTS_CMDS_ACTION_VI_BIG_A,
    TESTS_CMDS_ACTION_VI_DD,
    TESTS_CMDS_ACTION_VI_BIG_J,
    ]

TESTS_CMDS_ALL_MOTIONS = [
    TESTS_CMDS_MOTION_VI_L,
    TESTS_CMDS_MOTION_VI_H,
    TESTS_CMDS_MOTION_VI_BIG_G,
    TESTS_CMDS_MOTION_VI_G_G,
    TESTS_CMDS_MOTION_VI_DOLLAR,
    TESTS_CMDS_MOTION_VI_J,
    TESTS_CMDS_MOTION_VI_K,
    TESTS_CMDS_MOTION_VI_E,
    TESTS_CMDS_MOTION_VI_BIG_F,
    TESTS_CMDS_ACTION_VI_BIG_S,
    TESTS_CMDS_MOTION_VI_VISUAL_O,
    TESTS_CMDS_MOTION_VI_PERCENT,
    TESTS_CMDS_MOTION_VI_ANTILAMBDA,
    TESTS_CMDS_MOTION_VI_ZERO,
  ]

TESTS_ALL_TEXT_OBJECTS = [
    TESTS_TEXT_OBJECTS,
    TESTS_TEXT_OBJECTS_A_WORD,
    TESTS_TEXT_OBJECTS_PARAGRAPH,
]

TESTS_EX_CMDS = [
    TESTS_EX_CMDS_COPY,
    TESTS_EX_CMDS_MOVE,
    # TESTS_EX_CMDS_DELETE,
    # TESTS_EX_CMDS_SHELL_OUT,
]

TESTS_UNITS_ALL = [TESTS_UNITS_WORD,
                   TESTS_UNITS_BIG_WORD,
                   TESTS_UNITS_WORD_END,]


TESTS_CMDS_ALL = TESTS_CMDS_ALL_MOTIONS + TESTS_CMDS_ALL_ACTIONS + TESTS_CMDS_ALL_SUPPORT + TESTS_EX_CMDS


test_suites = {
        '_storage_': ['_pt_run_tests', [TESTS_MARKS,
                                        TESTS_SETTINGS,
                                        TESTS_REGISTERS]],

        'settings': ['_pt_run_tests', [TESTS_SETTINGS]],
        'registers': ['_pt_run_tests', [TESTS_REGISTERS]],
        'marks': ['_pt_run_tests', [TESTS_MARKS]],

        'state': ['_pt_run_tests', [TESTS_STATE]],
        'keys': ['_pt_run_tests', [TESTS_KEYS, TESTS_MAPPINGS]],

        'commands': ['_pt_run_tests', TESTS_CMDS_ALL],

        'units': ['_pt_run_tests', TESTS_UNITS_ALL],

        'ex_cmds': ['_pt_run_tests', TESTS_EX_CMDS],

        # '_sel_': ['_pt_run_tests', TESTS_SEL_RELATED],

        'objects': ['_pt_run_tests', TESTS_ALL_TEXT_OBJECTS],
}


# Combine all tests under one key for convenience. Ignore keys starting with an underscore. Use
# these for subsets of all the remaining tests that you don't want repeated under '_all_'.
# Convert to list so the 'chain' doesn't get exhausted after the first use.
all_tests = list(chain(*[data[1] for (key, data) in test_suites.items() if not key.startswith('_')]))
test_suites['_all_'] = ['_pt_run_tests', all_tests]


class ShowVintageousTestSuites(sublime_plugin.WindowCommand):
    """Displays a quick panel listing all available test stuites.
    """
    def run(self):
        TestsState.running = True
        self.window.show_quick_panel(sorted(test_suites.keys()), self.run_suite)

    def run_suite(self, idx):
      if idx == -1:
        return

      suite_name = sorted(test_suites.keys())[idx]
      TestsState.suite = suite_name
      command_to_run, _ = test_suites[suite_name]

      self.window.run_command(command_to_run, dict(suite_name=suite_name))


class _ptRunTests(sublime_plugin.WindowCommand):
    def run(self, suite_name):
        _, suite_names = test_suites[TestsState.suite]
        suite = unittest.TestLoader().loadTestsFromNames(suite_names)
        # path = os.path.join(sublime.packages_path(), 'Vintageous.tests')
        # suite = unittest.TestLoader().discover(path)

        bucket = OutputPanel('vintageous.tests')
        bucket.show()
        runner = unittest.TextTestRunner(stream=bucket, verbosity=1)
        sublime.set_timeout_async(lambda: runner.run(suite), 0)


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
        self.window.create_output_panel('exec')

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
            suite = unittest.TestLoader().discover(os.getcwd())
            print("HELLO WORLD FROM BUILD SYSTEM")

            display = OutputPanel('vintageous.tests')
            display.show()
            runner = unittest.TextTestRunner(stream=display, verbosity=1)

            def run_and_display():
                runner.run(suite)
                display.show()

            sublime.set_timeout_async(run_and_display, 0)
