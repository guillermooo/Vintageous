import unittest

from Vintageous.vi.utils import modes

from Vintageous.state import State

from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


# XXX: Am I using the best way to test this?
class Test__vi_ctrl_r(ViewTest):
    def testDoesNotLingerPastSoftEOL(self):
        self.write('abc\nxxx\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 0)))

        self.view.run_command('_vi_dd', {'mode': modes.INTERNAL_NORMAL})
        self.view.window().run_command('_vi_u')
        self.view.window().run_command('_vi_ctrl_r') # passing mode is irrelevant

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nabc\nabc'
        self.assertEqual(expected, actual)
        actual_sel = self.view.sel()[0]
        self.assertEqual(self.R((1, 0), (1, 0)), actual_sel)

    def testDoesNotLingerPastSoftEOL2(self):
        self.write('abc\nxxx foo bar\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((1, 8), (1, 8)))

        self.view.run_command('_vi_big_d', {'mode': modes.INTERNAL_NORMAL})
        self.view.window().run_command('_vi_u')
        self.view.window().run_command('_vi_ctrl_r') # passing mode is irrelevant

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = 'abc\nxxx foo \nabc\nabc'
        self.assertEqual(expected, actual)
        actual_sel = self.view.sel()[0]
        self.assertEqual(self.R((1, 7), (1, 7)), actual_sel)
