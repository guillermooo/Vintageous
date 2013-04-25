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
    def testDebug(self, mocked_state):
        x = mock.Mock()
        x.settings.view = {'vintageous_verbose': True}
        mocked_state.return_value = x

        with mock.patch.object(builtins, 'print') as p:
            self.vi_run.debug(['one', 'two'])
            p.assert_called_once_with('Vintageous:', ['one', 'two'])


class Test_do_action(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNothingIfNoActionAvailable(self):
        vi_cmd_data = {'action': None}
        with mock.patch.object(self.vi_run, 'debug') as deb:
            self.vi_run.do_action(vi_cmd_data)
            deb.assert_called_once_with('Vintageous: Action command: ', None)

    @mock.patch('Vintageous.run.VintageState.registers')
    def testCallsYank(self, mocked_regs):
        mocked_regs.yank = mock.Mock()
        vi_cmd_data = {
            'action': {'command': 'foo', 'args': {}},
            '_repeat_action': False,
            }
        self.vi_run.do_action(vi_cmd_data)
        mocked_regs.yank.assert_called_once_with(vi_cmd_data)

    @mock.patch('Vintageous.run.VintageState.registers')
    def testRunsCommandOnceIfMustNotRepeatAction(self, mocked_regs):
        mocked_regs.yank = mock.Mock()
        vi_cmd_data = {
            'action': {'command': 'foo', 'args': {}},
            '_repeat_action': False,
            }
        self.vi_run.do_action(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {})

    @mock.patch('Vintageous.run.VintageState.registers')
    def testRunsCommandExpectedTimes(self, mocked_regs):
        mocked_regs.yank = mock.Mock()
        vi_cmd_data = {
            'action': {'command': 'foo', 'args': {}},
            '_repeat_action': True,
            'count': 10,
            }
        self.vi_run.do_action(vi_cmd_data)
        self.assertEqual(self.vi_run.view.run_command.call_count, 10)


class Test_do_post_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNotRunIfUnset(self):
        vi_cmd_data = {'post_motion': []}
        self.vi_run.do_post_motion(vi_cmd_data)
        self.assertEqual(self.vi_run.view.run_command.call_count, 0)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'post_motion': [['foo', {'bar': 100}]]}
        self.vi_run.do_post_motion(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100})


class Test_do_pre_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNotRunIfUnset(self):
        vi_cmd_data = {'pre_motion': []}
        self.vi_run.do_pre_motion(vi_cmd_data)
        self.assertEqual(self.vi_run.view.run_command.call_count, 0)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'post_motion': [['foo', {'bar': 100}]]}
        self.vi_run.do_post_motion(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100})


class Test_do_post_every_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNotRunIfUnset(self):
        vi_cmd_data = {'post_every_motion': None}
        self.vi_run.do_post_every_motion(vi_cmd_data, 0, 0)
        self.assertEqual(self.vi_run.view.run_command.call_count, 0)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'post_every_motion': ['foo', {'bar': 100}]}
        self.vi_run.do_post_every_motion(vi_cmd_data, 100, 200)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100, 'current_iteration': 100, 'total_iterations': 200})

    def testRunsAsExpectedIfMissingArgs(self):
        vi_cmd_data = {'post_every_motion': ['foo']}
        self.vi_run.do_post_every_motion(vi_cmd_data, 100, 200)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'current_iteration': 100, 'total_iterations': 200})


class Test_do_pre_every_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNotRunIfUnset(self):
        vi_cmd_data = {'pre_every_motion': None}
        self.vi_run.do_pre_every_motion(vi_cmd_data, 0, 0)
        self.assertEqual(self.vi_run.view.run_command.call_count, 0)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'pre_every_motion': ['foo', {'bar': 100}]}
        self.vi_run.do_pre_every_motion(vi_cmd_data, 100, 200)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100, 'current_iteration': 100, 'total_iterations': 200})

    def testRunsAsExpectedIfMissingArgs(self):
        vi_cmd_data = {'pre_every_motion': ['foo']}
        self.vi_run.do_pre_every_motion(vi_cmd_data, 100, 200)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'current_iteration': 100, 'total_iterations': 200})


class Test_do_last_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testRunsEvenIfUnset(self):
        # TODO: Does this behavior make sense?
        vi_cmd_data = {'last_motion': []}
        self.vi_run.do_last_motion(vi_cmd_data)
        self.assertEqual(self.vi_run.view.run_command.call_count, 1)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'last_motion': ['foo', {'bar': 100}]}
        self.vi_run.do_last_motion(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100})


class Test_do_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testCallsDebug(self):
        vi_cmd_data = {'motion': {'command': 'foo', 'args': {'bar': 100}}}
        with mock.patch.object(self.vi_run, 'debug') as db:
            self.vi_run.do_motion(vi_cmd_data)
            db.assert_called_once_with('Vintageous: Motion command: ', vi_cmd_data['motion']['command'], vi_cmd_data['motion']['args'])

    def testCallsRunCommand(self):
        vi_cmd_data = {'motion': {'command': 'foo', 'args': {'bar': 100}}}
        self.vi_run.do_motion(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100})
