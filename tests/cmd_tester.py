'''
Tools for testing commands.

Command tests are declared in a special text format in files with the .cmd-test extension.
Several tests can be declared in the same file. This makes it easier to group tests.

Special attention must be payed to whitespace: it counts for tests.
'''

from collections import defaultdict
import glob
import os
import unittest

import sublime


# Comes after the header.
TEST_HEADER_DELIM = '***\n'
# Delimits tests.
TEST_DELIM = '\n---///---\n'
# Separates the test declaration from the expected result.
TEST_RESULTS_DELIM = '\n---\n'


_converters = defaultdict(lambda: (lambda x: str(x)))
_converters ['mode'] = str
_converters ['count'] = int


def _make_args(args):
    arg_dict = {}
    for a in args:
        name, value = a.split(':', 1)
        arg_dict[name] = _converters[name](value)
    return arg_dict


def process_notation(text, sel_start_token='^', sel_end_token='$'):
    '''
    Processes @text assuming it contains markers defining selections.

    @text
      Text that contains @sel_start_token's and @sel_end_token's to define
      selection regions.

    @sel_start_token
      Marks the start of a selection region. Removed from the test.

    @sel_end_token
      Marks the end of a selection region. Removed from the text.

    Reversed selections can be defined too.

    Returns (selections, processed_text), where `selections` are valid ST
            ranges, and `processed_text` is @text without the special symbols.
    '''
    deletions = 0
    start = None
    selections = []
    chars = []

    pos = 0
    while pos < len(text):
        c = text[pos]
        if c == sel_start_token:
            if start == sel_start_token:
                raise ValueError('unexpected token %s at %d', c, pos)
            if start is None:
                start = pos - deletions
            else:
                selections.append(sublime.Region(start, pos - deletions))
                start = None
            deletions += 1
        elif c == sel_end_token:
            if start == sel_end_token:
                raise ValueError('unexpected token %s at %d', c, pos)
            if start is None:
                start = pos - deletions
            else:
                selections.append(sublime.Region(start, pos - deletions))
                start = None
            deletions += 1
        else:
            chars.append(c)
        pos += 1

    if start is not None:
        raise ValueError('wrong format, orphan ^ at %d', start + deletions)
    return selections, ''.join(chars)


class ViCmdTest (object):

    def __init__(self, cmd_name, args, description,
                before_text, after_text, file_name, test_nr, options=None):
        self.cmd_name = cmd_name
        self.args = args
        self.description = description
        self.before_text = before_text
        self.after_text = after_text
        self.file_name = file_name
        self.test_nr = test_nr
        self.options = options

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
        description, options = ViCmdTest.process_description(description)
        cmd_name, args = header.split(' ', 1)
        args = _make_args(args.split())
        assert 'mode' in args, 'all commands need to know the current mode'
        before, after = body.split(TEST_RESULTS_DELIM)
        return ViCmdTest(cmd_name, args, description, before, after,
            file_name, test_nr, options)

    @staticmethod
    def process_description(text):
        lines = text.split('\n')
        description = lines
        options_line = lines[0]

        opts = {}
        if options_line.startswith('//options: '):
            description = lines[1:]
            raw_opts = options_line[11:].split()
            opts = _make_args(raw_opts)

        return '\n'.join(description), opts


    def run_with(self, runner):
        before_sels, before_text = process_notation(self.before_text)
        runner.append(before_text)
        runner.set_sels(before_sels)

        view = runner.view
        view.run_command(self.cmd_name, self.args)

        after_sels, after_text = process_notation(self.after_text)

        runner.assertEqual(view.substr(sublime.Region(0, view.size())),
                after_text, self.message)

        runner.assertEqual(list(view.sel()), after_sels, self.message)

class ViCmdTester (unittest.TestCase):
    '''
    Runs tests based in cmd-test spec files (cmd-test).

    Subclasses must implement setUp() and in it set self.path_to_test_specs.
    '''

    def get_motion_tests(self):
        specs = self.get_tests("*.motion-test")
        return specs

    def get_action_tests(self):
        specs = self.get_tests("*.cmd-test")
        return specs

    def get_tests(self, ext):
        """
        Yields `ViCmdTest`s found under the self.path_to_test_specs dir.
        """
        specs = glob.glob(os.path.join(self.path_to_test_specs, ext + "-solo"))
        if specs:
            specs = specs[0:1]
        else:
            specs = glob.glob(os.path.join(self.path_to_test_specs, ext))
        return specs

    def iter_tests(self):
        specs = self.get_motion_tests() + self.get_action_tests()
        for spec_path in specs:
            spec_path = os.path.abspath(spec_path)
            content = None
            with open(spec_path, 'rt') as f:
                content = f.read()
            tests = content.split(TEST_DELIM)
            for i, test in enumerate(tests):
                if not test:
                    continue
                yield ViCmdTest.from_text(test, spec_path, i)

    def append(self, text):
        self.view.run_command('append', {'characters': text})

    def reset(self):
        if getattr(self, "view", None):
            self.view.close()
        self.view = sublime.active_window().new_file()
        self.view.set_scratch(True)

    def set_sels(self, sels):
        """
        Enables adding selections to the buffer text using a minilanguage:

        S = add empty sel before S and delete S
        x = add empty sel before x
        v = add sel from before the first 'v' to after the last contiguous 'v'
        """
        self.view.sel().clear()
        self.view.sel().add_all(sels)
        return

        if test.args['mode'] in ('mode_normal', 'mode_internal_normal'):
            regions = self.view.find_all(r'$', sublime.LITERAL)
            if not regions:
                # TODO(guillermooo): report this? we should expect some regions
                return
            self.view.sel().add_all(regions)
            self.view.run_command('right_delete')
            return

        if test.args ['mode'] == 'mode_visual':
            visual_mode_regs = self.view.find_all(r'v+')
            for vmr in visual_mode_regs:
                self.view.sel().add(vmr)

            if len(self.view.sel()) > 0:
                return

            visual_mode_regs = self.view.find_all(r'S')
            for vmr in visual_mode_regs:
                self.view.sel().add(sublime.Region(vmr.a))
                self.view.run_command('right_delete')
