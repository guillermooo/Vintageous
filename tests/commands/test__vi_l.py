import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL

from Vintageous.tests.commands import set_text
from Vintageous.tests.commands import add_selection
from Vintageous.tests.commands import get_sel
from Vintageous.tests.commands import first_sel
from Vintageous.tests.commands import BufferTest


class Test_vi_l(BufferTest):
    def testCanMoveInNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_NORMAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(1, 1), first_sel(self.view))

    def testCanMoveInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(0, 1), first_sel(self.view))

    def testCanMoveInNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_NORMAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(10, 10), first_sel(self.view))

    def testCanMoveInInternalNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(0, 10), first_sel(self.view))

    def testCanMoveInVisualMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=1)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(0, 2), first_sel(self.view))

    def testCanMoveInVisualModeWithCount(self):
        set_text(self.view, 'foo bar fuzz buzz')
        add_selection(self.view, a=0, b=1)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(0, 11), first_sel(self.view))

    def testStopsAtRightEndInNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': MODE_NORMAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(2, 2), first_sel(self.view))

    def testStopsAtRightEndInVisualMode(self):
        set_text(self.view, 'abc\n')
        add_selection(self.view, a=0, b=1)

        self.view.run_command('_vi_l', {'mode': MODE_VISUAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(0, 4), first_sel(self.view))

    def testStopsAtRightEndInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(0, 3), first_sel(self.view))
