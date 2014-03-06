import unittest
from unittest import mock
from unittest.mock import call

import sublime

from Vintageous import state
from Vintageous.vi.utils import modes
from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import make_region
from Vintageous.tests import BufferTest
from Vintageous.vi.cmd_defs import cmd_types


class StateTestCase(BufferTest):
    def setUp(self):
        super().setUp()
        self.state = state.State(self.view)


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

    def testCanInitialize(self):
        s = state.State(self.view)
        # Make sure the actual usage of Vintageous doesn't change the pristine
        # state. This isn't great, though.
        self.view.window().settings().erase('_vintageous_last_char_search_command')
        self.view.window().settings().erase('_vintageous_last_character_search')
        self.view.window().settings().erase('_vintageous_last_buffer_search')

        self.assertEqual(s.sequence, '')
        self.assertEqual(s.partial_sequence, '')
        self.assertEqual(s.mode, modes.UNKNOWN)
        self.assertEqual(s.action, None)
        self.assertEqual(s.motion, None)
        self.assertEqual(s.action_count, '')
        self.assertEqual(s.glue_until_normal_mode, False)
        self.assertEqual(s.gluing_sequence, False)
        self.assertEqual(s.user_input, '')
        self.assertEqual(s.input_parsers, [])
        self.assertEqual(s.last_character_search, '')
        self.assertEqual(s.last_char_search_command, False)
        self.assertEqual(s.non_interactive, False)
        self.assertEqual(s.capture_register, False)
        self.assertEqual(s.last_buffer_search, '')
        self.assertEqual(s.reset_during_init, True)

    def test_must_scroll_into_view(self):
        self.assertFalse(self.state.must_scroll_into_view())

        fake_motion = {'scroll_into_view': False}
        self.state.motion = fake_motion
        self.assertFalse(self.state.must_scroll_into_view())

        fake_motion = {'scroll_into_view': True}
        self.state.motion = fake_motion
        self.assertTrue(self.state.must_scroll_into_view())


class Test_State_Mode_Switching(StateTestCase):
    def test_enter_normal_mode(self):
        self.assertEqual(self.state.mode, modes.UNKNOWN)
        self.state.enter_normal_mode()
        self.assertEqual(self.state.mode, modes.NORMAL)

    def test_enter_visual_mode(self):
        self.assertEqual(self.state.mode, modes.UNKNOWN)
        self.state.enter_visual_mode()
        self.assertEqual(self.state.mode, modes.VISUAL)

    def test_enter_insert_mode(self):
        self.assertEqual(self.state.mode, modes.UNKNOWN)
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

    def test_reset_user_input(self):
        self.state.user_input = 'x'
        self.state.reset_user_input()
        self.assertEqual(self.state.user_input, '')

    def test_reset_command_data(self):
        self.state.sequence = 'abc'
        self.state.partial_sequence = 'x'
        self.state.user_input = 'f'
        self.state.action = 'foobar'
        # Just to make state happy.
        self.state.motion = {'scroll_into_view': False}
        self.state.action_count = '10'
        self.state.motion_count = '100'
        self.state.register = 'a'
        self.state.capture_register = True

        self.state.reset_command_data()

        self.assertEqual(self.state.action, None)
        self.assertEqual(self.state.motion, None)
        self.assertEqual(self.state.action_count, '')
        self.assertEqual(self.state.motion_count, '')

        self.assertEqual(self.state.sequence, '')
        self.assertEqual(self.state.partial_sequence, '')
        self.assertEqual(self.state.user_input, '')
        self.assertEqual(self.state.register, '"')
        self.assertEqual(self.state.capture_register, False)


class Test_State_Resetting_Volatile_Data(StateTestCase):
    def test_reset_volatile_data(self):
        self.state.glue_until_normal_mode = True
        self.state.gluing_sequence = True
        self.state.non_interactive = True
        self.state.reset_during_init = False

        self.state.reset_volatile_data()

        self.assertFalse(self.state.glue_until_normal_mode)
        self.assertFalse(self.state.gluing_sequence)
        self.assertFalse(self.state.non_interactive)
        self.assertTrue(self.state.reset_during_init)


