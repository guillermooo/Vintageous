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


class Test_ex_delete_Deleting_InNormalMode_SingleLine_DefaultStart(BufferTest):
    def testCanDeleteDefaultLineRange(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        self.view.run_command('ex_delete')

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc'
        self.assertEqual(expected, actual)

    def testCanDeleteAtEof_NoNewLine(self):
        set_text(self.view, 'abc\nabc\nabc\nxxx')
        add_sel(self.view, self.R((3, 0), (3, 0)))

        r = CURRENT_LINE_RANGE.copy()
        r['left_ref'] = '4'
        self.view.run_command('ex_delete', {'line_range': r})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc\n'
        self.assertEqual(expected, actual)

    def testCanDeleteAtEof_NewLine(self):
        set_text(self.view, 'abc\nabc\nabc\nxxx\n')
        add_sel(self.view, self.R((3, 0), (3, 0)))

        r = CURRENT_LINE_RANGE.copy()
        r['left_ref'] = '4'
        self.view.run_command('ex_delete', {'line_range': r})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc\n'
        self.assertEqual(expected, actual)

    def testCanDeleteZeroLineRange(self):
        set_text(self.view, 'xxx\nabc\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        r = CURRENT_LINE_RANGE.copy()
        r['text_range'] = '0'
        # If we don't do this, it will default to '.' and the test will fail.
        r['left_ref'] = '0'
        self.view.run_command('ex_delete', {'line_range': r})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc'
        self.assertEqual(expected, actual)

    def testCanDeleteEmptyLine(self):
        set_text(self.view, 'abc\nabc\n\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        r = CURRENT_LINE_RANGE.copy()
        r['right_ref'] = None
        r['left_ref'] = None
        r['text_range'] = '3'
        r['left_offset'] = 3
        self.view.run_command('ex_delete', {'line_range': r})

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc'
        self.assertEqual(expected, actual)


@unittest.skip("Fixme")
class Test_ex_delete_Deleting_InNormalMode_MultipleLines(BufferTest):
    def setUp(self):
        super().setUp()
        self.range = {'left_ref': None,'left_offset': None, 'left_search_offsets': [],
                      'right_ref': None, 'right_offset': None, 'right_search_offsets': [],
                      'separator': ','}

    def testCanDeleteTwoLines(self):
        set_text(self.view, 'abc\nxxx\nxxx\nabc\nabc')
        add_sel(self.view, self.R((0, 0), (0, 0)))

        self.range['left_offset'] = 2
        self.range['right_offset'] = 3
        self.range['text_range'] = '2,3'
        self.view.run_command('ex_delete', {'line_range': self.range})

        expected = 'abc\nabc\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    def testCanDeleteThreeLines(self):
        set_text(self.view, 'abc\nxxx\nxxx\nxxx\nabc\nabc')
        add_sel(self.view, self.R((0, 0), (0, 0)))

        self.range['left_offset'] = 2
        self.range['right_offset'] = 4
        self.range['text_range'] = '2,4'
        self.view.run_command('ex_delete', {'line_range': self.range})

        expected = 'abc\nabc\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)

    # TODO: fix this
    def testCanDeleteMultipleEmptyLines(self):
        set_text(self.view, 'abc\n\n\n\nabc\nabc')
        add_sel(self.view, self.R((0, 0), (0, 0)))

        self.range['left_offset'] = 2
        self.range['right_offset'] = 4
        self.range['text_range'] = '2,4'
        self.view.run_command('ex_delete', {'line_range': self.range})

        expected = 'abc\nabc\nabc'
        actual = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, actual)


class Test_ex_delete_InNormalMode_CaretPosition(BufferTest):
    def setUp(self):
        super().setUp()
        self.range = {'left_ref': None,'left_offset': None, 'left_search_offsets': [],
                      'right_ref': None, 'right_offset': None, 'right_search_offsets': [],
                      'separator': ','}

    def testCanRepositionCaret(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((3, 0), (3, 0)))

        self.range['left_offset'] = 2
        self.range['text_range'] = '2,4'
        self.view.run_command('ex_delete', {'line_range': self.range})

        actual = list(self.view.sel())
        expected = [self.R((1, 0), (1, 0))]
        self.assertEqual(expected, actual)

    # TODO: test with multiple selections.


class Test_ex_delete_ModeTransition(BufferTest):
    def setUp(self):
        super().setUp()
        self.range = {'left_ref': None,'left_offset': None, 'left_search_offsets': [],
                      'right_ref': None, 'right_offset': None, 'right_search_offsets': [],
                      'separator': ','}

    def testFromNormalModeToNormalMode(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 0)))

        state = VintageState(self.view)
        state.enter_normal_mode()

        self.view.run_command('vi_enter_normal_mode')
        prev_mode = state.mode

        self.range['left_offset'] = 2
        self.range['text_range'] = '2'
        self.view.run_command('ex_delete', {'line_range': self.range})

        state = VintageState(self.view)
        new_mode = state.mode
        self.assertEqual(prev_mode, new_mode)

    def testFromVisualModeToNormalMode(self):
        set_text(self.view, 'abc\nxxx\nabc\nabc')
        add_sel(self.view, self.R((1, 0), (1, 1)))

        state = VintageState(self.view)
        state.enter_visual_mode()
        prev_mode = state.mode

        self.range['left_ref'] = "'<"
        self.range['right_ref'] = "'>"
        self.range['text_range'] = "'<,'>"
        self.view.run_command('ex_delete', {'line_range': self.range})

        state = VintageState(self.view)
        new_mode = state.mode
        self.assertNotEqual(prev_mode, new_mode)
        self.assertEqual(new_mode, MODE_NORMAL)
