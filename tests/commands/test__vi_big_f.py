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


class Test_vi_big_f_InVisualMode(BufferTest):
    def testCanSearch_OppositeEndSmaller_NoCrossOver(self):
        set_text(self.view, 'foo bar\n')
        add_selection(self.view, self.R((0, 2), (0, 6)))

        self.view.run_command('vi_reverse_find_in_line_inclusive', {'mode': MODE_VISUAL, 'count': 1, 'character': 'b'})
        self.assertEqual(self.R((0, 2), (0, 5)), first_sel(self.view))
