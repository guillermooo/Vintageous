import unittest

import sublime

from Vintageous.tests.borrowed import mock
from Vintageous.state import VintageState
from Vintageous.test_runner import TestsState
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_INSERT
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE


class VintageStateTests(unittest.TestCase):
    def setUp(self):
        TestsState.view.settings().erase('vintage')
        TestsState.view.window().settings().erase('vintage')
        self.state = VintageState(TestsState.view)

    def test_buffer_was_changed_in_visual_mode_AlwaysReportsChangedForNonVisualModes(self):
        self.state.mode = _MODE_INTERNAL_NORMAL
        self.assertTrue(self.state.buffer_was_changed_in_visual_mode())
        self.state.mode = MODE_NORMAL
        self.assertTrue(self.state.buffer_was_changed_in_visual_mode())

    def test_buffer_was_changed_in_visual_mode_ReportsFalseIfCommandHistoryIsEmpty(self):
        self.state.mode = MODE_VISUAL
        self.assertEqual(self.state.view.command_history(-1), ('', None, 0))
        self.assertFalse(self.state.buffer_was_changed_in_visual_mode())

    def test_buffer_was_changed_in_visual_mode_ReturnsFalseInVisualModeIfCantFindModifyingCommand(self):
        self.state.mode = MODE_VISUAL
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action':{'command': 'vi_enter_visual_mode', 'args': {}}}, 0),
                     # A command without an action is a non-modifying command.
                     # TODO: This asertion isn't reversible, so test that too.
                     ('vi_run', {'action':{}}, 0),
                ]
            cmd_hist.side_effect = reversed(items)

            self.assertFalse(self.state.buffer_was_changed_in_visual_mode())

    def test_buffer_was_changed_in_visual_mode_ReturnsTrueInVisualModeIfCanlFindModifyingCommand(self):
        self.state.mode = MODE_VISUAL
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action':{'command': 'vi_enter_visual_mode', 'args': {}}}, 0),
                     # A command without an action is a non-modifying command.
                     # TODO: This asertion isn't reversible, so test that too.
                     ('vi_run', {'action':{'command': 'foo_bar'}}, 0),
                ]
            cmd_hist.side_effect = reversed(items)

            self.assertTrue(self.state.buffer_was_changed_in_visual_mode())

    def test_buffer_was_changed_in_visual_mode_ReturnsFalseInVisualLineModeIfCantFindModifyingCommand(self):
        self.state.mode = MODE_VISUAL_LINE
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action':{'command': 'vi_enter_visual_line_mode', 'args': {}}}, 0),
                     # A command without an action is a non-modifying command.
                     # TODO: This asertion isn't reversible, so test that too.
                     ('vi_run', {'action':{}}, 0),
                ]
            cmd_hist.side_effect = reversed(items)

            self.assertFalse(self.state.buffer_was_changed_in_visual_mode())

    def test_buffer_was_changed_in_visual_mode_ReturnsTrueInVisualLineModeIfCanFindModifyingCommand(self):
        self.state.mode = MODE_VISUAL_LINE
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action':{'command': 'vi_enter_visual_line_mode', 'args': {}}}, 0),
                     # A command without an action is a non-modifying command.
                     # TODO: This asertion isn't reversible, so test that too.
                     ('vi_run', {'action':{'command': 'foo_bar'}}, 0),
                ]
            cmd_hist.side_effect = reversed(items)

            self.assertTrue(self.state.buffer_was_changed_in_visual_mode())

    @unittest.skip("Not implemented.")
    def test_buffer_was_changed_in_visual_mode_IgnoresNonModifyingCommandsThatAreTrueCommands(self):
        # Leave this here for documentation. We need to exclude commands that do not modify the
        # buffer, although are treated as other commands.

        self.state.mode = MODE_VISUAL_LINE
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action':{'command': 'vi_enter_visual_line_mode', 'args': {}}}, 0),
                     ('vi_run', {'action':{'command': 'vi_yy'}}, 0),
                ]

            cmd_hist.side_effect = reversed(items)
            self.assertFalse(self.state.buffer_was_changed_in_visual_mode())

    def test_buffer_was_changed_in_visual_mode_ReturnsFalseWhenWeExceedLookUpsLimit(self):
        self.state.mode = MODE_VISUAL
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            many_items = [('xxx', {}, 0),] * 249
            # Item 251th won't be consulted, so we should get False back.
            many_items.insert(0, ('vi_run', {'action': {'command': 'foo_bar'}}, 0))
            cmd_hist.side_effect = reversed(many_items)

            self.assertFalse(self.state.buffer_was_changed_in_visual_mode())

    def test_buffer_was_changed_in_visual_mode_ReturnsTrueIfLastCommandInspectedIsModifyingCommand(self):
        self.state.mode = MODE_VISUAL
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            many_items = [('xxx', {}, 0),] * 248
            many_items.insert(0, ('vi_run', {'action': {'command': 'foo_bar'}}, 0))
            cmd_hist.side_effect = reversed(many_items)

            self.assertTrue(self.state.buffer_was_changed_in_visual_mode())

    def test_buffer_was_changed_in_visual_mode_ReturnsFalseIfNoModifyingCommandFoundAndWeHitBottomOfUndoStack(self):
        # XXX: This should actually never happen in visual mode! It would mean that the opening
        # vi_enter_visual_mode command was missing.
        self.state.mode = MODE_VISUAL
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            many_items = [('xxx', {}, 0),] * 50
            many_items.insert(0, ('', None, 0))
            cmd_hist.side_effect = reversed(many_items)

            self.assertFalse(self.state.buffer_was_changed_in_visual_mode())


