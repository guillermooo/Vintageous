import unittest

from Vintageous.vi.utils import modes

from Vintageous.state import State

from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest

from Vintageous.ex_commands import CURRENT_LINE_RANGE


class Test_ex_move_Moving_InNormalMode_SingleLine_DefaultStart(ViewTest):
    def testCanMoveDefaultLineRange(self):
        self.write('abc\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move3'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nxxx\nabc'
        self.assertEqual(expected, actual)

    def testCanMoveToEof(self):
        self.write('abc\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move4'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc\nxxx'
        self.assertEqual(expected, actual)

    def testCanMoveToBof(self):
        self.write('abc\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move0'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'xxx\nabc\nabc\nabc'
        self.assertEqual(expected, actual)

    def testCanMoveToEmptyLine(self):
        self.write('abc\nxxx\nabc\n\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move4'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\n\nxxx\nabc'
        self.assertEqual(expected, actual)

    def testCanMoveToSameLine(self):
        self.write('abc\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'address': '2'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nxxx\nabc\nabc'
        self.assertEqual(expected, actual)


class Test_ex_move_Moveing_InNormalMode_MultipleLines(ViewTest):
    def setUp(self):
        super().setUp()
        self.range = {'left_ref': '.','left_offset': 0, 'left_search_offsets': [],
                      'right_ref': '.', 'right_offset': 1, 'right_search_offsets': []}

    def testCanMoveDefaultLineRange(self):
        self.write('abc\nxxx\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move4'})

        expected = 'abc\nxxx\nabc\nxxx\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    def testCanMoveToEof(self):
        self.write('aaa\nxxx\nxxx\naaa\naaa')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move5'})

        expected = 'aaa\nxxx\naaa\naaa\nxxx'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    def testCanMoveToBof(self):
        self.write('abc\nxxx\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move0'})

        expected = 'xxx\nabc\nxxx\nabc\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    def testCanMoveToEmptyLine(self):
        self.write('aaa\nxxx\nxxx\naaa\n\naaa')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move5'})

        expected = 'aaa\nxxx\naaa\n\nxxx\naaa'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    @unittest.skip("Not implemented")
    def testCanMoveToSameLine(self):
        self.write('abc\nxxx\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'address': '2', 'line_range': self.range})

        expected = 'abc\nxxx\nxxx\nxxx\nxxx\nabc\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)


class Test_ex_move_InNormalMode_CaretPosition(ViewTest):
    def testCanRepositionCaret(self):
        self.write('abc\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('ex_move', {'command_line': 'move3'})

        actual = list(self.view.sel())
        expected = [self.R((2, 0), (2, 0))]
        self.assertEqual(expected, actual)

    # TODO: test with multiple selections.


class Test_ex_move_ModeTransition(ViewTest):
    def testFromNormalModeToNormalMode(self):
        self.write('abc\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        state = State(self.view)
        state.enter_normal_mode()

        self.view.run_command('vi_enter_normal_mode')
        prev_mode = state.mode

        self.view.run_command('ex_move', {'address': '3'})

        state = State(self.view)
        new_mode = state.mode
        self.assertEqual(prev_mode, new_mode)

    def testFromVisualModeToNormalMode(self):
        self.write('abc\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 1)))

        state = State(self.view)
        state.enter_visual_mode()
        prev_mode = state.mode

        self.view.run_command('ex_move', {'command_line': 'move3'})

        state = State(self.view)
        new_mode = state.mode
        self.assertNotEqual(prev_mode, new_mode)
