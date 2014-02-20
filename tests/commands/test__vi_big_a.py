"""
Tests for o motion (visual kind).
"""

import sublime

import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.constants import MODE_VISUAL_BLOCK

from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import second_sel
from Vintageous.tests import BufferTest


class Test_vi_big_a_InNormalMode_SingleSel(BufferTest):
    def testMovesCaretToEol(self):
        set_text(self.view, 'abc')
        add_sel(self.view, self.R(0, 2))

        self.view.run_command('_vi_big_a', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(3, 3), first_sel(self.view))


class Test_vi_big_a_InNormalMode_MultipleSel(BufferTest):
    def testMovesCaretToEol(self):
        set_text(self.view, 'abc\nabc')
        self.view.sel().add(self.R((0, 1), (0, 1)))
        self.view.sel().add(self.R((1, 1), (1, 1)))

        self.view.run_command('_vi_big_a', {'mode': modes.INTERNAL_NORMAL, 'count': 1})

        self.assertEqual(self.R(3, 3), first_sel(self.view))
        self.assertEqual(self.R((1, 3), (1, 3)), second_sel(self.view))


class Test_vi_big_a_InVisualMode_SingleSel(BufferTest):
    def testMovesCaretToEol(self):
        set_text(self.view, 'abc')
        add_sel(self.view, self.R((0, 0), (0, 2)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL, 'count': 1})

        self.assertEqual(self.R(2, 2), first_sel(self.view))


class Test_vi_big_a_InVisualMode_MultipleSel(BufferTest):
    def testMovesCaretToEol(self):
        set_text(self.view, 'abc\nabc')
        add_sel(self.view, self.R((0, 0), (0, 2)))
        self.view.sel().add(self.R((1, 1), (1, 2)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL, 'count': 1})

        self.assertEqual(self.R(2, 2), first_sel(self.view))
        self.assertEqual(self.R((1, 2), (1, 2)), second_sel(self.view))


class Test_vi_big_a_InVisualLineMode_SingleSel(BufferTest):
    def testMovesCaretToEol(self):
        set_text(self.view, 'abc')
        add_sel(self.view, self.R((0, 0), (0, 3)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL_LINE, 'count': 1})

        self.assertEqual(self.R(3, 3), first_sel(self.view))


class Test_vi_big_a_InVisualLineMode_MultipleSel(BufferTest):
    def testMovesCaretToEol(self):
        set_text(self.view, 'abc\nabc')
        add_sel(self.view, self.R((0, 0), (0, 4)))
        self.view.sel().add(self.R((1, 0), (1, 3)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL_LINE, 'count': 1})

        self.assertEqual(self.R(3, 3), first_sel(self.view))
        self.assertEqual(self.R((1, 3), (1, 3)), second_sel(self.view))


class Test_vi_big_a_InVisualBlockMode_SingleSel(BufferTest):
    def testMovesCaretToEol(self):
        set_text(self.view, 'abc')
        add_sel(self.view, self.R((0, 0), (0, 2)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL_BLOCK, 'count': 1})

        self.assertEqual(self.R(2, 2), first_sel(self.view))


class Test_vi_big_a_InVisualBlockMode_MultipleSel(BufferTest):
    def testMovesCaretToEol(self):
        set_text(self.view, 'abc\nabc')
        add_sel(self.view, self.R((0, 0), (0, 2)))
        self.view.sel().add(self.R((1, 0), (1, 2)))

        self.view.run_command('_vi_big_a', {'mode': modes.VISUAL_BLOCK, 'count': 1})

        self.assertEqual(self.R(2, 2), first_sel(self.view))
        self.assertEqual(self.R((1, 2), (1, 2)), second_sel(self.view))
