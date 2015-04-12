from Vintageous.vi.utils import modes

from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_slash_InNormalMode(ViewTest):
    def testSearchBegin(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_slash_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.assertEqual(self.R(4, 4), first_sel(self.view))

    def testSearchWrap(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(25, 25))

        self.view.run_command('_vi_slash_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.assertEqual(self.R(4, 4), first_sel(self.view))

    def testSearchWrapMidMatch(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(22, 22))

        self.view.run_command('_vi_slash_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.assertEqual(self.R(4, 4), first_sel(self.view))

    def testSearchWrapEnd(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')

        self.clear_sel()
        self.add_sel(self.R(27, 27))

        self.view.run_command('_vi_slash_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.assertEqual(self.R(4, 4), first_sel(self.view))

class Test_vi_question_mark_InNormalMode(ViewTest):
    def testSearchWrapBegin(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_question_mark_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.assertEqual(self.R(20, 20), first_sel(self.view))

    def testSearchWrap(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(25, 25))

        self.view.run_command('_vi_question_mark_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.assertEqual(self.R(20, 20), first_sel(self.view))

    def testSearchWrapMidMatch(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(12, 12))

        self.view.run_command('_vi_question_mark_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.assertEqual(self.R(4, 4), first_sel(self.view))

    def testSearchEnd(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')

        self.clear_sel()
        self.add_sel(self.R(27, 27))

        self.view.run_command('_vi_question_mark_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.assertEqual(self.R(20, 20), first_sel(self.view))
