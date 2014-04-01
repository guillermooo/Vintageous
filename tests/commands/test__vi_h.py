from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_h_InNormalMode(ViewTest):
    def testCanMoveInNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_h', {'mode': modes.NORMAL, 'count': 1})
        self.assertEqual(self.R(0, 0), first_sel(self.view))

    def testCanMoveInNormalModeWithCount(self):
        self.write('foo bar baz')
        self.clear_sel()
        self.add_sel(a=11, b=11)

        self.view.run_command('_vi_h', {'mode': modes.NORMAL, 'count': 10})
        self.assertEqual(self.R(1, 1), first_sel(self.view))

    def testStopsAtLeftEndInNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_h', {'mode': modes.NORMAL, 'count': 10000})
        self.assertEqual(self.R(0, 0), first_sel(self.view))


class Test_vi_h_InInternalNormalMode(ViewTest):
    def testCanMoveInInternalNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_h', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(1, 0), first_sel(self.view))

    def testCanMoveInInternalNormalModeWithCount(self):
        self.write('foo bar baz')
        self.clear_sel()
        self.add_sel(a=11, b=11)

        self.view.run_command('_vi_h', {'mode': modes.INTERNAL_NORMAL, 'count': 10})
        self.assertEqual(self.R(11, 1), first_sel(self.view))

    def testStopsAtLeftEndInInternalNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_h', {'mode': modes.INTERNAL_NORMAL, 'count': 10000})
        self.assertEqual(self.R(1, 0), first_sel(self.view))


class Test_vi_h_InVisualMode(ViewTest):
    def testCanMove(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=2)

        self.view.run_command('_vi_h', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

    def testCanMoveReversed(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=3)

        self.view.run_command('_vi_h', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(1, 2), first_sel(self.view))

    def testCanMoveReversedCrossOver(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=3)

        self.view.run_command('_vi_h', {'mode': modes.VISUAL, 'count': 2})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

    def testCanMoveReversedCrossOverLargeCount(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=3)

        self.view.run_command('_vi_h', {'mode': modes.VISUAL, 'count': 100})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

    def testCanMoveWithCount(self):
        self.write('foo bar fuzz buzz')
        self.clear_sel()
        self.add_sel(a=11, b=12)

        self.view.run_command('_vi_h', {'mode': modes.VISUAL, 'count': 10})
        self.assertEqual(self.R(12, 1), first_sel(self.view))

    def testStopsAtLeftEnd(self):
        self.write('abc\n')
        self.clear_sel()
        self.add_sel(a=1, b=2)

        self.view.run_command('_vi_h', {'mode': modes.VISUAL, 'count': 10000})
        self.assertEqual(self.R(2, 0), first_sel(self.view))

