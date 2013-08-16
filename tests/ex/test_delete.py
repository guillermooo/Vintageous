import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.state import VintageState

from Vintageous.tests.commands import set_text
from Vintageous.tests.commands import add_selection
from Vintageous.tests.commands import get_sel
from Vintageous.tests.commands import first_sel
from Vintageous.tests.commands import make_region_at_row
from Vintageous.tests.commands import BufferTest

from Vintageous.ex_commands import CURRENT_LINE_RANGE


class Test_ex_delete_Deleting_InNormalMode_SingleLine_DefaultStart(BufferTest):
    def testCanDeleteDefaultLineRange(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_selection(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_delete')

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc'
        self.assertEqual(expected, actual)

    def testCanDeleteAtEof_NoNewLine(self):
        set_text(self.view, 'abc\nabc\nabc\nxxx')
        add_selection(self.view, self.R((3, 0), (3, 0)))

        r = CURRENT_LINE_RANGE.copy()
        r['left_ref'] = '4'
        self.view.run_command('ex_delete', {'line_range': r})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc\n'
        self.assertEqual(expected, actual)

    def testCanDeleteAtEof_NewLine(self):
        set_text(self.view, 'abc\nabc\nabc\nxxx\n')
        add_selection(self.view, self.R((3, 0), (3, 0)))

        r = CURRENT_LINE_RANGE.copy()
        r['left_ref'] = '4'
        self.view.run_command('ex_delete', {'line_range': r})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc\n'
        self.assertEqual(expected, actual)

    def testCanDeleteZeroLineRange(self):
        set_text(self.view, 'xxx\nabc\nabc\nabc')
        add_selection(self.view, self.R((1, 0), (1, 0)))

        r = CURRENT_LINE_RANGE.copy()
        r['text_range'] = '0'
        r['left_ref'] = '0'
        self.view.run_command('ex_delete', {'line_range': r})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc'
        self.assertEqual(expected, actual)

#     def testCanDeleteToEmptyLine(self):
#         set_text(self.view, 'abc\nxxx\nabc\n\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         self.view.run_command('ex_delete', {'address': '4'})

#         actual = self.view.substr(self.R(0, self.view.size()))
#         expected = 'abc\nabc\n\nxxx\nabc'
#         self.assertEqual(expected, actual)

#     def testCanDeleteToSameLine(self):
#         set_text(self.view, 'abc\nxxx\nabc\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         self.view.run_command('ex_delete', {'address': '2'})

#         actual = self.view.substr(self.R(0, self.view.size()))
#         expected = 'abc\nxxx\nabc\nabc'
#         self.assertEqual(expected, actual)


# class Test_ex_delete_Deleteing_InNormalMode_MultipleLines(BufferTest):
#     def setUp(self):
#         super().setUp()
#         self.range = {'left_ref': '.','left_offset': 0, 'left_search_offsets': [],
#                       'right_ref': '.', 'right_offset': 1, 'right_search_offsets': []}

#     def testCanDeleteDefaultLineRange(self):
#         set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         self.view.run_command('ex_delete', {'address': '4', 'line_range': self.range})

#         expected = 'abc\nabc\nxxx\nxxx\nabc'
#         actual = self.view.substr(self.R(0, self.view.size()))
#         self.assertEqual(expected, actual)

#     def testCanDeleteToEof(self):
#         set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         self.view.run_command('ex_delete', {'address': '5', 'line_range': self.range})

#         expected = 'abc\nabc\nabc\nxxx\nxxx'
#         actual = self.view.substr(self.R(0, self.view.size()))
#         self.assertEqual(expected, actual)

#     def testCanDeleteToBof(self):
#         set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         self.view.run_command('ex_delete', {'address': '0', 'line_range': self.range})

#         expected = 'xxx\nxxx\nabc\nabc\nabc'
#         actual = self.view.substr(self.R(0, self.view.size()))
#         self.assertEqual(expected, actual)

#     def testCanDeleteToEmptyLine(self):
#         set_text(self.view, 'abc\nxxx\nxxx\nabc\n\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         self.view.run_command('ex_delete', {'address': '5', 'line_range': self.range})

#         expected = 'abc\nabc\n\nxxx\nxxx\nabc'
#         actual = self.view.substr(self.R(0, self.view.size()))
#         self.assertEqual(expected, actual)

#     @unittest.skip("Not implemented")
#     def testCanDeleteToSameLine(self):
#         set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         self.view.run_command('ex_delete', {'address': '2', 'line_range': self.range})

#         expected = 'abc\nxxx\nxxx\nxxx\nxxx\nabc\nabc'
#         actual = self.view.substr(self.R(0, self.view.size()))
#         self.assertEqual(expected, actual)


# class Test_ex_delete_InNormalMode_CaretPosition(BufferTest):
#     def testCanRepositionCaret(self):
#         set_text(self.view, 'abc\nxxx\nabc\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         self.view.run_command('ex_delete', {'address': '3'})

#         actual = list(self.view.sel())
#         expected = [self.R((2, 0), (2, 0))]
#         self.assertEqual(expected, actual)

#     # TODO: test with multiple selections.


# class Test_ex_delete_ModeTransition(BufferTest):
#     def testFromNormalModeToNormalMode(self):
#         set_text(self.view, 'abc\nxxx\nabc\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 0)))

#         state = VintageState(self.view)
#         state.enter_normal_mode()

#         self.view.run_command('vi_enter_normal_mode')
#         prev_mode = state.mode

#         self.view.run_command('ex_delete', {'address': '3'})

#         state = VintageState(self.view)
#         new_mode = state.mode
#         self.assertEqual(prev_mode, new_mode)

#     def testFromVisualModeToNormalMode(self):
#         set_text(self.view, 'abc\nxxx\nabc\nabc')
#         add_selection(self.view, self.R((1, 0), (1, 1)))

#         state = VintageState(self.view)
#         state.enter_visual_mode()
#         prev_mode = state.mode

#         self.view.run_command('ex_delete', {'address': '3'})

#         state = VintageState(self.view)
#         new_mode = state.mode
#         self.assertNotEqual(prev_mode, new_mode)
#         self.assertEqual(new_mode, MODE_NORMAL)
