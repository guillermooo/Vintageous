from Vintageous.vi.utils import modes

from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_star_InNormalMode(ViewTest):
    def testSelectMatch(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(0, 3), self.R(4, 7)])

    def testSelectMatchMiddle(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(self.R(1, 1))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(0, 3), self.R(4, 7)])

    def testSelectMatchEnd(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(self.R(2, 2))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(0, 3), self.R(4, 7)])

    def testSelectMatchEnd(self):
        self.write('abc\nabc')
        self.clear_sel()
        self.add_sel(self.R(2, 2))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(0, 3), self.R(4, 7)])

    def testSelectRepeatMatch(self):
        self.write('abc\nabc\nfoo\nabc\nbar')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.assertEqual(self.R(12, 12), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(0, 3), self.R(4, 7), self.R(12, 15)])

    def testSelectWrapMatch(self):
        self.write('boo\nabc\nfoo\nabc\nbar')
        self.clear_sel()
        self.add_sel(self.R(12, 12))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15)])

    def testSelectNoPartialMatch(self):
        self.write('boo\nabc\nabcxabc\nabc\nbar')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.assertEqual(self.R(16, 16), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(16, 19)])

    def testSelectNoMatch(self):
        self.write('boo\nabc\nfoo\nabc\nbar')
        self.clear_sel()
        self.add_sel(self.R(9, 9))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.assertEqual(self.R(8, 8), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(8, 11)])