class Test_State_counts(StateTestCase):
    def testCanRetrieveGoodActionCount(self):
        self.state.action_count = '10'
        self.assertEqual(self.state.count, 10)

    def testFailsIfBadActionCount(self):
        self.state.action_count = 'x'
        self.assertRaises(ValueError, lambda: self.state.count)

    def testFailsIfBadMotionCount(self):
        self.state.motion_count = 'x'
        self.assertRaises(ValueError, lambda: self.state.count)

    def testCountIsNeverLessThan1(self):
        self.state.motion_count = '0'
        self.assertEqual(self.state.count, 1)
        self.state.motion_count = '-1'
        self.assertRaises(ValueError, lambda: self.state.count)

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

        self.state = state.State(self.view)
        self.state.mode = modes.VISUAL
        self.assertEqual(self.state.can_run_action(), None)

        self.state = state.State(self.view)
        self.state.action = {'name': 'fake_action', 'motion_required': True}
        self.state.mode = modes.VISUAL
        self.assertEqual(self.state.can_run_action(), True)

        self.state = state.State(self.view)
        self.state.action = {'name': 'fake_action', 'motion_required': False}
        self.state.mode = modes.VISUAL
        self.assertEqual(self.state.can_run_action(), True)

        self.state = state.State(self.view)
        self.state.mode = modes.NORMAL
        self.state.action = {'motion_required': True}
        self.assertEqual(self.state.can_run_action(), None)

        self.state = state.State(self.view)
        self.state.mode = modes.NORMAL
        self.state.action = {'motion_required': False}
        self.assertEqual(self.state.can_run_action(), True)

    def test_runnable_AndParsers(self):
        self.state.input_parsers.append('fake')
        self.assertEqual(self.state.runnable(), False)

    def test_runnable_IfActionAndMotionAvailable(self):
        self.state.mode = modes.NORMAL
        self.state.action = {'name': 'fake_action'}
        self.state.motion = {'name': 'fake_motion'}
        self.assertEqual(self.state.runnable(), True)

        self.state = state.State(self.view)
        self.state.mode = 'junk'
        self.state.action = {'name': 'fake_action'}
        self.state.motion = {'name': 'fake_motion'}
        self.assertRaises(ValueError, self.state.runnable)

    def test_runnable_IfMotionAvailable(self):
        self.state.mode = modes.NORMAL
        self.state.motion = {'name': 'fake_motion'}
        self.assertEqual(self.state.runnable(), True)

        self.state = state.State(self.view)
        self.state.mode = modes.OPERATOR_PENDING
        self.state.motion = {'name': 'fake_motion'}
        self.assertRaises(ValueError, self.state.runnable)

    def test_runnable_IfActionAvailable(self):
        self.state.mode = modes.NORMAL
        self.state.action = {'name': 'fake_action', 'motion_required': False}
        self.assertEqual(self.state.runnable(), True)

        self.state = state.State(self.view)
        self.state.action = {'name': 'fake_action', 'motion_required': True}
        self.assertEqual(self.state.runnable(), False)

        self.state = state.State(self.view)
        self.state.mode = modes.OPERATOR_PENDING
        # ensure we can run the action
        self.state.action = {'name': 'fake_action', 'motion_required': False}
        self.assertRaises(ValueError, self.state.runnable)


class Test_State_set_command(StateTestCase):
    def testRaiseErrorIfUnknownCommandType(self):
        fake_command = {'type': 'foo'}
        self.assertRaises(ValueError, self.state.set_command, fake_command)

    def testRaisesErrorIfTooManyMotions(self):
        fake_command_1 = {'type': cmd_types.MOTION, 'name': 'foo'}
        fake_command_2 = {'type': cmd_types.MOTION, 'name': 'bar'}

        self.state.motion = fake_command_1

        self.assertRaises(ValueError, self.state.set_command, fake_command_2)

    def testChangesModeForLoneMotion(self):
        self.state.mode = modes.OPERATOR_PENDING

        fake_command_1 = {'type': cmd_types.MOTION, 'name': 'foo'}
        self.state.set_command(fake_command_1)

        self.assertEqual(self.state.mode, modes.NORMAL)

    def testSetsParser(self):
        fake_command_1 = {'type': cmd_types.MOTION, 'name': 'foo', 'input': 'vi_f'}
        self.state.set_command(fake_command_1)

        self.assertEqual(self.state.input_parsers[-1], 'vi_f')

    def testRaisesErrorIfTooManyActions(self):
        fake_command_1 = {'type': cmd_types.ACTION, 'name': 'foo'}
        fake_command_2 = {'type': cmd_types.ACTION, 'name': 'bar'}

        self.state.motion = fake_command_1

        self.assertRaises(ValueError, self.state.set_command, fake_command_2)

    def testChangesModeForLoneAction(self):
        fake_command_1 = {'type': cmd_types.ACTION, 'name': 'foo', 'motion_required': True}

        self.state.set_command(fake_command_1)

        self.assertEqual(self.state.mode, modes.OPERATOR_PENDING)