class VintageStateTests_update_repeat_command(unittest.TestCase):
    def setUp(self):
        TestsState.view.settings().erase('vintage')
        TestsState.view.window().settings().erase('vintage')
        self.state = VintageState(TestsState.view)

    def tearDown(self):
        self.state.repeat_command = ('', None, 0)

    def test_update_repeat_command_IsEmptyAfterInstantiation(self):
        self.assertEqual(self.state.repeat_command, ('', None, 0))

    def test_update_repeat_command_IgnoresEmptyCommands(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('', None, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('foo', {}, 0))

    def test_update_repeat_command_CanUpdateIfNativeModifyingCommandFound(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('bar', {}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('bar', {}, 0))

    def test_update_repeat_command_CommandStaysTheSameIfIdenticalModifyingCommandFound(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('foo', {}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('foo', {}, 0))

    def test_update_repeat_command_IgnoreNonModifyingViRunCommands(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('foo', {}, 0))

    def test_update_repeat_command_CanUpdateIfViRunModifyingCommandFound(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action': 'fizz', 'args': {}}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('vi_run', {'action': 'fizz', 'args': {}}, 0))

    def test_update_repeat_command_CommandStaysTheSameIfIdenticalViRunModifyingCommandFound(self):
        self.state.repeat_command = ('vi_run', {'action': 'fizz', 'args': {}}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action': 'fizz', 'args': {}}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('vi_run', {'action': 'fizz', 'args': {}}, 0))

    def test_update_repeat_command_CanUpdateIfSequenceCommandFound(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('sequence', {}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('sequence', {}, 0))

    def test_update_repeat_command_CommandStaysTheSameIfIdenticalSequenceModifyingCommandFound(self):
        self.state.repeat_command = ('sequence', {'action': 'fizz', 'args': {}}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('sequence', {'action': 'fizz', 'args': {}}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('sequence', {'action': 'fizz', 'args': {}}, 0))


class TestSomeProperties(unittest.TestCase):
    def setUp(self):
        TestsState.view.settings().erase('vintage')
        TestsState.view.window().settings().erase('vintage')
        self.state = VintageState(TestsState.view)

    def testCantSetAction(self):
        self.state.action = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['action'], 'foo')

    def testCantGetAction(self):
        self.state.action = 'foo'
        self.assertEqual(self.state.action, 'foo')

    def testCantSetMotion(self):
        self.state.motion = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['motion'], 'foo')

    def testCantGetMotion(self):
        self.state.motion = 'foo'
        self.assertEqual(self.state.motion, 'foo')

    def testCantSetRegister(self):
        self.state.register = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['register'], 'foo')

    def testCantGetRegister(self):
        self.state.register = 'foo'
        self.assertEqual(self.state.register, 'foo')

    def testCantSetUserInput(self):
        self.state.user_input = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['user_input'], 'foo')

    def testCantGetUserInput(self):
        self.state.user_input = 'foo'
        self.assertEqual(self.state.user_input, 'foo')

    def testCantSetExpectingRegister(self):
        self.state.expecting_register = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['expecting_register'], 'foo')

    def testCantGetExpectingRegister(self):
        self.state.expecting_register = 'foo'
        self.assertEqual(self.state.expecting_register, 'foo')

    def testCantSetExpectingUserInput(self):
        self.state.expecting_user_input = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['expecting_user_input'], 'foo')

    def testCantGetExpectingUserInput(self):
        self.state.expecting_user_input = 'foo'
        self.assertEqual(self.state.expecting_user_input, 'foo')

    def testCantSetExpectingCancelAction(self):
        self.state.cancel_action = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['cancel_action'], 'foo')

    def testCantGetExpectingCancelAction(self):
        self.state.cancel_action = 'foo'
        self.assertEqual(self.state.cancel_action, 'foo')

    def testCantSetMode(self):
        self.state.mode = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['mode'], 'foo')

    def testCantGetMode(self):
        self.state.mode = 'foo'
        self.assertEqual(self.state.mode, 'foo')

    def testCantSetMotionDigits(self):
        self.state.motion_digits = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['motion_digits'], 'foo')

    def testCantGetMotionDigits(self):
        self.state.motion_digits = 'foo'
        self.assertEqual(self.state.motion_digits, 'foo')

    def testCantSetActionDigits(self):
        self.state.action_digits = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['action_digits'], 'foo')

    def testCantGetActionDigits(self):
        self.state.action_digits = 'foo'
        self.assertEqual(self.state.action_digits, 'foo')

    def testCantSetNextMode(self):
        self.state.next_mode = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['next_mode'], 'foo')

    def testCantGetNextMode(self):
        self.state.next_mode = 'foo'
        self.assertEqual(self.state.next_mode, 'foo')

    def testCantSetNextModeCommand(self):
        self.state.next_mode_command = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['next_mode_command'], 'foo')

    def testCantGetNextModeCommand(self):
        self.state.next_mode_command = 'foo'
        self.assertEqual(self.state.next_mode_command, 'foo')


