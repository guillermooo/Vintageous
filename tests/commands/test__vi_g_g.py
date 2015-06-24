from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_g_g_InNormalMode(ViewTest):
    def testCanMoveInNormalMode(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(self.R(5, 5))

        self.view.run_command('_vi_gg', {'mode': modes.NORMAL})
        self.assertEqual(self.R(0, 0), first_sel(self.view))

    def testGoToHardEofIfLastLineIsEmpty(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(self.R(5, 5))

        self.view.run_command('_vi_gg', {'mode': modes.NORMAL})
        self.assertEqual(self.R(0, 0), first_sel(self.view))


class Test_vi_g_g_InVisualMode(ViewTest):
    def testCanMoveInVisualMode(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(self.R((0, 1), (0, 2)))

        self.view.run_command('_vi_gg', {'mode': modes.VISUAL})
        self.assertEqual(self.R((0, 2), (0, 0)), first_sel(self.view))

    def testCanMoveInVisualMode_Reversed(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(self.R((0, 2), (0, 1)))

        self.view.run_command('_vi_gg', {'mode': modes.VISUAL})
        self.assertEqual(self.R((0, 2), (0, 0)), first_sel(self.view))


class Test_vi_g_g_InInternalNormalMode(ViewTest):
    def testCanMoveInModeInternalNormal(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(self.R(1, 1))

        self.view.run_command('_vi_gg', {'mode': modes.INTERNAL_NORMAL})
        self.assertEqual(self.R(4, 0), first_sel(self.view))


class Test_vi_g_g_InVisualLineMode(ViewTest):
    def testCanMoveInModeVisualLine(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(self.R((0, 0), (0, 4)))

        self.view.run_command('_vi_gg', {'mode': modes.VISUAL_LINE})
        self.assertEqual(self.R((0, 0), (0, 4)), first_sel(self.view))

    def testExtendsSelection(self):
        self.write('abc\nabc\n')
        self.clear_sel()
        self.add_sel(self.R((0, 4), (0, 8)))

        self.view.run_command('_vi_gg', {'mode': modes.VISUAL_LINE})
        self.assertEqual(self.R((0, 0), (0, 8)), first_sel(self.view))

