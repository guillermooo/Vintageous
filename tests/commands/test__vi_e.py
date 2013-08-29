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


# The heavy lifting is done by units.* functions, but we refine some cases in the actual motion
# command, so we need to test for that too here.
class Test_vi_e_InNormalMode(BufferTest):
    def testMoveToEndOfWord_OnLastLine(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, self.R((2, 0), (2, 0)))

        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        self.assertEqual(self.R((2, 2), (2, 2)), first_sel(self.view))

    def testMoveToEndOfWord_OnMiddleLine_WithTrailingWhitespace(self):
        set_text(self.view, 'abc\nabc   \nabc')
        add_sel(self.view, self.R((1, 2), (1, 2)))

        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        self.assertEqual(self.R((2, 2), (2, 2)), first_sel(self.view))

    def testMoveToEndOfWord_OnLastLine_WithTrailingWhitespace(self):
        set_text(self.view, 'abc\nabc\nabc   ')
        add_sel(self.view, self.R((2, 0), (2, 0)))

        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        self.assertEqual(self.R((2, 2), (2, 2)), first_sel(self.view))

        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        self.assertEqual(self.R((2, 5), (2, 5)), first_sel(self.view))
