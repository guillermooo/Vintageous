from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_big_g_InNormalMode(ViewTest):
    def testCanMoveInNormalMode(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_big_g', {'mode': modes.NORMAL, 'count': 1})
        self.assertEqual(self.R(6, 6), first_sel(self.view))

    def testGoToHardEofIfLastLineIsEmpty(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_big_g', {'mode': modes.NORMAL, 'count': 1})
        self.assertEqual(self.R(8, 8), first_sel(self.view))


class Test_vi_big_g_InVisualMode(ViewTest):
    def testCanMoveInVisualMode(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=1)

        self.view.run_command('_vi_big_g', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(0, 8), first_sel(self.view))


class Test_vi_big_g_InInternalNormalMode(ViewTest):
    def testCanMoveInModeInternalNormal(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(self.R(1, 1))

        self.view.run_command('_vi_big_g', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(0, 8), first_sel(self.view))

    def testOperatesLinewise(self):
        self.write('abc\nabc\nabc\n')
        self.clear_sel()
        self.add_sel(self.R((1, 0), (1, 1)))

        self.view.run_command('_vi_big_g', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R((0, 3), (2, 4)), first_sel(self.view))


class Test_vi_big_g_InVisualLineMode(ViewTest):
    def testCanMoveInModeVisualLine(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(a=0, b=4)

        self.view.run_command('_vi_big_g', {'mode': modes.VISUAL_LINE, 'count': 1})
        self.assertEqual(self.R(0, 8), first_sel(self.view))

