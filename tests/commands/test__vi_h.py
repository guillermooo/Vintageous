
import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL

from Vintageous.tests.commands import set_text
from Vintageous.tests.commands import add_selection
from Vintageous.tests.commands import get_sel
from Vintageous.tests.commands import first_sel
from Vintageous.tests.commands import BufferTest


class Test_vi_h_InNormalMode(BufferTest):
    def testCanMoveInNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=1)

        self.view.run_command('_vi_h', {'mode': MODE_NORMAL, 'count': 1})
        self.assertEqual(self.R(0, 0), first_sel(self.view))

    def testCanMoveInNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_selection(self.view, a=11, b=11)

        self.view.run_command('_vi_h', {'mode': MODE_NORMAL, 'count': 10})
        self.assertEqual(self.R(1, 1), first_sel(self.view))

    def testStopsAtLeftEndInNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=1)

        self.view.run_command('_vi_h', {'mode': MODE_NORMAL, 'count': 10000})
        self.assertEqual(self.R(0, 0), first_sel(self.view))


class Test_vi_h_InInternalNormalMode(BufferTest):
    def testCanMoveInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=1)

        self.view.run_command('_vi_h', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(1, 0), first_sel(self.view))

    def testCanMoveInInternalNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_selection(self.view, a=11, b=11)

        self.view.run_command('_vi_h', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10})
        self.assertEqual(self.R(11, 1), first_sel(self.view))

    def testStopsAtLeftEndInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=1)

        self.view.run_command('_vi_h', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10000})
        self.assertEqual(self.R(1, 0), first_sel(self.view))


class Test_vi_h_InVisualMode(BufferTest):
    def testCanMove(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=2)

        self.view.run_command('_vi_h', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

    def testCanMoveReversed(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=3)

        self.view.run_command('_vi_h', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(1, 2), first_sel(self.view))

    def testCanMoveReversedCrossOver(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=3)

        self.view.run_command('_vi_h', {'mode': MODE_VISUAL, 'count': 2})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

    def testCanMoveReversedCrossOverLargeCount(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=3)

        self.view.run_command('_vi_h', {'mode': MODE_VISUAL, 'count': 100})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

    def testCanMoveWithCount(self):
        set_text(self.view, 'foo bar fuzz buzz')
        add_selection(self.view, a=11, b=12)

        self.view.run_command('_vi_h', {'mode': MODE_VISUAL, 'count': 10})
        self.assertEqual(self.R(12, 1), first_sel(self.view))

    def testStopsAtLeftEnd(self):
        set_text(self.view, 'abc\n')
        add_selection(self.view, a=1, b=2)

        self.view.run_command('_vi_h', {'mode': MODE_VISUAL, 'count': 10000})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

