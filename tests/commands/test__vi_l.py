import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import BufferTest


class Test_vi_l_InNormalMode(BufferTest):
    def testCanMoveInNormalMode(self):
        set_text(self.view, 'abc')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_NORMAL, 'count': 1})
        self.assertEqual(self.R(1, 1), first_sel(self.view))

    def testCanMoveInNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_NORMAL, 'count': 10})
        self.assertEqual(self.R(10, 10), first_sel(self.view))

    def testStopsAtRightEndInNormalMode(self):
        set_text(self.view, 'abc')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_NORMAL, 'count': 10000})
        self.assertEqual(self.R(2, 2), first_sel(self.view))


class Test_vi_l_InInternalNormalMode(BufferTest):
    def testCanMoveInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(0, 1), first_sel(self.view))

    def testCanMoveInInternalNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10})
        self.assertEqual(self.R(0, 10), first_sel(self.view))

    def testStopsAtRightEndInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10000})
        self.assertEqual(self.R(0, 3), first_sel(self.view))


class Test_vi_l_InVisualMode(BufferTest):
    def testCanMove(self):
        set_text(self.view, 'abc')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(0, 2), first_sel(self.view))

    def testCanMoveReversedNoCrossOver(self):
        set_text(self.view, 'abc')
        add_sel(self.view, a=2, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(2, 1), first_sel(self.view))

    def testCanMoveReversedMinimal(self):
        set_text(self.view, 'abc')
        add_sel(self.view, a=1, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(0, 2), first_sel(self.view))

    def testCanMoveReversedCrossOver(self):
        set_text(self.view, 'foo bar baz')
        add_sel(self.view, a=5, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 5})
        self.assertEqual(self.R(4, 6), first_sel(self.view))

    def testCanMoveReversedDifferentLines(self):
        set_text(self.view, 'foo\nbar\n')
        add_sel(self.view, a=5, b=1)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(5, 2), first_sel(self.view))

    def testStopsAtEolDifferentLinesReversed(self):
        set_text(self.view, 'foo\nbar\n')
        add_sel(self.view, a=5, b=3)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(5, 3), first_sel(self.view))

    def testStopsAtEolDifferentLinesReversedLargeCount(self):
        set_text(self.view, 'foo\nbar\n')
        add_sel(self.view, a=5, b=3)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 100})
        self.assertEqual(self.R(5, 3), first_sel(self.view))

    def testCanMoveWithCount(self):
        set_text(self.view, 'foo bar fuzz buzz')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 10})
        self.assertEqual(self.R(0, 11), first_sel(self.view))

    def testStopsAtRightEnd(self):
        set_text(self.view, 'abc\n')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 10000})
        self.assertEqual(self.R(0, 4), first_sel(self.view))
