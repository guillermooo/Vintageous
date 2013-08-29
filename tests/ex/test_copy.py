import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.state import VintageState

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import BufferTest

from Vintageous.ex_commands import CURRENT_LINE_RANGE


class Test_ex_copy_Copying_InNormalMode_SingleLine_DefaultStart(BufferTest):
    def testCanCopyDefaultLineRange(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '3'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nxxx\nabc\nxxx\nabc'
        self.assertEqual(expected, actual)

    def testCanCopyToEof(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '4'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nxxx\nabc\nabc\nxxx'
        self.assertEqual(expected, actual)

    def testCanCopyToBof(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '0'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'xxx\nabc\nxxx\nabc\nabc'
        self.assertEqual(expected, actual)

    def testCanCopyToEmptyLine(self):
        set_text(self.view, 'abc\nxxx\nabc\n\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '4'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nxxx\nabc\n\nxxx\nabc'
        self.assertEqual(expected, actual)

    def testCanCopyToSameLine(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '2'})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nxxx\nxxx\nabc\nabc'
        self.assertEqual(expected, actual)


class Test_ex_copy_Copying_InNormalMode_MultipleLines(BufferTest):
    def setUp(self):
        super().setUp()
        self.range = {'left_ref': '.','left_offset': 0, 'left_search_offsets': [],
                      'right_ref': '.', 'right_offset': 1, 'right_search_offsets': []}

    def testCanCopyDefaultLineRange(self):
        set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '4', 'line_range': self.range})

        expected = 'abc\nxxx\nxxx\nabc\nxxx\nxxx\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    def testCanCopyToEof(self):
        set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '5', 'line_range': self.range})

        expected = 'abc\nxxx\nxxx\nabc\nabc\nxxx\nxxx'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    def testCanCopyToBof(self):
        set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '0', 'line_range': self.range})

        expected = 'xxx\nxxx\nabc\nxxx\nxxx\nabc\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    def testCanCopyToEmptyLine(self):
        set_text(self.view, 'abc\nxxx\nxxx\nabc\n\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '5', 'line_range': self.range})

        expected = 'abc\nxxx\nxxx\nabc\n\nxxx\nxxx\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    def testCanCopyToSameLine(self):
        set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '2', 'line_range': self.range})

        expected = 'abc\nxxx\nxxx\nxxx\nxxx\nabc\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)


class Test_ex_copy_InNormalMode_CaretPosition(BufferTest):
    def testCanRepositionCaret(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_copy', {'address': '3'})

        actual = list(self.view.sel())
        expected = [self.R((3, 0), (3, 0))]
        self.assertEqual(expected, actual)


class Test_ex_copy_ModeTransition(BufferTest):
    def testFromNormalModeToNormalMode(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        state = VintageState(self.view)
        state.enter_normal_mode()

        self.view.run_command('vi_enter_normal_mode')
        prev_mode = state.mode

        self.view.run_command('ex_copy', {'address': '3'})

        state = VintageState(self.view)
        new_mode = state.mode
        self.assertEqual(prev_mode, new_mode, MODE_NORMAL)

    def testFromVisualModeToNormalMode(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 1)))

        state = VintageState(self.view)
        state.enter_visual_mode()
        prev_mode = state.mode

        self.view.run_command('ex_copy', {'address': '3'})

        state = VintageState(self.view)
        new_mode = state.mode
        self.assertNotEqual(prev_mode, new_mode)
        self.assertEqual(new_mode, MODE_NORMAL)
