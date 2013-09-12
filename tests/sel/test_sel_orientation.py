"""
ViRunCommand reorients the selection prior to running the action. This
tests verify these cases.
TODO: Probably this should be part of the ViRunCommand tests.
"""


import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.state import VintageState
from Vintageous.vi.actions import vi_r
from Vintageous.vi.cmd_data import CmdData

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import BufferTest


class Test_vi_enter_normal_mode__SingleSelection__LeftRoRight(BufferTest):
    def testCaretEndsInExpectedRegion(self):
        set_text(self.view, ''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        add_sel(self.view, self.R((1, 0), (1, 3)))

        VintageState(self.view).mode = MODE_VISUAL

        self.view.run_command('vi_enter_normal_mode', {})
        self.assertEqual(self.R((1, 2), (1, 2)), first_sel(self.view))


class Test_vi_enter_normal_mode__SingleSelection__RightToLeft(BufferTest):

    def testCaretEndsInExpectedRegion(self):
        set_text(self.view, ''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        add_sel(self.view, self.R((1, 3), (1, 0)))

        VintageState(self.view).mode = MODE_VISUAL

        self.view.run_command('vi_enter_normal_mode', {})
        self.assertEqual(self.R((1, 0), (1, 0)), first_sel(self.view))


class Test_vi_r__SingleSelection__LeftToRight(BufferTest):
    def testCaretEndsInExpectedRegion(self):
        set_text(self.view, ''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        add_sel(self.view, self.R((1, 0), (1, 3)))

        state = VintageState(self.view)
        state.enter_visual_mode()

        # TODO: we should bypass vi_r and define the values directly.
        data = CmdData(state)
        data = vi_r(data)
        data['action']['args']['character'] = 'X'

        self.view.run_command('vi_run', data)

        self.assertEqual(self.R((1, 0), (1, 0)), first_sel(self.view))


class Test_vi_r__SingleSelection__RightToLeft(BufferTest):
    def testCaretEndsInExpectedRegion(self):
        set_text(self.view, ''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        add_sel(self.view, self.R((1, 3), (1, 0)))

        state = VintageState(self.view)
        state.enter_visual_mode()

        # TODO: we should bypass vi_r and define the values directly.
        data = CmdData(state)
        data = vi_r(data)
        data['action']['args']['character'] = 'X'

        self.view.run_command('vi_run', data)

        self.assertEqual(self.R((1, 0), (1, 0)), first_sel(self.view))
