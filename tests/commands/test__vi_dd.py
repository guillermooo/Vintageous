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


class Test_vi_dd_action_InNormalMode(BufferTest):
    def testDeletesLastLine(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, self.R((2, 0), (2, 0)))

        # TODO: We should probably test these two commands separately.
        self.view.run_command('_vi_dd_motion', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1})
        self.view.run_command('_vi_dd_action', {'mode': _MODE_INTERNAL_NORMAL})

        expected = self.view.substr(self.R(0, self.view.size()))
        self.assertEqual(expected, 'abc\nabc')
