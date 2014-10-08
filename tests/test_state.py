import sublime

import os
import unittest
from unittest import mock
from unittest.mock import call


from Vintageous import state
from Vintageous.vi.utils import modes
from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import make_region
from Vintageous.tests import ViewTest
from Vintageous.vi.cmd_base import cmd_types
from Vintageous.vi import cmd_defs


class StateTestCase(ViewTest):
    def setUp(self):
        super().setUp()


class Test_State(StateTestCase):
    def test_is_in_any_visual_mode(self):
        self.assertEqual(self.state.in_any_visual_mode(), False)

        self.state.mode = modes.NORMAL
        self.assertEqual(self.state.in_any_visual_mode(), False)
        self.state.mode = modes.VISUAL
        self.assertEqual(self.state.in_any_visual_mode(), True)
        self.state.mode = modes.VISUAL_LINE
        self.assertEqual(self.state.in_any_visual_mode(), True)
        self.state.mode = modes.VISUAL_BLOCK
        self.assertEqual(self.state.in_any_visual_mode(), True)

    @unittest.skipIf(os.environ.get('APPVEYOR', False), 'fails in CI server only')
    def testCanInitialize(self):
        s = state.State(self.view)
        # Make sure the actual usage of Vintageous doesn't change the pristine
        # state. This isn't great, though.
        self.view.window().settings().erase('_vintageous_last_char_search_command')
        self.view.window().settings().erase('_vintageous_last_character_search')
        self.view.window().settings().erase('_vintageous_last_buffer_search')

        self.assertEqual(s.sequence, '')
        self.assertEqual(s.partial_sequence, '')
        # TODO(guillermooo): This one fails in AppVeyor, but not locally.
        self.assertEqual(s.mode, modes.NORMAL)
        self.assertEqual(s.action, None)
        self.assertEqual(s.motion, None)
        self.assertEqual(s.action_count, '')
        self.assertEqual(s.glue_until_normal_mode, False)
        self.assertEqual(s.processing_notation, False)
        self.assertEqual(s.last_character_search, '')
        self.assertEqual(s.last_char_search_command, 'vi_f')
        self.assertEqual(s.non_interactive, False)
        self.assertEqual(s.must_capture_register_name, False)
        self.assertEqual(s.last_buffer_search, '')
        self.assertEqual(s.reset_during_init, True)

    def test_must_scroll_into_view(self):
        self.assertFalse(self.state.must_scroll_into_view())

        motion = cmd_defs.ViGotoSymbolInFile()
        self.state.motion = motion
        self.assertTrue(self.state.must_scroll_into_view())


class Test_State_Mode_Switching(StateTestCase):
    # TODO(guillermooo): Disable this only on CI server via env vars?
    @unittest.skipIf(os.environ.get('APPVEYOR', False), 'fails in CI server only')
    def test_enter_normal_mode(self):
        self.assertEqual(self.state.mode, modes.NORMAL)
        self.state.mode = modes.UNKNOWN
        self.assertNotEqual(self.state.mode, modes.NORMAL)
        self.state.enter_normal_mode()
        self.assertEqual(self.state.mode, modes.NORMAL)

    @unittest.skipIf(os.environ.get('APPVEYOR', False), 'fails in CI server only')
    def test_enter_visual_mode(self):
        self.assertEqual(self.state.mode, modes.NORMAL)
        self.state.enter_visual_mode()
        self.assertEqual(self.state.mode, modes.VISUAL)

    @unittest.skipIf(os.environ.get('APPVEYOR', False), 'fails in CI server only')
    def test_enter_insert_mode(self):
        self.assertEqual(self.state.mode, modes.NORMAL)
        self.state.enter_insert_mode()
        self.assertEqual(self.state.mode, modes.INSERT)


class Test_State_Resetting_State(StateTestCase):
    def test_reset_sequence(self):
        self.state.sequence = 'x'
        self.state.reset_sequence()
        self.assertEqual(self.state.sequence, '')

    def test_reset_partial_sequence(self):
        self.state.partial_sequence = 'x'
        self.state.reset_partial_sequence()
        self.assertEqual(self.state.partial_sequence, '')

    def test_reset_command_data(self):
        self.state.sequence = 'abc'
        self.state.partial_sequence = 'x'
        self.state.user_input = 'f'
        self.state.action = cmd_defs.ViReplaceCharacters()
        self.state.motion = cmd_defs.ViGotoSymbolInFile()
        self.state.action_count = '10'
        self.state.motion_count = '100'
        self.state.register = 'a'
        self.state.must_capture_register_name = True

        self.state.reset_command_data()

        self.assertEqual(self.state.action, None)
        self.assertEqual(self.state.motion, None)
        self.assertEqual(self.state.action_count, '')
        self.assertEqual(self.state.motion_count, '')

        self.assertEqual(self.state.sequence, '')
        self.assertEqual(self.state.partial_sequence, '')
        self.assertEqual(self.state.register, '"')
        self.assertEqual(self.state.must_capture_register_name, False)


class Test_State_Resetting_Volatile_Data(StateTestCase):
    def test_reset_volatile_data(self):
        self.state.glue_until_normal_mode = True
        self.state.processing_notation = True
        self.state.non_interactive = True
        self.state.reset_during_init = False

        self.state.reset_volatile_data()

        self.assertFalse(self.state.glue_until_normal_mode)
        self.assertFalse(self.state.processing_notation)
        self.assertFalse(self.state.non_interactive)
        self.assertTrue(self.state.reset_during_init)


