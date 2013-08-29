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


class Test_vi_big_g_InNormalMode(BufferTest):
    def testCanMoveInNormalMode(self):
        set_text(self.view, 'abc\nabc')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_big_g', {'mode': MODE_NORMAL, 'count': 1})
        self.assertEqual(self.R(6, 6), first_sel(self.view))

    def testGoToHardEofIfLastLineIsEmpty(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_big_g', {'mode': MODE_NORMAL, 'count': 1})
        self.assertEqual(self.R(8, 8), first_sel(self.view))


class Test_vi_big_g_InVisualMode(BufferTest):
    def testCanMoveInVisualMode(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_big_g', {'mode': MODE_VISUAL, 'count': 1})
        self.assertEqual(self.R(0, 8), first_sel(self.view))


class Test_vi_big_g_InInternalNormalMode(BufferTest):
    def testCanMoveInModeInternalNormal(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_big_g', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(0, 8), first_sel(self.view))


class Test_vi_big_g_InVisualLineMode(BufferTest):
    def testCanMoveInModeVisualLine(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, a=0, b=4)

        self.view.run_command('_vi_big_g', {'mode': MODE_VISUAL_LINE, 'count': 1})
        self.assertEqual(self.R(0, 8), first_sel(self.view))

