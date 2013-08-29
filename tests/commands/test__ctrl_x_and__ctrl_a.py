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


class Test_vi_ctrl_x_InNormalMode(BufferTest):
    def testAbortsIfNoDigitsInAnyLine(self):
        set_text(self.view, ''.join(('foo bar\nfoo bar\nfoo bar\n',)))
        add_sel(self.view, self.R((0, 0), (0, 0)))
        add_sel(self.view, self.R((1, 0), (1, 0)))
        add_sel(self.view, self.R((2, 0), (2, 0)))

        self.view.run_command('_vi_ctrl_x', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo bar\nfoo bar\nfoo bar\n')

    def testDecreaseDigitsUnderSelection(self):
        set_text(self.view, ''.join(('foo 100\nfoo 200\nfoo 300\n',)))
        add_sel(self.view, self.R((0, 4), (0, 4)))
        add_sel(self.view, self.R((1, 4), (1, 4)))
        add_sel(self.view, self.R((2, 4), (2, 4)))

        self.view.run_command('_vi_ctrl_x', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo 99\nfoo 199\nfoo 299\n')

    def testDecreasePrefixedDigitsUnderSelection(self):
        set_text(self.view, ''.join(('foo 10\nfoo 10\nfoo 10\n',)))
        add_sel(self.view, self.R((0, 4), (0, 4)))
        add_sel(self.view, self.R((1, 4), (1, 4)))
        add_sel(self.view, self.R((2, 4), (2, 4)))

        self.view.run_command('_vi_ctrl_x', {'mode': _MODE_INTERNAL_NORMAL, 'count': 11})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo -1\nfoo -1\nfoo -1\n')

    def testDecreaseSuffixeddDigitsUnderSelection(self):
        set_text(self.view, ''.join(('foo 10px\nfoo 10px\nfoo 10px\n',)))
        add_sel(self.view, self.R((0, 4), (0, 4)))
        add_sel(self.view, self.R((1, 4), (1, 4)))
        add_sel(self.view, self.R((2, 4), (2, 4)))

        self.view.run_command('_vi_ctrl_x', {'mode': _MODE_INTERNAL_NORMAL, 'count': 11})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo -1px\nfoo -1px\nfoo -1px\n')

    def testDecreaseDigitsAfterSelection(self):
        set_text(self.view, ''.join(('foo 100\nfoo 200\nfoo 300\n',)))
        add_sel(self.view, self.R((0, 0), (0, 0)))
        add_sel(self.view, self.R((1, 0), (1, 0)))
        add_sel(self.view, self.R((2, 0), (2, 0)))

        self.view.run_command('_vi_ctrl_x', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo 99\nfoo 199\nfoo 299\n')

    def testDecreaseDigitsAfterSelectionByCount(self):
        set_text(self.view, ''.join(('foo 100\nfoo 200\nfoo 300\n',)))
        add_sel(self.view, self.R((0, 4), (0, 4)))
        add_sel(self.view, self.R((1, 4), (1, 4)))
        add_sel(self.view, self.R((2, 4), (2, 4)))

        self.view.run_command('_vi_ctrl_x', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo 90\nfoo 190\nfoo 290\n')

    def testAbortIfOnlySomeSelectionsHaveDigits(self):
        set_text(self.view, ''.join(('foo 100\nfoo bar\nfoo 300\n',)))
        add_sel(self.view, self.R((0, 4), (0, 4)))
        add_sel(self.view, self.R((1, 4), (1, 4)))
        add_sel(self.view, self.R((2, 4), (2, 4)))

        self.view.run_command('_vi_ctrl_x', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo 100\nfoo bar\nfoo 300\n')

    def testAbortIfOnlySomeSelectionsHaveDigitsAfterThem(self):
        set_text(self.view, ''.join(('foo 100\nfoo bar\nfoo 300\n',)))
        add_sel(self.view, self.R((0, 0), (0, 0)))
        add_sel(self.view, self.R((1, 0), (1, 0)))
        add_sel(self.view, self.R((2, 0), (2, 0)))

        self.view.run_command('_vi_ctrl_x', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.view.substr(self.R(0, self.view.size())), 'foo 100\nfoo bar\nfoo 300\n')
