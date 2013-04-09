import unittest

import sublime

from Vintageous.tests.borrowed import mock
from Vintageous.tests.borrowed.mock import call
from Vintageous.state import VintageState
from Vintageous.test_runner import TestsState
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_INSERT
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_REPLACE
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.constants import MODE_NORMAL_INSERT
from Vintageous.vi.constants import digraphs
from Vintageous.vi.constants import DIGRAPH_MOTION
from Vintageous.vi.constants import DIGRAPH_ACTION
from Vintageous.state import _init_vintageous
from Vintageous.vi.cmd_data import CmdData
from Vintageous.vi import utils
import Vintageous.state


class TestCaseUsingView(unittest.TestCase):
    """Base class to get a clean view for testing.
    """
    def setUp(self):
        TestsState.view.settings().erase('vintage')
        TestsState.view.window().settings().erase('vintage')
        TestsState.view.settings().erase('is_widget')
        self.state = VintageState(TestsState.view)
        self.state.view.set_overwrite_status(False)

    def tearDown(self):
        self.state.view.sel().clear()
        self.state.view.sel().add(sublime.Region(0, 0))


class Test_buffer_was_changed_in_visual_mode(TestCaseUsingView):
    def testAlwaysReportsChangedForNonVisualModes(self):
        self.state.mode = _MODE_INTERNAL_NORMAL
        self.assertTrue(self.state.buffer_was_changed_in_visual_mode())
        self.state.mode = MODE_NORMAL
        self.assertTrue(self.state.buffer_was_changed_in_visual_mode())

    def testReportsFalseIfCommandHistoryIsEmpty(self):
        self.state.mode = MODE_VISUAL
        self.assertEqual(self.state.view.command_history(-1), ('', None, 0))
        self.assertFalse(self.state.buffer_was_changed_in_visual_mode())

    def testReturnsFalseInVisualModeIfCantFindModifyingCommand(self):
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

    def testReturnsTrueInVisualModeIfCanlFindModifyingCommand(self):
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

    def testReturnsFalseInVisualLineModeIfCantFindModifyingCommand(self):
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

    def testReturnsTrueInVisualLineModeIfCanFindModifyingCommand(self):
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
    def test_IgnoresNonModifyingCommandsThatAreTrueCommands(self):
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

    def test_ReturnsFalseWhenWeExceedLookUpsLimit(self):
        self.state.mode = MODE_VISUAL
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            many_items = [('xxx', {}, 0),] * 249
            # Item 251th won't be consulted, so we should get False back.
            many_items.insert(0, ('vi_run', {'action': {'command': 'foo_bar'}}, 0))
            cmd_hist.side_effect = reversed(many_items)

            self.assertFalse(self.state.buffer_was_changed_in_visual_mode())

    def test_ReturnsTrueIfLastCommandInspectedIsModifyingCommand(self):
        self.state.mode = MODE_VISUAL
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            many_items = [('xxx', {}, 0),] * 248
            many_items.insert(0, ('vi_run', {'action': {'command': 'foo_bar'}}, 0))
            cmd_hist.side_effect = reversed(many_items)

            self.assertTrue(self.state.buffer_was_changed_in_visual_mode())

    def test_ReturnsFalseIfNoModifyingCommandFoundAndWeHitBottomOfUndoStack(self):
        # XXX: This should actually never happen in visual mode! It would mean that the opening
        # vi_enter_visual_mode command was missing.
        self.state.mode = MODE_VISUAL
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            many_items = [('xxx', {}, 0),] * 50
            many_items.insert(0, ('', None, 0))
            cmd_hist.side_effect = reversed(many_items)

            self.assertFalse(self.state.buffer_was_changed_in_visual_mode())


