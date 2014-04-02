import unittest

from Vintageous.vi.utils import modes

from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_cc_InModeInternalNormal(ViewTest):
    def testSelectsWholeLine(self):
        self.write(''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        self.clear_sel()
        self.add_sel(self.R((1, 2), (1, 2)))

        self.view.run_command('_vi_cc_motion', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R((1, 0), (1, 7)), first_sel(self.view))

    def testDeletesWholeLine(self):
        self.write(''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 7)))

        self.view.run_command('_vi_cc_action', {'mode': modes.INTERNAL_NORMAL})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo bar\n\nfoo bar\n')

    def testKeepsLeadingWhitespace(self):
        self.write(''.join(('\tfoo bar\n\tfoo bar\nfoo bar\n',)))
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 7)))

        self.view.run_command('_vi_cc_action', {'mode': modes.INTERNAL_NORMAL})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), '\tfoo bar\n\t\nfoo bar\n')

    @unittest.skip("Implement")
    def testCanDeleteWithCount(self):
        self.assertTrue(False)

    @unittest.skip("Implement")
    def testDeletedLinesAreYanked(self):
        self.assertTrue(False)

