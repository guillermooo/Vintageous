from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_l_InNormalMode(ViewTest):
    def testCanMoveInNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_l', {'mode': modes.NORMAL, 'count': 1})
        self.assertEqual(self.R(1, 1), first_sel(self.view))

    def testCanMoveInNormalModeWithCount(self):
        self.write('foo bar baz')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_l', {'mode': modes.NORMAL, 'count': 10})
        self.assertEqual(self.R(10, 10), first_sel(self.view))

    def testStopsAtRightEndInNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_l', {'mode': modes.NORMAL, 'count': 10000})
        self.assertEqual(self.R(2, 2), first_sel(self.view))


class Test_vi_l_InInternalNormalMode(ViewTest):
    def testCanMoveInInternalNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_l', {'mode': modes.INTERNAL_NORMAL, 'count': 1})
        self.assertEqual(self.R(0, 1), first_sel(self.view))

    def testCanMoveInInternalNormalModeWithCount(self):
        self.write('foo bar baz')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_l', {'mode': modes.INTERNAL_NORMAL, 'count': 10})
        self.assertEqual(self.R(0, 10), first_sel(self.view))

    def testStopsAtRightEndInInternalNormalMode(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_l', {'mode': modes.INTERNAL_NORMAL, 'count': 10000})
        self.assertEqual(self.R(0, 3), first_sel(self.view))


class Test_vi_l_InVisualMode(ViewTest):
    def testCanMove(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=0, b=1)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(0, 2), first_sel(self.view))

    def testCanMoveReversedNoCrossOver(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=2, b=0)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(2, 1), first_sel(self.view))

    def testCanMoveReversedMinimal(self):
        self.write('abc')
        self.clear_sel()
        self.add_sel(a=1, b=0)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(0, 2), first_sel(self.view))

    def testCanMoveReversedCrossOver(self):
        self.write('foo bar baz')
        self.clear_sel()
        self.add_sel(a=5, b=0)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 5})
        self.assertEqual(self.R(4, 6), first_sel(self.view))

    def testCanMoveReversedDifferentLines(self):
        self.write('foo\nbar\n')
        self.clear_sel()
        self.add_sel(a=5, b=1)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(5, 2), first_sel(self.view))

    def testStopsAtEolDifferentLinesReversed(self):
        self.write('foo\nbar\n')
        self.clear_sel()
        self.add_sel(a=5, b=3)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 1})
        self.assertEqual(self.R(5, 3), first_sel(self.view))

    def testStopsAtEolDifferentLinesReversedLargeCount(self):
        self.write('foo\nbar\n')
        self.clear_sel()
        self.add_sel(a=5, b=3)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 100})
        self.assertEqual(self.R(5, 3), first_sel(self.view))

    def testCanMoveWithCount(self):
        self.write('foo bar fuzz buzz')
        self.clear_sel()
        self.add_sel(a=0, b=1)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 10})
        self.assertEqual(self.R(0, 11), first_sel(self.view))

    def testStopsAtRightEnd(self):
        self.write('abc\n')
        self.clear_sel()
        self.add_sel(a=0, b=1)

        self.view.run_command('_vi_l', {'mode': modes.VISUAL, 'count': 10000})
        self.assertEqual(self.R(0, 4), first_sel(self.view))
