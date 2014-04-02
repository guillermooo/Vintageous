"""
Tests for o motion (visual kind).
"""

from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_visual_o_InNormalMode(ViewTest):
    def testDoesntDoAnything(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(self.R((0, 2), (0, 0)))

        self.view.run_command('_vi_visual_o', {'mode': modes.NORMAL, 'count': 1})
        self.assertEqual(self.R(2, 0), first_sel(self.view))


class Test_vi_visual_o_InInternalNormalMode(ViewTest):
    def testCanMoveInInternalNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(self.R((0, 2), (0, 0)))

        self.view.run_command('_vi_visual_o', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(2, 0), first_sel(self.view))


class Test_vi_visual_o_InVisualMode(ViewTest):
    def testCanMove(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(self.R(0, 2))

        self.view.run_command('_vi_visual_o', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(2, 0), first_sel(self.view))


class Test_vi_visual_o_InVisualLineMode(ViewTest):
    def testCanMove(self):
        self.write('abc\ndef')
        self.clear_sel()
        self.add_sel(self.R(0, 4))

        self.view.run_command('_vi_visual_o', {'mode': modes.VISUAL_LINE, 'count': 1})
        self.assertEqual(self.R(4, 0), first_sel(self.view))