class Test_update_repeat_command(TestCaseUsingView):
    def tearDown(self):
        self.state.repeat_command = ('', None, 0)

    def testIsEmptyAfterInstantiation(self):
        self.assertEqual(self.state.repeat_command, ('', None, 0))

    def testIgnoresEmptyCommands(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('', None, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('foo', {}, 0))

    def testCanUpdateIfNativeModifyingCommandFound(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('bar', {}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('bar', {}, 0))

    def testCommandStaysTheSameIfIdenticalModifyingCommandFound(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('foo', {}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('foo', {}, 0))

    def testIgnoreNonModifyingViRunCommands(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('foo', {}, 0))

    def testCanUpdateIfViRunModifyingCommandFound(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action': 'fizz', 'args': {}}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('vi_run', {'action': 'fizz', 'args': {}}, 0))

    def testCommandStaysTheSameIfIdenticalViRunModifyingCommandFound(self):
        self.state.repeat_command = ('vi_run', {'action': 'fizz', 'args': {}}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('vi_run', {'action': 'fizz', 'args': {}}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('vi_run', {'action': 'fizz', 'args': {}}, 0))

    def testCanUpdateIfSequenceCommandFound(self):
        self.state.repeat_command = ('foo', {}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('sequence', {}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('sequence', {}, 0))

    def testCommandStaysTheSameIfIdenticalSequenceModifyingCommandFound(self):
        self.state.repeat_command = ('sequence', {'action': 'fizz', 'args': {}}, 0)
        # patch command_history
        with mock.patch.object(self.state.view, 'command_history') as cmd_hist:
            items = [('sequence', {'action': 'fizz', 'args': {}}, 0)]
            cmd_hist.side_effect = reversed(items)

            self.state.update_repeat_command()
            self.assertEqual(self.state.repeat_command, ('sequence', {'action': 'fizz', 'args': {}}, 0))


class TestVintageStateProperties(TestCaseUsingView):
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

    def testCanGetDefaultNextMode(self):
        self.assertEqual(self.state.next_mode, MODE_NORMAL)

    def testCantSetNextModeCommand(self):
        self.state.next_mode_command = 'foo'
        self.assertEqual(self.state.view.settings().get('vintage')['next_mode_command'], 'foo')

    def testCantGetNextModeCommand(self):
        self.state.next_mode_command = 'foo'
        self.assertEqual(self.state.next_mode_command, 'foo')


class Test_reset(TestCaseUsingView):
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
        with mock.patch.object(self.state.view, 'run_command') as rc:
            self.state.reset()
            rc.assert_called_once_with('foo')

        self.state.reset()

        self.state.next_mode = MODE_NORMAL
        self.state.next_mode_command = 'bar'

        with mock.patch.object(self.state.view, 'run_command') as m:
            self.state.reset()
            m.assert_called_once_with('bar')

    def testDoesNotCallAnyModeChangeCommandForOtherModes(self):
        self.state.next_mode = MODE_VISUAL_LINE
        self.state.next_mode_command = 'foo'

        with mock.patch.object(self.state.view, 'run_command') as rc:
            self.state.reset()
            self.assertEqual(rc.call_count, 0)

    def testDoesNotCallAnyModeChangeCommandIfNotSpecified(self):
        self.state.next_mode = MODE_NORMAL

        with mock.patch.object(self.state.view, 'run_command') as rc:
            self.state.reset()
            self.assertEqual(rc.call_count, 0)

        self.state.next_mode = MODE_VISUAL

        with mock.patch.object(self.state.view, 'run_command') as rc:
            self.state.reset()
            self.assertEqual(rc.call_count, 0)

    def testUpdatesRepeatCommandIfThereWasAnAction(self):
        self.state.action = 'foo'

        with mock.patch.object(self.state, 'update_repeat_command') as m:
            self.state.reset()
            self.assertEqual(m.call_count, 1)

    def testDoesNotUpdateRepeatCommandIfThereWasNoAction(self):
        with mock.patch.object(self.state, 'update_repeat_command') as m:
            self.state.reset()
            self.assertEqual(m.call_count, 0)


class Test__init_vintageous(TestCaseUsingView):
    def testAbortsIfPassedWidget(self):
        self.state.action = 'foo'
        self.state.view.settings().set('is_widget', True)
        _init_vintageous(self.state.view)
        self.assertEqual(self.state.action, 'foo')

    def testAbortsIfPassedViewWithoutSettings(self):
        self.state.action = 'foo'
        _init_vintageous(object())
        self.assertEqual(self.state.action, 'foo')

    def testAbortsIfAskedToNotResetDuringInit(self):
        self.state.action = 'foo'
        with mock.patch.object(Vintageous.state, '_dont_reset_during_init') as x:
            x.return_value = True
            _init_vintageous(self.state.view)
            self.assertEqual(self.state.action, 'foo')

    def testResetIsCalled(self):
        self.state.action = 'foo'
        with mock.patch.object(VintageState, 'reset') as m:
            _init_vintageous(self.state.view)
            self.assertEqual(m.call_count, 1)

    def testResets(self):
        self.state.action = 'foo'
        _init_vintageous(self.state.view)
        self.assertEqual(self.state.action, None)

    def testCallsEnterNormalModeCommandIfStateIsInVisualMode(self):
        self.state.mode = MODE_VISUAL
        with mock.patch.object(self.state.view, 'run_command') as m:
            _init_vintageous(self.state.view)
            m.assert_called_once_with('enter_normal_mode')

    def testCallsEnterNormalModeCommandIfStateIsInVisualLineMode(self):
        self.state.mode = MODE_VISUAL_LINE
        with mock.patch.object(self.state.view, 'run_command') as m:
            _init_vintageous(self.state.view)
            m.assert_called_once_with('enter_normal_mode')

    def testCallsEnterNormalModeFromInsertModeCommandIfStateIsInInsertMode(self):
        self.state.mode = MODE_INSERT
        with mock.patch.object(self.state.view, 'run_command') as m:
            _init_vintageous(self.state.view)
            m.assert_called_once_with('vi_enter_normal_mode_from_insert_mode')

    def testCallsEnterNormalModeFromInsertModeCommandIfStateIsInReplaceMode(self):
        self.state.mode = MODE_REPLACE
        with mock.patch.object(self.state.view, 'run_command') as m:
            _init_vintageous(self.state.view)
            m.assert_called_once_with('vi_enter_normal_mode_from_insert_mode')

    def testCallsRunNormalInsertModeActionsCommandIfStateIsInNormalInsertMode(self):
        self.state.mode = MODE_NORMAL_INSERT
        with mock.patch.object(self.state.view, 'run_command') as m:
            _init_vintageous(self.state.view)
            m.assert_called_once_with('vi_run_normal_insert_mode_actions')

    # TODO: Test that enter_normal_mode() gets called when it should.


class Test_action(TestCaseUsingView):
    def canSet(self):
        self.state.action = 'foo'
        self.assertEqual(self.state.action, 'foo')

    def testTriesToFindDigraph(self):
        self.state.action = 'xxx'

        with mock.patch.dict(digraphs, {('xxx', 'yyy'): ('ooo', None)}):
            self.state.action = 'yyy'
            self.assertEqual(self.state.action, 'ooo')

    def testCanFindDigraphMotion(self):
        self.state.action = 'xxx'
        subst = {('xxx', 'xxx'): ('ooo', DIGRAPH_MOTION)}

        with mock.patch.dict(digraphs, subst):
            self.state.action = 'xxx'
            self.assertEqual(self.state.motion, 'ooo')
            self.assertEqual(self.state.action, None)

    def testCanFindDigraphAction(self):
        self.state.action = 'xxx'
        subst = {('xxx', 'xxx'): ('ooo', DIGRAPH_ACTION)}

        with mock.patch.dict(digraphs, subst):
            self.state.action = 'xxx'
            self.assertEqual(self.state.motion, None)
            self.assertEqual(self.state.action, 'ooo')

    def testCancelActionIfNoMatchFound(self):
        self.state.action = 'xxx'

        with mock.patch.dict(digraphs, {}):
            self.state.action = 'xxx'
            self.assertEqual(self.state.action, 'xxx')
            self.assertEqual(self.state.motion, None)
            self.assertTrue(self.state.cancel_action)


class Test_count(TestCaseUsingView):
    def testCanReturnDefault(self):
        self.assertEqual(self.state.count, 1)

    def testReturnsExpectedCount(self):
        self.state.motion_digits = ['2']
        self.assertEqual(self.state.count, 2)
        self.state.action_digits = ['2']
        self.assertEqual(self.state.count, 2 * 2)
        self.state.motion_digits = []
        self.assertEqual(self.state.count, 2)


class Test_push_action_digit(unittest.TestCase):
    def setUp(self):
        TestsState.view.settings().erase('vintage')
        TestsState.view.window().settings().erase('vintage')
        TestsState.view.settings().erase('is_widget')
        self.state = VintageState(TestsState.view)

    def testCanAddOneItemWhenListIsEmpty(self):
        self.state.push_action_digit("1")
        self.assertEqual(self.state.action_digits, ["1"])

    def testCanAppendMoreDigits(self):
        self.state.push_action_digit("1")
        self.state.push_action_digit("1")
        self.assertEqual(self.state.action_digits, ["1", "1"])


class Test_push_motion_digit(TestCaseUsingView):
    def testCanAddOneItemWhenListIsEmpty(self):
        self.state.push_motion_digit("1")
        self.assertEqual(self.state.motion_digits, ["1"])

    def testCanAppendMoreDigits(self):
        self.state.push_motion_digit("1")
        self.state.push_motion_digit("1")
        self.assertEqual(self.state.motion_digits, ["1", "1"])


class Test_user_provided_count(TestCaseUsingView):
    def testReturnsNoneIfNoneProvided(self):
        self.assertEqual(self.state.user_provided_count, None)

    def testCanReturnActualCount(self):
        self.state.push_motion_digit("10")
        self.state.push_action_digit("10")
        self.assertEqual(self.state.user_provided_count, 100)


class Test_user_input_Setter(TestCaseUsingView):
    def testResetsExpectingUserInputFlag(self):
        self.state.expecting_user_input = True
        self.state.user_input = 'x'
        self.assertEqual(self.state.user_input, 'x')
        self.assertFalse(self.state.expecting_user_input)


class Test_last_buffer_search(TestCaseUsingView):
    def testCanSet(self):
        self.state.last_buffer_search = 'xxx'
        self.assertEqual(self.state.view.window().settings().get('vintage')['last_buffer_search'], 'xxx')


class Test_last_character_search(TestCaseUsingView):
    def testCanSet(self):
        self.state.last_character_search = 'x'
        self.assertEqual(self.state.view.settings().get('vintage')['last_character_search'], 'x')


class Test_xpos(TestCaseUsingView):
    def testCanSet(self):
        self.state.xpos = 100
        self.assertEqual(self.state.view.settings().get('vintage')['xpos'], 100)

    def testCanGet(self):
        self.state.xpos = 100
        self.assertEqual(self.state.xpos, 100)

    def testCanGetDefault(self):
        self.state.xpos = 'foo'
        self.assertEqual(self.state.xpos, None)


class Test_parse_motion(TestCaseUsingView):
    def testCanParseWithUnknownMotion(self):
        self.state.motion = 'foobar'
        self.assertRaises(AttributeError, self.state.parse_motion)

    def testSetsXposIfItsNone(self):
        self.assertEqual(self.state.xpos, None)
        cmd_data = self.state.parse_motion()
        # FIXME: The returned value looks like a mistake. It should rather be
        # a scalar?
        self.assertEqual(cmd_data['xpos'], (0, 0))

    def testSetsXposToTheCurrentXposInTheView(self):
        self.state.view.sel().clear()

        pt = self.state.view.text_point(10, 10)
        self.state.view.sel().add(sublime.Region(pt, pt))

        cmd_data = self.state.parse_motion()
        self.assertEqual(cmd_data['xpos'], (10, 10))

        pt = self.state.view.text_point(10, 10)
        self.state.view.sel().add(sublime.Region(pt, pt + 1))

        cmd_data = self.state.parse_motion()
        self.assertEqual(cmd_data['xpos'], (10, 11))

    def testCmdDataDoesntChangeIfNoMotionProvided(self):
        cmd_data = CmdData(self.state)
        cmd_data['xpos'] = (0, 0)
        new_cmd_data = self.state.parse_motion()
        self.assertEqual(cmd_data, new_cmd_data)

    def testActionInNormalModeSwitchesToInternalNormalMode(self):
        self.state.mode = MODE_NORMAL
        self.state.action = 'foobar'
        cmd_data = self.state.parse_motion()
        self.assertEqual(cmd_data['mode'], _MODE_INTERNAL_NORMAL)

    def testActionAndMotionInNormalModeSwitchesToInternalNormalMode(self):
        self.state.mode = MODE_NORMAL
        # FIXME: We're introducing a dependency in this test.
        self.state.motion = 'vi_l'
        self.state.action = 'bar'
        cmd_data = self.state.parse_motion()
        self.assertEqual(cmd_data['mode'], _MODE_INTERNAL_NORMAL)

    def testKeepSameModeIfInVisualMode(self):
        self.state.mode = MODE_VISUAL
        cmd_data = self.state.parse_motion()
        self.assertEqual(cmd_data['mode'], MODE_VISUAL)

    def testKeepSameModeIfInVisualLineMode(self):
        self.state.mode = MODE_VISUAL_LINE
        cmd_data = self.state.parse_motion()
        self.assertEqual(cmd_data['mode'], MODE_VISUAL_LINE)


class Test_parse_action(TestCaseUsingView):
    def testCantParseWithUnknownMotion(self):
        self.state.action = 'foobar'
        cmd_data = CmdData(self.state)
        self.assertRaises(AttributeError, self.state.parse_action, cmd_data)

    def testCanParseNoneMotion(self):
        cmd_data = CmdData(self.state)
        self.assertRaises(TypeError, self.state.parse_action, cmd_data)

    def testCmdDataIsntModifiedIfThereIsNoAction(self):
        # FIXME: The following creates a dependency in this test.
        self.state.action = 'vi_d'
        new_cmd_data = self.state.parse_action(CmdData(self.state))
        self.assertEqual(new_cmd_data['action']['command'], 'left_delete')

    def testCanRunActionWhenThereAreNonEmptySelections(self):
        self.state.action = 'vi_d'
        self.state.view.sel().clear()
        self.state.view.sel().add(sublime.Region(10, 20))
        new_cmd_data = self.state.parse_action(CmdData(self.state))
        self.assertFalse(new_cmd_data['motion_required'])


class Test_update_xpos(TestCaseUsingView):
    def testCanSetXposInNormalMode(self):
        self.state.mode = MODE_NORMAL
        self.state.view.sel().clear()
        pt = self.state.view.text_point(2, 10)
        self.state.view.sel().add(sublime.Region(pt, pt))
        self.state.update_xpos()
        self.assertEqual(self.state.xpos, 10)

    def testCanSetXposInVisualMode(self):
        self.state.mode = MODE_VISUAL
        self.state.view.sel().clear()
        pt = self.state.view.text_point(2, 10)
        self.state.view.sel().add(sublime.Region(pt - 5, pt))
        self.state.update_xpos()
        self.assertEqual(self.state.xpos, 9)

    def testCanSetXposInVisualModeWithReversedRegion(self):
        self.state.mode = MODE_VISUAL
        self.state.view.sel().clear()
        pt = self.state.view.text_point(2, 10)
        self.state.view.sel().add(sublime.Region(pt, pt - 5))
        self.state.update_xpos()
        self.assertEqual(self.state.xpos, 5)

    def testCanSetXposToDefaultValue(self):
        self.state.mode = MODE_VISUAL_LINE
        self.state.view.sel().clear()
        pt = self.state.view.text_point(2, 10)
        self.state.view.sel().add(sublime.Region(pt, pt - 5))
        self.state.update_xpos()
        self.assertEqual(self.state.xpos, 0)


class Test_eval_cancel_action(TestCaseUsingView):
    def testCallsExpectedFunctions(self):
        with mock.patch.object(self.state, 'parse_motion') as pm, \
            mock.patch.object(self.state, 'parse_action') as pa, \
            mock.patch.object(utils, 'blink') as ub, \
            mock.patch.object(self.state.view, 'run_command') as rc:
                pm.return_value = 'xxx'
                pa.return_value = {'_exit_mode': 'foo',
                                   'must_blink_on_error': False,
                                   '_exit_mode_command': 'bar'}

                self.state.eval_cancel_action()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('xxx')
                self.assertEqual(ub.call_count, 0)
                self.assertEqual(self.state.next_mode, 'foo')
                rc.assert_called_once_with('bar')

    def testDoesntCallsAllFunctions(self):
        with mock.patch.object(self.state, 'parse_motion') as pm, \
            mock.patch.object(self.state, 'parse_action') as pa, \
            mock.patch.object(utils, 'blink') as ub, \
            mock.patch.object(self.state.view, 'run_command') as rc:
                pm.return_value = 'xxx'
                pa.return_value = {'_exit_mode': 'foo',
                                   'must_blink_on_error': True,
                                   '_exit_mode_command': None}

                self.state.eval_cancel_action()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('xxx')
                self.assertEqual(ub.call_count, 1)
                self.assertEqual(self.state.next_mode, 'foo')
                self.assertEqual(rc.call_count, 0)


class Test_eval_full_command(TestCaseUsingView):
    def testFollowsDefaultPathIfIsNotDigraphStart(self):
        data = {
            'is_digraph_start': False,
            '_mark_groups_for_gluing': False
        }

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'reset') as res:

                pm.return_value = 'foo'
                pa.return_value = data

                self.state.eval_full_command()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                self.assertEqual(rc.call_count, 1)
                rc.assert_called_once_with('vi_run', data)
                self.assertEqual(res.call_count, 1)

    def testFollowsExpectedPatIfNotDigraphStartAndMustMarkUndoGroups(self):
        data = {
            'is_digraph_start': False,
            '_mark_groups_for_gluing': True
        }

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'reset') as res:

                pm.return_value = 'foo'
                pa.return_value = data

                self.state.eval_full_command()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                self.assertEqual(rc.call_count, 2)
                self.assertEqual(rc.call_args_list, [mock.call('maybe_mark_undo_groups_for_gluing'), mock.call('vi_run', data)])
                self.assertEqual(res.call_count, 1)

    def testFollowsExpectedDefaultPathForDigraphsModeNormal(self):
        vi_cmd_data = {
            'is_digraph_start': True,
            '_exit_mode': MODE_NORMAL
        }

        self.state.mode = MODE_NORMAL

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'reset') as res:

                pm.return_value = 'foo'
                pa.return_value = vi_cmd_data

                self.state.eval_full_command()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                self.assertEqual(rc.call_count, 0)


    def testFollowsExpectedDefaultPathForDigraphsModeNotNormal(self):
        vi_cmd_data = {
            'is_digraph_start': True,
            '_exit_mode': MODE_NORMAL
        }

        self.state.mode = -100

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'reset') as res, \
             mock.patch.object(self.state, 'enter_normal_mode') as en:

                pm.return_value = 'foo'
                pa.return_value = vi_cmd_data

                self.state.eval_full_command()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                self.assertEqual(rc.call_count, 0)
                self.assertEqual(en.call_count, 1)
                self.assertEqual(res.call_count, 1)

    def testFollowsExpectedDefaultPathForDigraphsExitModeIsInsert(self):
        vi_cmd_data = {
            'is_digraph_start': True,
            '_exit_mode': MODE_INSERT
        }

        self.state.mode = -100

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'reset') as res, \
             mock.patch.object(utils, 'blink') as ub, \
             mock.patch.object(self.state, 'enter_insert_mode') as ei:

                pm.return_value = 'foo'
                pa.return_value = vi_cmd_data

                self.state.eval_full_command()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                self.assertEqual(rc.call_count, 0)
                self.assertEqual(ub.call_count, 1)
                self.assertEqual(res.call_count, 1)
                self.assertEqual(ei.call_count, 1)


class Test_eval_lone_action(TestCaseUsingView):
    def testFollowsDefaultPathIfDigraphStart(self):
        vi_cmd_data = {
            'is_digraph_start': True,
            'motion_required': False,
            '_change_mode_to': MODE_VISUAL,
        }

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state, 'update_status') as ups:

                pm.return_value = 'foo'
                pa.return_value = vi_cmd_data

                self.state.eval_lone_action()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                self.assertEqual(ups.call_count, 0)

    def testFollowsDefaultPathIfDigraphStartAndMustChangeToModeNormal(self):
        vi_cmd_data = {
            'is_digraph_start': True,
            'motion_required': False,
            '_change_mode_to': MODE_NORMAL,
        }

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state, 'enter_normal_mode') as enm, \
             mock.patch.object(self.state, 'update_status') as ups:

                pm.return_value = 'foo'
                pa.return_value = vi_cmd_data

                self.state.eval_lone_action()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                self.assertEqual(enm.call_count, 1)
                self.assertEqual(ups.call_count, 0)

    def testFollowsDefaultPathIfNotDigraphStartAndNotMarkingUndoGroups(self):
        vi_cmd_data = {
            'is_digraph_start': False,
            'motion_required': False,
            '_mark_groups_for_gluing': False,
        }

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'reset') as res, \
             mock.patch.object(self.state, 'update_status') as ups:

                pm.return_value = 'foo'
                pa.return_value = vi_cmd_data

                self.state.eval_lone_action()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                rc.assert_called_once_with('vi_run', vi_cmd_data)
                self.assertEqual(res.call_count, 1)
                self.assertEqual(ups.call_count, 1)

    def testFollowsDefaultPathIfNotDigraphStartAndMarkingUndoGroups(self):
        vi_cmd_data = {
            'is_digraph_start': False,
            'motion_required': False,
            '_mark_groups_for_gluing': True,
        }

        with mock.patch.object(self.state, 'parse_motion') as pm, \
             mock.patch.object(self.state, 'parse_action') as pa, \
             mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'reset') as res, \
             mock.patch.object(self.state, 'update_status') as ups:

                pm.return_value = 'foo'
                pa.return_value = vi_cmd_data

                self.state.eval_lone_action()

                self.assertEqual(pm.call_count, 1)
                pa.assert_called_once_with('foo')
                self.assertEqual(rc.call_args_list, [call('maybe_mark_undo_groups_for_gluing'), call('vi_run', vi_cmd_data)])
                self.assertEqual(res.call_count, 1)
                self.assertEqual(ups.call_count, 1)


