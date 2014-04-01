import unittest

from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_dollar_InNormalMode(ViewTest):
    def testCanMoveInNormalMode(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_dollar', {'mode': modes.NORMAL, 'count': 1})
        self.assertEqual(self.R(2, 2), first_sel(self.view))

    def testCanMoveInNormalModeWithCount(self):
        self.write(''.join(('abc\n',) * 10))
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_dollar', {'mode': modes.NORMAL, 'count': 5})
        self.assertEqual(self.R(18, 18), first_sel(self.view))

    def testStaysPutOnEmptyLineInNormalMode(self):
        self.write('abc\n\nabc\n')
        self.clear_sel()
        self.add_sel(a=4, b=4)

        self.view.run_command('_vi_dollar', {'mode': modes.NORMAL, 'count': 1})
        self.assertEqual(self.R(4, 4), first_sel(self.view))


class Test_vi_dollar_InVisualMode(ViewTest):
    def testCanMoveInVisualMode(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=1)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(0, 4), first_sel(self.view))

    def testCanMoveInVisualModeWithCount(self):
        self.write(''.join(('abc\n',) * 10))
        self.clear_sel()
        self.add_sel(a=0, b=1)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL, 'count': 5})
        self.assertEqual(self.R(0, 20), first_sel(self.view))

    def testStaysPutOnEmptyLineInVisualMode(self):
        self.write('abc\n\nabc\n')
        self.clear_sel()
        self.add_sel(a=4, b=5)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(4, 5), first_sel(self.view))

    def testCanMoveInVisualModeWithReversedSelectionNoCrossOver(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=6, b=1)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(6, 3), first_sel(self.view))

    def testCanMoveInVisualModeWithReversedSelectionAtEol(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=5, b=4)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(4, 8), first_sel(self.view))

    def testCanMoveInVisualModeWithReversedSelectionCrossOver(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=5, b=4)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL, 'count': 2})
        self.assertEqual(self.R(4, 8), first_sel(self.view))

    def testCanMoveInVisualLineMode(self):
        self.write('abc\nabc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=4)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL_LINE, 'count': 1})
        self.assertEqual(self.R(0, 4), first_sel(self.view))


class Test_vi_dollar_InVisualLineMode(ViewTest):
    @unittest.skip("Maybe later")
    def testCanMoveInVisualLineModeWithCount(self):
        self.write('abc\nabc\nabc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=4)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL_LINE, 'count': 3})
        self.assertEqual(self.R(0, 12), first_sel(self.view))

    @unittest.skip("Maybe later")
    def testCanMoveInVisualLineModeWithReversedSelection(self):
        self.write('abc\nabc\nabc\nabc\n')
        self.clear_sel()
        self.add_sel(a=4, b=0)

        self.view.run_command('_vi_dollar', {'mode': modes.VISUAL_LINE, 'count': 1})
        self.assertEqual(self.R(4, 1), first_sel(self.view))


class Test_vi_dollar_InInternalNormalMode(ViewTest):
    def testCanMoveInInternalNormalMode(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_dollar', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(0, 3), first_sel(self.view))

    def testCanMoveInInternalNormalModeWithCount(self):
        self.write('abc\nabc\nabc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_dollar', {'mode': modes.INTERNAL_NORMAL, 'count': 3})
        self.assertEqual(self.R(0, 12), first_sel(self.view))
