import unittest

from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_dd_action_InNormalMode(ViewTest):
    def testDeletesLastLine(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(self.R((2, 0), (2, 0)))

        # TODO: We should probably test these two commands separately.
        self.view.run_command('_vi_dd_motion', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.view.run_command('_vi_dd_action', {'mode': modes.INTERNAL_NORMAL})

        expected = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, 'abc\nabc')
