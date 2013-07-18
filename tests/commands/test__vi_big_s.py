import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests.commands import set_text
from Vintageous.tests.commands import add_selection
from Vintageous.tests.commands import get_sel
from Vintageous.tests.commands import first_sel
from Vintageous.tests.commands import BufferTest


class Test_vi_big_s_InModeInternalNormal(BufferTest):
    def testSelectsWholeLine(self):
        set_text(self.view, ''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        add_selection(self.view, self.R((1, 2), (1, 2)))

        self.view.run_command('_vi_big_s_motion', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R((1, 0), (1, 7)), first_sel(self.view))

    def testDeletesWholeLine(self):
        set_text(self.view, ''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        add_selection(self.view, self.R((1, 0), (1, 7)))

        self.view.run_command('_vi_big_s_action', {'mode': _MODE_INTERNAL_NORMAL})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo bar\n\nfoo bar\n')

    def testKeepsLeadingWhitespace(self):
        set_text(self.view, ''.join(('foo bar\n\t  foo bar\nfoo bar\n',)))
        add_selection(self.view, self.R((1, 0), (1, 10)))

        self.view.run_command('_vi_big_s_action', {'mode': _MODE_INTERNAL_NORMAL})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo bar\n\t  \nfoo bar\n')

    @unittest.skip("Implement")
    def testCanDeleteWithCount(self):
        self.assertTrue(False)