class Test_State_counts(StateTestCase):
    def testCanRetrieveGoodActionCount(self):
        self.state.action_count = '10'
        self.assertEqual(self.state.count, 10)

    def testFailsIfBadActionCount(self):
        def set_count():
            self.state.action_count = 'x'
        self.assertRaises(AssertionError, set_count)

    def testFailsIfBadMotionCount(self):
        def set_count():
            self.state.motion_count = 'x'
        self.assertRaises(AssertionError, set_count)

    def testCountIsNeverLessThan1(self):
        self.state.motion_count = '0'
        self.assertEqual(self.state.count, 1)
        def set_count():
            self.state.motion_count = '-1'
        self.assertRaises(AssertionError, set_count)

    def testCanRetrieveGoodMotionCount(self):
        self.state.motion_count = '10'
        self.assertEqual(self.state.count, 10)

    def testCanRetrieveGoodCombinedCount(self):
        self.state.motion_count = '10'
        self.state.action_count = '10'
        self.assertEqual(self.state.count, 100)


class Test_State_Mode_Names(unittest.TestCase):
    def testModeName(self):
        self.assertEqual(modes.COMMAND_LINE, 'mode_command_line')
        self.assertEqual(modes.INSERT, 'mode_insert')
        self.assertEqual(modes.INTERNAL_NORMAL, 'mode_internal_normal')
        self.assertEqual(modes.NORMAL, 'mode_normal')
        self.assertEqual(modes.OPERATOR_PENDING, 'mode_operator_pending')
        self.assertEqual(modes.VISUAL, 'mode_visual')
        self.assertEqual(modes.VISUAL_BLOCK, 'mode_visual_block')
        self.assertEqual(modes.VISUAL_LINE, 'mode_visual_line')


class Test_State_Runnability(StateTestCase):
    def test_can_run_action(self):
        self.assertEqual(self.state.can_run_action(), None)

        self.state.mode = modes.VISUAL
        self.assertEqual(self.state.can_run_action(), None)

        self.state.action = cmd_defs.ViDeleteByChars()
        self.state.mode = modes.VISUAL
        self.assertEqual(self.state.can_run_action(), True)

        self.state.action = cmd_defs.ViDeleteLine()
        self.state.mode = modes.VISUAL
        self.assertEqual(self.state.can_run_action(), True)

        self.state.mode = modes.NORMAL
        self.state.action = cmd_defs.ViDeleteByChars()
        self.assertEqual(self.state.can_run_action(), None)

        self.state.mode = modes.NORMAL
        self.state.action = cmd_defs.ViDeleteLine()
        self.assertEqual(self.state.can_run_action(), True)

    def test_runnable_IfActionAndMotionAvailable(self):
        self.state.mode = modes.NORMAL
        self.state.action = cmd_defs.ViDeleteLine()
        self.state.motion = cmd_defs.ViMoveRightByChars()
        self.assertEqual(self.state.runnable(), True)

        self.state.mode = 'junk'
        self.state.action = cmd_defs.ViDeleteByChars()
        self.state.motion = cmd_defs.ViMoveRightByChars()
        self.assertRaises(ValueError, self.state.runnable)

    def test_runnable_IfMotionAvailable(self):
        self.state.mode = modes.NORMAL
        self.state.motion = cmd_defs.ViMoveRightByChars()
        self.assertEqual(self.state.runnable(), True)

        self.state.mode = modes.OPERATOR_PENDING
        self.state.motion = cmd_defs.ViMoveRightByChars()
        self.assertRaises(ValueError, self.state.runnable)

    def test_runnable_IfActionAvailable(self):
        self.state.mode = modes.NORMAL
        self.state.action = cmd_defs.ViDeleteLine()
        self.assertEqual(self.state.runnable(), True)

        self.state.action = cmd_defs.ViDeleteByChars()
        self.assertEqual(self.state.runnable(), False)

        self.state.mode = modes.OPERATOR_PENDING
        # ensure we can run the action
        self.state.action = cmd_defs.ViDeleteLine()
        self.assertRaises(ValueError, self.state.runnable)


class Test_State_set_command(StateTestCase):
    def testRaiseErrorIfUnknownCommandType(self):
        fake_command = {'type': 'foo'}
        self.assertRaises(AssertionError, self.state.set_command, fake_command)

    def testRaisesErrorIfTooManyMotions(self):
        self.state.motion = cmd_defs.ViMoveRightByChars()

        self.assertRaises(ValueError, self.state.set_command, cmd_defs.ViMoveRightByChars())

    def testChangesModeForLoneMotion(self):
        self.state.mode = modes.OPERATOR_PENDING

        motion = cmd_defs.ViMoveRightByChars()
        self.state.set_command(motion)

        self.assertEqual(self.state.mode, modes.NORMAL)

    def testRaisesErrorIfTooManyActions(self):
        self.state.motion = cmd_defs.ViDeleteLine()

        self.assertRaises(ValueError, self.state.set_command, cmd_defs.ViDeleteLine())

    def testChangesModeForLoneAction(self):
        operator = cmd_defs.ViDeleteByChars()

        self.state.set_command(operator)

        self.assertEqual(self.state.mode, modes.OPERATOR_PENDING)
