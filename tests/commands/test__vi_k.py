from Vintageous.vi.utils import modes

from collections import namedtuple

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


# TODO: Test against folded regions.
# TODO: Ensure that we only create empty selections while testing. Add assert_all_sels_empty()?
# TODO: Test different values for xpos in combination with the starting col.
test_data = namedtuple('test_data', 'cmd initial_text regions cmd_params expected actual_func msg')
region_data = namedtuple('region_data', 'regions')


def get_text(test):
    return test.view.substr(test.R(0, test.view.size()))

def  first_sel_wrapper(test):
    return first_sel(test.view)


TESTS_MODES = (
    # NORMAL mode
    test_data(cmd='_vi_k', initial_text='abc\nabc', regions=[[(1, 1), (1, 1)]], cmd_params={'mode': modes.NORMAL, 'xpos': 1},
              expected=region_data([(0, 1), (0, 1)]), actual_func=first_sel_wrapper, msg='should move up one line (normal mode)'),
    test_data(cmd='_vi_k', initial_text='abc\nabc\nabc', regions=[[(2, 1), (2, 1)]], cmd_params={'mode': modes.NORMAL, 'xpos': 1, 'count': 2},
              expected=region_data([(0, 1), (0, 1)]), actual_func=first_sel_wrapper, msg='should move up two lines (normal mode)'),
    test_data(cmd='_vi_k', initial_text='foo bar\nfoo', regions=[[(1, 1), (1, 1)]], cmd_params={'mode': modes.NORMAL, 'xpos': 1},
              expected=region_data([(0, 1), (0, 1)]), actual_func=first_sel_wrapper, msg='should move up one line onto longer line (normal mode)'),

    test_data(cmd='_vi_k', initial_text='foo\nfoo bar', regions=[[(1, 5), (1, 5)]], cmd_params={'mode': modes.NORMAL, 'xpos': 5},
              expected=region_data([(0, 2), (0, 2)]), actual_func=first_sel_wrapper, msg='should move onto shorter line (mode normal)'),
    test_data(cmd='_vi_k', initial_text='foo\n\n', regions=[[(1, 0), (1, 0)]], cmd_params={'mode': modes.NORMAL, 'xpos': 1},
              expected=region_data([(0, 1), (0, 1)]), actual_func=first_sel_wrapper, msg='should be able to move from empty line (mode normal)'),
    test_data(cmd='_vi_k', initial_text='\n\n\n', regions=[[(1, 0), (1, 0)]], cmd_params={'mode': modes.NORMAL, 'xpos': 0},
              expected=region_data([(0, 0), (0, 0)]), actual_func=first_sel_wrapper, msg='should move from empty line to empty line (mode normal)'),
    test_data(cmd='_vi_k', initial_text='foo\nbar\nbaz\n', regions=[[(2, 1), (2, 1)]], cmd_params={'mode': modes.NORMAL, 'xpos': 1, 'count': 100},
              expected=region_data([(0, 1), (0, 1)]), actual_func=first_sel_wrapper, msg='should not move too far (mode normal)'),

    test_data(cmd='_vi_k', initial_text='foo\nbar\nbaz\n', regions=[[(1, 1), (1, 2)]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 2},
              expected=region_data([(1, 2), (0, 2)]), actual_func=first_sel_wrapper, msg='move one line (visual mode)'),
    test_data(cmd='_vi_k', initial_text='foo\nbar\nbaz\n', regions=[[(2, 1), (2, 2)]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 2},
              expected=region_data([(2, 2), (1, 2)]), actual_func=first_sel_wrapper, msg='move opposite end greater with sel of size 1 (visual mode)'),
    test_data(cmd='_vi_k', initial_text='foo\nfoo\nbaz', regions=[[(1, 1), (1, 3)]], cmd_params={'mode': modes.VISUAL, 'xpos': 3},
              expected=region_data([(1, 2), (0, 3)]), actual_func=first_sel_wrapper, msg='move opposite end smaller with sel of size 2'),
    test_data(cmd='_vi_k', initial_text='foobar\nbarfoo\nbuzzfizz\n', regions=[[(1, 1), (1, 4)]], cmd_params={'mode': modes.VISUAL, 'xpos': 3},
              expected=region_data([(1, 2), (0, 3)]), actual_func=first_sel_wrapper, msg='move opposite end smaller with sel of size 3'),
    test_data(cmd='_vi_k', initial_text='foo\nbar\nbaz\n', regions=[[(0, 1), (2, 1)]], cmd_params={'mode': modes.VISUAL, 'xpos': 1},
              expected=region_data([(0, 1), (1, 2)]), actual_func=first_sel_wrapper, msg='move opposite end smaller different lines no cross over'),

    test_data(cmd='_vi_k', initial_text='foo\nbar\nbaz\n', regions=[[(1, 0), (2, 1)]], cmd_params={'mode': modes.VISUAL, 'xpos': 0},
              expected=region_data([(1, 0), (1, 1)]), actual_func=first_sel_wrapper, msg='move opposite end smaller different lines cross over xpos at 0'),
    test_data(cmd='_vi_k', initial_text='foo bar\nfoo bar\nfoo bar\n', regions=[[(1, 4), (2, 4)]], cmd_params={'mode': modes.VISUAL, 'xpos': 4, 'count': 2},
              expected=region_data([(1, 5), (0, 4)]), actual_func=first_sel_wrapper, msg='move opposite end smaller different lines cross over non 0 xpos'),
    test_data(cmd='_vi_k', initial_text='foo\nbar\nbaz\n', regions=[[(0, 1), (1, 1)]], cmd_params={'mode': modes.VISUAL, 'xpos': 0, 'count': 1},
              expected=region_data([(0, 2), (0, 0)]), actual_func=first_sel_wrapper, msg='move back to same line same xpos'),

    test_data(cmd='_vi_k', initial_text='foo\nbar\nbaz\n', regions=[[(0, 2), (1, 0)]], cmd_params={'mode': modes.VISUAL, 'xpos': 0, 'count': 1},
              expected=region_data([(0, 3), (0, 0)]), actual_func=first_sel_wrapper, msg='move back to same line opposite end has greater xpos'),
    test_data(cmd='_vi_k', initial_text=(''.join(('foo\n',) * 50)), regions=[[(20, 2), (20, 1)]], cmd_params={'mode': modes.VISUAL, 'xpos': 1, 'count': 10},
              expected=region_data([(20, 2), (10, 1)]), actual_func=first_sel_wrapper, msg='move many opposite end greater from same line'),
    test_data(cmd='_vi_k', initial_text=(''.join(('foo\n',) * 50)), regions=[[(21, 2), (20, 1)]], cmd_params={'mode': modes.VISUAL, 'xpos': 1, 'count': 10},
              expected=region_data([(21, 2), (10, 1)]), actual_func=first_sel_wrapper, msg='move many opposite end greater from same line'),

    )