class Test_reset(unittest.TestCase):
    def setUp(self):
        TestsState.view.settings().erase('vintage')
        TestsState.view.window().settings().erase('vintage')
        self.state = VintageState(TestsState.view)

    def testResetsData(self):
        self.state.action = 'action'
        self.state.motion = 'motion'
        self.state.register = 'register'
        self.state.user_input = 'user_input'
        self.state.expecting_register = 'expecting_register'
        self.state.expecting_user_input = 'expecting_user_input'
        self.state.cancel_action = 'cancel_action'
        self.state.mode = 'mode'
        self.state.next_mode = 'next_mode'
        self.state.next_mode_command = 'next_mode_command'

        self.state.reset()

        self.assertEqual(self.state.action, None)
        self.assertEqual(self.state.motion, None)
        self.assertEqual(self.state.register, None)
        self.assertEqual(self.state.user_input, None)
        self.assertEqual(self.state.expecting_register, False)
        self.assertEqual(self.state.expecting_user_input, False)
        self.assertEqual(self.state.cancel_action, False)
        self.assertEqual(self.state.mode, 'mode')
        self.assertEqual(self.state.next_mode, MODE_NORMAL)
        self.assertEqual(self.state.next_mode_command, None)

    def testCallsCorrectModeChangeMethod(self):
        self.state.next_mode = MODE_INSERT
        self.state.next_mode_command = 'foo'

        # XXX Check the code. Do we actually need to call this method at this point?
        with mock.patch.object(self.state, 'enter_insert_mode') as m, \
             mock.patch.object(self.state.view, 'run_command') as rc:
            self.state.reset()
            m.assert_called_once_with()
            rc.assert_called_once_with('foo')

        self.state.reset()

        self.state.next_mode = MODE_NORMAL
        self.state.next_mode_command = 'bar'

        with mock.patch.object(self.state.view, 'run_command') as m:
            self.state.reset()
            m.assert_called_once_with('bar')

    def testDoesNotCallAnyCommandForOtherModes(self):
        self.state.next_mode = MODE_VISUAL_LINE
        self.state.next_mode_command = 'foo'

        with mock.patch.object(self.state.view, 'run_command') as rc:
            self.state.reset()
            self.assertEqual(rc.call_count, 0)