class Test_enter_normal_mode(TestCaseUsingView):
    def testSetsXpos(self):
        self.state.view.sel().clear()
        pt = self.state.view.text_point(1, 5)
        self.state.view.sel().add(sublime.Region(pt, pt))

        self.state.enter_normal_mode()
        self.assertEqual(self.state.xpos, 5)

    def testCanSetSettings(self):
        self.state.enter_normal_mode()
        self.assertTrue(self.state.settings.view['command_mode'])
        self.assertTrue(self.state.settings.view['inverse_caret_state'])

    def testClearsOutlinedRegionsFromSearching(self):
        with mock.patch.object(self.state.view, 'erase_regions') as erase_regs:
            self.state.enter_normal_mode()
            erase_regs.assert_called_once_with('vi_search')

    def testSetsModeToNormalMode(self):
        self.state.mode = MODE_VISUAL
        self.state.enter_normal_mode()
        self.assertEqual(self.state.mode, MODE_NORMAL)

    def testTurnsOverwriteModeOff(self):
        with mock.patch.object(self.state.view, 'set_overwrite_status') as overw, \
             mock.patch.object(self.state.view, 'overwrite_status') as oevers:
                oevers.return_value = True
                self.state.enter_normal_mode()
                overw.assert_called_once_with(False)

    def testGluesMarkedGroups(self):
        with mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'buffer_was_changed_in_visual_mode') as bufch:
                bufch.return_value = True
                self.state.enter_normal_mode()
                rc.assert_called_once_with('glue_marked_undo_groups')

    def testUnmarksMarkedGroupsForGluing(self):
        with mock.patch.object(self.state.view, 'run_command') as rc, \
             mock.patch.object(self.state, 'buffer_was_changed_in_visual_mode') as bufch:
                bufch.return_value = False
                self.state.enter_normal_mode()
                rc.assert_called_once_with('unmark_undo_groups_for_gluing')


