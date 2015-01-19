from collections import defaultdict
import glob
import os
import unittest

import sublime


TEST_DELIM = '\n---///---\n'
TEST_HEADER_DELIM = '***\n'
TEST_RESULTS_DELIM = '\n---\n'

_converters = defaultdict(lambda: (lambda x: str(x)))
_converters ['mode'] = str
_converters ['count'] = int


def _make_args(args):
    arg_dict = {}
    for a in args:
        name, value = a.split(':')
        arg_dict[name] = _converters[name](value)
    return arg_dict


class ViCmdTest (object):

    def __init__(self, cmd_name, args, description,
                before_text, after_text, file_name, test_nr):
        self.cmd_name = cmd_name
        self.args = args
        self.description = description
        self.before_text = before_text
        self.after_text = after_text
        self.file_name = file_name
        self.test_nr = test_nr

    @property
    def message(self):
        return "Failure in File: {0} Test Nr.: {1} -- {2}".format(self.file_name,
                self.test_nr, self.description)

    @staticmethod
    def from_text(text, file_name, test_nr):
        ''' creates a test instance from a textual representation
        '''
        header, body = text.split(TEST_HEADER_DELIM, 1)
        header, description = header.split('\n', 1)
        cmd_name, args = header.split(' ', 1)
        args = _make_args(args.split())
        before, after = body.split(TEST_RESULTS_DELIM)
        return ViCmdTest(cmd_name, args, description, before, after,
            file_name, test_nr)


class ViCmdTester (unittest.TestCase):
    """
    Runs tests based in cmd-test spec files (cmd-test).

    Subclasses must implement setUp() and in it set self.path_to_test_specs.
    """

    def get_tests(self):
        """
        Yields `ViCmdTest`s found under the self.path_to_test_specs dir.
        """
        specs = glob.glob(os.path.join(self.path_to_test_specs, "*.cmd-test-solo"))
        if specs:
            specs = specs[0:1]
        else:
            specs = glob.glob(os.path.join(self.path_to_test_specs, "*.cmd-test"))

        for s in specs:
            s = os.path.abspath(s)
            content = None
            with open(s, 'rt') as f:
                content = f.read()
            tests = content.split(TEST_DELIM)
            for i, t in enumerate(tests):
                yield ViCmdTest.from_text(t, s, i)

    def append(self, text):
        self.view.run_command('append', {'characters': text})

    def reset(self):
        if getattr(self, "view", None):
            self.view.close()
        self.view = sublime.active_window().new_file()
        self.view.set_scratch(True)

    def set_sels(self):
        """
        Enables adding selections to the buffer text using a minilanguage:

        S = add empty sel before S and delete S
        x = add empty sel before x
        v = add sel from before the first 'v' to after the last contiguous 'v'
        """
        self.view.sel().clear()

        normal_mode_regs = self.view.find_all(r'x')
        for nmr in normal_mode_regs:
            self.view.sel().add(sublime.Region(nmr.a))

        if len(self.view.sel()) > 0:
            return

        visual_mode_regs = self.view.find_all(r'v+')
        for vmr in visual_mode_regs:
            self.view.sel().add(vmr)

        if len(self.view.sel()) > 0:
            return

        visual_mode_regs = self.view.find_all(r'S')
        for vmr in visual_mode_regs:
            self.view.sel().add(sublime.Region(vmr.a))
            self.view.run_command('right_delete')
