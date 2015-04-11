from Vintageous.vi.utils import modes

from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


class Test_vi_repeat_star_InNormalMode(ViewTest):
    def testRepeatForward(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(20, 20), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatForwardTwice(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatReverse(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': True})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatReverseTwice(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': True})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': True})
        self.assertEqual(self.R(20, 20), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatForwardReverseTwiceForwardThrice(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        for i in range(0, 2):
            self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': True})
        for i in range(0, 3):
            self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatNoPartial(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabcxend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_star', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15)])

class Test_vi_repeat_octothorp_InNormalMode(ViewTest):
    def testRepeatForward(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_octothorp', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(12, 12), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatReverse(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_octothorp', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': True})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatNoPartial(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabcxend')
        self.clear_sel()
        self.add_sel(self.R(4, 4))

        self.view.run_command('_vi_octothorp', {'mode': modes.NORMAL})
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': True})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15)])

class Test_vi_repeat_slash_InNormalMode(ViewTest):
    def testRepeatForward(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_slash_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.state.last_buffer_search_command = 'vi_slash'
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(12, 12), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatReverse(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_slash_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.state.last_buffer_search_command = 'vi_slash'
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': True})
        self.assertEqual(self.R(20, 20), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatPartial(self):
        self.write('foo\nabc\nbar\nabcxmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_slash_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.state.last_buffer_search_command = 'vi_slash'
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(12, 12), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

class Test_vi_repeat_question_mark_InNormalMode(ViewTest):
    def testRepeatForward(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_question_mark_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.state.last_buffer_search_command = 'vi_question_mark'
        self.assertEqual(self.R(20, 20), first_sel(self.view))
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(12, 12), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatReverse(self):
        self.write('foo\nabc\nbar\nabc\nmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_question_mark_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.state.last_buffer_search_command = 'vi_question_mark'
        self.assertEqual(self.R(20, 20), first_sel(self.view))
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': True})
        self.assertEqual(self.R(4, 4), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])

    def testRepeatPartial(self):
        self.write('foo\nabc\nbar\nabcxmoo\nabc\nend')
        self.clear_sel()
        self.add_sel(self.R(0, 0))

        self.view.run_command('_vi_question_mark_impl', {'mode': modes.NORMAL, 'search_string': 'abc'})
        self.state.last_buffer_search_command = 'vi_question_mark'
        self.assertEqual(self.R(20, 20), first_sel(self.view))
        self.view.run_command('_vi_repeat_buffer_search', {'mode': modes.NORMAL, 'reverse': False})
        self.assertEqual(self.R(12, 12), first_sel(self.view))
        self.assertEqual(self.view.get_regions('vi_search'), [self.R(4, 7), self.R(12, 15), self.R(20, 23)])