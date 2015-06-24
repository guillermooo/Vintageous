"""
Tests for o motion (visual kind).
"""

import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


# unittest.skip("Command doesn't exist as such.")
# class Test_vi_s_InNormalMode(ViewTest):
#     def testChangesModes(self):
#         set_text(self.view, 'abc')
#         add_sel(self.view, self.R((0, 2), (0, 0)))

#         self.view.run_command('_vi_s', {'mode': MODE_NORMAL, 'count': 1})
#         self.assertEqual(self.view.settings().get('vintage')['mode'], MODE_VISUAL_LINE)


# class Test_vi_s_InInternalNormalMode(ViewTest):
#     def testCanMoveInInternalNormalMode(self):
#         set_text(self.view, 'abc')
#         add_sel(self.view, self.R((0, 2), (0, 0)))

#         self.view.run_command('_vi_s', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
#         self.assertEqual(self.R(2, 0), first_sel(self.view))


# class Test_vi_s_InVisualMode(ViewTest):
#     def testCanMove(self):
#         set_text(self.view, 'abc')
#         add_sel(self.view, self.R(0, 2))

#         self.view.run_command('_vi_s', {'mode': MODE_VISUAL, 'count': 1})
#         self.assertEqual(self.R(2, 0), first_sel(self.view))


# class Test_vi_s_InVisualLineMode(ViewTest):
#     def testCanMove(self):
#         set_text(self.view, 'abc\ndef')
#         add_sel(self.view, self.R(0, 4))

#         self.view.run_command('_vi_s', {'mode': MODE_VISUAL_LINE, 'count': 1})
#         self.assertEqual(self.R(4, 0), first_sel(self.view))
