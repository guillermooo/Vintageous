import unittest

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest

from Vintageous.vi.utils import modes


class Test_vi_big_f_InVisualMode(ViewTest):
    def testCanSearch_OppositeEndSmaller_NoCrossOver(self):
        set_text(self.view, 'foo bar\n')
        add_sel(self.view, self.R((0, 2), (0, 6)))

        self.view.run_command('_vi_reverse_find_in_line', {'mode': modes.VISUAL, 'count': 1, 'char': 'b', 'inclusive': True})
        self.assertEqual(self.R((0, 2), (0, 4)), first_sel(self.view))