TESTS = TESTS_MODES


class Test_vi_h(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            self.write(data.initial_text)
            for region in data.regions:
                self.add_sel(self.R(*region))

            self.view.run_command(data.cmd, data.cmd_params)

            msg = "failed at test index {0} {1}".format(i, data.msg)
            actual = data.actual_func(self)

            if isinstance(data.expected, region_data):
                self.assertEqual(self.R(*data.expected.regions), actual, msg)
            else:
                self.assertEqual(data.expected, actual, msg)


test = namedtuple('simple_test', 'content regions kwargs expected msg')

MORE_TESTS = (
    test(content='''aaa
bbb
''',
    regions=((1, 1), (1, 1)), kwargs={'mode': modes.NORMAL, 'count': 1, 'xpos': 1}, expected=((0, 1), (0, 1)), msg='from same length'),

    test(content='''

''',
    regions=((1, 0), (1, 0)), kwargs={'mode': modes.NORMAL, 'count': 1, 'xpos': 0}, expected=((0, 0), (0, 0)), msg='from empty to empty'),

    test(content='''
aaa
''',
    regions=((1, 2), (1, 2)), kwargs={'mode': modes.NORMAL, 'count': 1, 'xpos': 2}, expected=((0, 0), (0,0)), msg='from longer to empty'),

    test(content='''aaa

''',
    regions=((1, 0), (1, 0)), kwargs={'mode': modes.NORMAL, 'count': 1, 'xpos': 0}, expected=((0, 0), (0, 0)), msg='from empty to longer'),

    test(content='''aaa bbb
aaa
''',
    regions=((1, 2), (1, 2)), kwargs={'mode': modes.NORMAL, 'count': 1, 'xpos': 2}, expected=((0, 2), (0, 2)), msg='from shorter to longer'),

    test(content='''aaa
aaa bbb
''',
    regions=((1, 6), (1, 6)), kwargs={'mode': modes.NORMAL, 'count': 1, 'xpos': 6}, expected=((0, 2), (0, 2)), msg='from longer to shorter'),

    test(content='''\t\taaa
aaa bbb ccc
''',
    regions=((1, 8), (1, 8)), kwargs={'mode': modes.NORMAL, 'count': 1, 'xpos': 8}, expected=((0, 2), (0, 2)), msg='xpos with tabs'),

    test(content='''aaa
aaa bbb ccc
''',
    regions=((1, 8), (1, 8)), kwargs={'mode': modes.NORMAL, 'count': 1, 'xpos': 1000}, expected=((0, 2), (0, 2)), msg='xpos stops at eol'),

    # VISUAL
    test(content='''aaa

ccc
''',
    regions=(((1, 0), (1, 1)),), kwargs={'mode': modes.VISUAL, 'count': 1, 'xpos': 0}, expected=((1, 1), (0, 0)), msg='from empty to non-empty (visual)'),

    test(content='''aaa bbb ccc ddd
aaa bbb ccc ddd
''',
    regions=(((0, 6), (1, 2)),), kwargs={'mode': modes.VISUAL, 'count': 1, 'xpos': 2}, expected=((0, 7), (0, 2)), msg='from empty to non-empty (visual)'),
)


class Test_vi_k_new(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(MORE_TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            self.write(data.content)
            for region in data.regions:
                self.add_sel(self.R(*region))

            self.view.run_command('_vi_k', data.kwargs)

            msg = "failed at test index {0}: {1}".format(i, data.msg)
            actual = self.view.sel()[0]
            self.assertEqual(self.R(*data.expected), actual, msg)
