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


class Test_vi_g_g_InNormalMode(BufferTest):
    def testCanMoveInNormalMode(self):
        set_text(self.view, 'abc\nabc')
        add_sel(self.view, self.R(5, 5))

        self.view.run_command('_vi_g_g', {'mode': MODE_NORMAL})
        self.assertEqual(self.R(0, 0), first_sel(self.view))

    def testGoToHardEofIfLastLineIsEmpty(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, self.R(5, 5))

        self.view.run_command('_vi_g_g', {'mode': MODE_NORMAL})
        self.assertEqual(self.R(0, 0), first_sel(self.view))


class Test_vi_g_g_InVisualMode(BufferTest):
    def testCanMoveInVisualMode(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, self.R((0, 1), (0, 2)))

        self.view.run_command('_vi_g_g', {'mode': MODE_VISUAL})
        self.assertEqual(self.R((0, 2), (0, 0)), first_sel(self.view))

    def testCanMoveInVisualMode_Reversed(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, self.R((0, 2), (0, 1)))

        self.view.run_command('_vi_g_g', {'mode': MODE_VISUAL})
        self.assertEqual(self.R((0, 2), (0, 0)), first_sel(self.view))


class Test_vi_g_g_InInternalNormalMode(BufferTest):
    def testCanMoveInModeInternalNormal(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, self.R(1, 1))

        self.view.run_command('_vi_g_g', {'mode': _MODE_INTERNAL_NORMAL})
        self.assertEqual(self.R(4, 0), first_sel(self.view))


class Test_vi_g_g_InVisualLineMode(BufferTest):
    def testCanMoveInModeVisualLine(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, self.R((0, 0), (0, 4)))

        self.view.run_command('_vi_g_g', {'mode': MODE_VISUAL_LINE})
        self.assertEqual(self.R((0, 0), (0, 4)), first_sel(self.view))

    def testExtendsSelection(self):
        set_text(self.view, 'abc\nabc\n')
        add_sel(self.view, self.R((0, 4), (0, 8)))

        self.view.run_command('_vi_g_g', {'mode': MODE_VISUAL_LINE})
        self.assertEqual(self.R((0, 0), (0, 8)), first_sel(self.view))

