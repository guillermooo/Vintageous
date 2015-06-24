"""
Tests for o motion (visual kind).
"""

from Vintageous.vi.utils import modes

from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import second_sel
from Vintageous.tests import ViewTest


class Test_vi_big_a_InNormalMode_SingleSel(ViewTest):
    def testMovesCaretToEol(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(self.R(0, 2))

        self.view.run_command('_vi_big_a', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(3, 3), first_sel(self.view))


class Test_vi_big_a_InNormalMode_MultipleSel(ViewTest):
    def testMovesCaretToEol(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.view.sel().add(self.R((0, 1), (0, 1)))
        self.view.sel().add(self.R((1, 1), (1, 1)))

        self.view.run_command('_vi_big_a', {'mode': modes.INTERNAL_NORMAL, 'count': 1})

        self.assertEqual(self.R(3, 3), first_sel(self.view))
        self.assertEqual(self.R((1, 3), (1, 3)), second_sel(self.view))


class Test_vi_big_a_InVisualMode_SingleSel(ViewTest):
    def testMovesCaretToEol(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(self.R((0, 0), (0, 2)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL, 'count': 1})

        self.assertEqual(self.R(2, 2), first_sel(self.view))


class Test_vi_big_a_InVisualMode_MultipleSel(ViewTest):
    def testMovesCaretToEol(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(self.R((0, 0), (0, 2)))
        self.view.sel().add(self.R((1, 1), (1, 2)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL, 'count': 1})

        self.assertEqual(self.R(2, 2), first_sel(self.view))
        self.assertEqual(self.R((1, 2), (1, 2)), second_sel(self.view))


class Test_vi_big_a_InVisualLineMode_SingleSel(ViewTest):
    def testMovesCaretToEol(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(self.R((0, 0), (0, 3)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL_LINE, 'count': 1})

        self.assertEqual(self.R(3, 3), first_sel(self.view))


class Test_vi_big_a_InVisualLineMode_MultipleSel(ViewTest):
    def testMovesCaretToEol(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(self.R((0, 0), (0, 4)))
        self.view.sel().add(self.R((1, 0), (1, 3)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL_LINE, 'count': 1})

        self.assertEqual(self.R(3, 3), first_sel(self.view))
        self.assertEqual(self.R((1, 3), (1, 3)), second_sel(self.view))


class Test_vi_big_a_InVisualBlockMode_SingleSel(ViewTest):
    def testMovesCaretToEol(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(self.R((0, 0), (0, 2)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL_BLOCK, 'count': 1})

        self.assertEqual(self.R(2, 2), first_sel(self.view))


class Test_vi_big_a_InVisualBlockMode_MultipleSel(ViewTest):
    def testMovesCaretToEol(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(self.R((0, 0), (0, 2)))
        self.view.sel().add(self.R((1, 0), (1, 2)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL_BLOCK, 'count': 1})

        self.assertEqual(self.R(2, 2), first_sel(self.view))
        self.assertEqual(self.R((1, 2), (1, 2)), second_sel(self.view))