class Test_enter_visual_line_mode(TestCaseUsingView):
    def testSetsMode(self):
        self.state.enter_visual_line_mode()
        self.assertEqual(self.state.mode, MODE_VISUAL_LINE)


class Test_enter_normal_insert_mode(TestCaseUsingView):
    def testSetsMode(self):
        self.state.enter_normal_insert_mode()
        self.assertEqual(self.state.mode, MODE_NORMAL_INSERT)

    def testSetsSettings(self):
        self.state.enter_normal_insert_mode()
        self.assertFalse(self.state.settings.view['command_mode'])
        self.assertFalse(self.state.settings.view['inverse_caret_state'])


class Test_enter_replace_mode(TestCaseUsingView):
    def testSetsMode(self):
        self.state.enter_replace_mode()
        self.assertEqual(self.state.mode, MODE_REPLACE)

    def testSetsSettings(self):
        self.state.enter_replace_mode()
        self.assertFalse(self.state.settings.view['command_mode'])
        self.assertFalse(self.state.settings.view['inverse_caret_state'])


class Test_store_visual_selections(TestCaseUsingView):
    def testStoresThem(self):
        ra, rb = sublime.Region(10, 20), sublime.Region(30, 40)
        self.state.view.sel().clear()
        self.state.view.sel().add(ra)
        self.state.view.sel().add(rb)

        self.state.store_visual_selections()
        stored_sels = self.state.view.get_regions('vi_visual_selections')

        self.assertEqual(stored_sels[0], ra)
        self.assertEqual(stored_sels[1], rb)
