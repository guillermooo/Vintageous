import unittest
import builtins

import sublime
import sublime_plugin


from Vintageous.tests.borrowed import mock
from Vintageous.tests.borrowed.mock import call
from Vintageous.run import ViExecutionState
from Vintageous.run import ViRunCommand


class Test_ExecutionState(unittest.TestCase):
    def testCanResetWordState(self):
        ViExecutionState.select_word_begin_from_empty_line = True
        ViExecutionState.reset_word_state()
        self.assertFalse(ViExecutionState.select_word_begin_from_empty_line)

    def testCanReset(self):
        ViExecutionState.select_word_begin_from_empty_line = True
        ViExecutionState.reset()
        self.assertFalse(ViExecutionState.select_word_begin_from_empty_line)

    def testHasExpectedInitialValues(self):
        self.assertFalse(ViExecutionState.select_word_begin_from_empty_line)


class Test_ViRunCommand(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoPostAction(self):
        vi_cmd_data = {'post_action': ['foo', {'bar': 1}]}
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.do_post_action(vi_cmd_data)
            rc.assert_called_once_with('foo', {'bar': 1})

    def testDontDoPostActionIfUndefined(self):
        vi_cmd_data = {'post_action': None}
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.do_post_action(vi_cmd_data)
            self.assertEqual(rc.call_count, 0)

    def testAddJumpToList(self):
        vi_cmd_data = {'is_jump': True}

        with mock.patch.object(self.vi_run.view, 'window') as rc:
            x = mock.Mock()
            rc.return_value = x

            self.vi_run.add_to_jump_list(vi_cmd_data)
            self.assertEqual(rc.call_count, 1)
            x.run_command.assert_called_once_with('vi_add_to_jump_list')

    def testDontAddJumpToListIfNotRequested(self):
        vi_cmd_data = {'is_jump': False}

        with mock.patch.object(self.vi_run.view, 'window') as rc:
            x = mock.Mock()
            rc.return_value = x

            self.vi_run.add_to_jump_list(vi_cmd_data)
            self.assertEqual(rc.call_count, 0)
            self.assertEqual(x.run_command.call_count, 0)

    @mock.patch('Vintageous.state.VintageState')
    def testDebug(self, mocked_class):
        x = mock.Mock()
        x.settings.view = {'vintageous_verbose': True}
        mocked_class.return_value = x

        with mock.patch.object(builtins, 'print') as p:
            self.vi_run.debug(['one', 'two'])
            p.assert_called_once_with('Vintageous:', ['one', 'two'])


class Test_get_selected_text(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testExtractsSubstrings(self):
        self.vi_run.view.sel.return_value = [10, 20, 30]
        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': False,
        }
        self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(self.vi_run.view.substr.call_count, 3)

    def testReturnsFragments(self):
        self.vi_run.view.sel.return_value = [10, 20, 30]
        self.vi_run.view.substr.side_effect = lambda x: x
        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': False,
        }
        rv = self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, [10, 20, 30])

    def testCanSynthetizeNewLineAtEof(self):
        self.vi_run.view.substr.return_value = "AAA"
        self.vi_run.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]
        self.vi_run.view.size.return_value = 0

        vi_cmd_data = {
            'synthetize_new_line_at_eof': True,
            'yanks_linewise': False,
        }
        rv = self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA", "AAA\n"])

    def testDoesntSynthetizeNewLineAtEofIfNotNeeded(self):
        self.vi_run.view.substr.return_value = "AAA\n"
        self.vi_run.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]
        self.vi_run.view.size.return_value = 0

        vi_cmd_data = {
            'synthetize_new_line_at_eof': True,
            'yanks_linewise': False,
        }
        rv = self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA\n", "AAA\n"])

    def testDoesntSynthetizeNewLineAtEofIfNotAtEof(self):
        self.vi_run.view.substr.return_value = "AAA"
        self.vi_run.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]
        self.vi_run.view.size.return_value = 100

        vi_cmd_data = {
            'synthetize_new_line_at_eof': True,
            'yanks_linewise': False,
        }
        rv = self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA", "AAA"])

    def testCanYankLinewise(self):
        self.vi_run.view.substr.return_value = "AAA"
        self.vi_run.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]

        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': True,
        }
        rv = self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA\n", "AAA\n"])

    def testDoesNotYankLinewiseIfNonEmptyStringFollowedByNewLine(self):
        self.vi_run.view.substr.return_value = "AAA\n"
        self.vi_run.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]

        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': True,
        }
        rv = self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA\n", "AAA\n"])

    def testYankLinewiseIfEmptyStringFollowedByNewLine(self):
        self.vi_run.view.substr.return_value = "\n"
        self.vi_run.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]

        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': True,
        }
        rv = self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["\n\n", "\n\n"])

    def testYankLinewiseIfTwoTrailingNewLines(self):
        self.vi_run.view.substr.return_value = "\n\n"
        self.vi_run.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]

        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': True,
        }
        rv = self.vi_run.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["\n\n\n", "\n\n\n"])
