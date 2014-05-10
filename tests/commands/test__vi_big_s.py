import unittest

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest

from Vintageous.vi.utils import modes


class Test_vi_big_s_InModeInternalNormal(ViewTest):
    def testDeletesWholeLine(self):
        self.write(''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 7)))

        self.view.run_command('_vi_big_s_action', {'mode': modes.INTERNAL_NORMAL})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo bar\n\nfoo bar\n')

    def testReindents(self):
        content = """\tfoo bar
foo bar
foo bar
"""
        self.write(content)
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 7)))

        self.view.run_command('_vi_big_s_action', {'mode': modes.INTERNAL_NORMAL})
        expected = """\t foo bar
\tfoo bar
"""
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), '\tfoo bar\n\t\nfoo bar\n')

    @unittest.skip("Implement")
    def testCanDeleteWithCount(self):
        self.assertTrue(False)
