
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
        add_selection(self.view, a=1, b=1)

        self.view.run_command('_vi_h_motion', {'mode': MODE_NORMAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(0, 0), first_sel(self.view))

    def testCanMoveInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=1)

        self.view.run_command('_vi_h_motion', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(1, 0), self.view.sel()[0])

    def testCanMoveInNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_selection(self.view, a=11, b=11)

        self.view.run_command('_vi_h_motion', {'mode': MODE_NORMAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(1, 1), self.view.sel()[0])

    def testCanMoveInInternalNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_selection(self.view, a=11, b=11)

        self.view.run_command('_vi_h_motion', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(11, 1), self.view.sel()[0])

    def testCanMoveInVisualMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=2)

        self.view.run_command('_vi_h_motion', {'mode': MODE_VISUAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

    def testCanMoveInVisualModeWithCount(self):
        set_text(self.view, 'foo bar fuzz buzz')
        add_selection(self.view, a=11, b=12)

        self.view.run_command('_vi_h_motion', {'mode': MODE_VISUAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(12, 1), first_sel(self.view))

    def testStopsAtLeftEndInNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=1)

        self.view.run_command('_vi_h_motion', {'mode': MODE_NORMAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(0, 0), first_sel(self.view))

    def testStopsAtLeftEndInVisualMode(self):
        set_text(self.view, 'abc\n')
        add_selection(self.view, a=1, b=2)

        self.view.run_command('_vi_h_motion', {'mode': MODE_VISUAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

    def testStopsAtLeftEndInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=1, b=1)

        self.view.run_command('_vi_h_motion', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(1, 0), first_sel(self.view))
