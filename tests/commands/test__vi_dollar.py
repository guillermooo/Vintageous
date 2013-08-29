import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import BufferTest


class Test_vi_dollar_InNormalMode(BufferTest):
    def testCanMoveInNormalMode(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_dollar', {'mode': MODE_NORMAL, 'count': 1})
        self.assertEqual(self.R(2, 2), first_sel(self.view))

    def testCanMoveInNormalModeWithCount(self):
        set_text(self.view, ''.join(('abc\n',) * 10))
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_dollar', {'mode': MODE_NORMAL, 'count': 5})
        self.assertEqual(self.R(18, 18), first_sel(self.view))

    def testStaysPutOnEmptyLineInNormalMode(self):
        set_text(self.view, 'abc\n\nabc\n')
        add_sel(self.view, a=4, b=4)

        self.view.run_command('_vi_dollar', {'mode': MODE_NORMAL, 'count': 1})
        self.assertEqual(self.R(4, 4), first_sel(self.view))


class Test_vi_dollar_InVisualMode(BufferTest):
    def testCanMoveInVisualMode(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(0, 4), first_sel(self.view))

    def testCanMoveInVisualModeWithCount(self):
        set_text(self.view, ''.join(('abc\n',) * 10))
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL, 'count': 5})
        self.assertEqual(self.R(0, 20), first_sel(self.view))

    def testStaysPutOnEmptyLineInVisualMode(self):
        set_text(self.view, 'abc\n\nabc\n')
        add_sel(self.view, a=4, b=5)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(4, 5), first_sel(self.view))

    def testCanMoveInVisualModeWithReversedSelectionNoCrossOver(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=6, b=1)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(6, 3), first_sel(self.view))

    def testCanMoveInVisualModeWithReversedSelectionAtEol(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=5, b=4)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(4, 8), first_sel(self.view))

    def testCanMoveInVisualModeWithReversedSelectionCrossOver(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=5, b=4)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL, 'count': 2})
        self.assertEqual(self.R(4, 8), first_sel(self.view))

    def testCanMoveInVisualLineMode(self):
        set_text(self.view, 'abc\nabc\nabc\n')
        add_sel(self.view, a=0, b=4)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL_LINE, 'count': 1})
        self.assertEqual(self.R(0, 4), first_sel(self.view))


class Test_vi_dollar_InVisualLineMode(BufferTest):
    @unittest.skip("Maybe later")
    def testCanMoveInVisualLineModeWithCount(self):
        set_text(self.view, 'abc\nabc\nabc\nabc\n')
        add_sel(self.view, a=0, b=4)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL_LINE, 'count': 3})
        self.assertEqual(self.R(0, 12), first_sel(self.view))

    @unittest.skip("Maybe later")
    def testCanMoveInVisualLineModeWithReversedSelection(self):
        set_text(self.view, 'abc\nabc\nabc\nabc\n')
        add_sel(self.view, a=4, b=0)

        self.view.run_command('_vi_dollar', {'mode': MODE_VISUAL_LINE, 'count': 1})
        self.assertEqual(self.R(4, 1), first_sel(self.view))


class Test_vi_dollar_InInternalNormalMode(BufferTest):
    def testCanMoveInInternalNormalMode(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_dollar', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(0, 3), first_sel(self.view))

    def testCanMoveInInternalNormalModeWithCount(self):
        set_text(self.view, 'abc\nabc\nabc\nabc\n')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_dollar', {'mode': _MODE_INTERNAL_NORMAL, 'count': 3})
        self.assertEqual(self.R(0, 12), first_sel(self.view))
