from Vintageous.vi.utils import modes

from collections import namedtuple

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


# TODO: Test against folded regions.
# TODO: Ensure that we only create empty selections while testing. Add assert_all_sels_empty()?
test_data = namedtuple('test_data', 'cmd initial_text regions cmd_params expected actual_func msg')
region_data = namedtuple('region_data', 'regions')


def get_text(test):
    return test.view.substr(test.R(0, test.view.size()))


def  first_sel_wrapper(test):
    return first_sel(test.view)


TESTS_MODES = (
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'xpos': 1},
              expected=region_data([(1, 1), (1, 1)]), actual_func=first_sel_wrapper, msg='move one line down'),
    test_data(cmd='_vi_j', initial_text=(''.join('abc\n' * 60)), regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'count': 50, 'xpos': 1},
              expected=region_data([(50, 1), (50, 1)]), actual_func=first_sel_wrapper, msg='move many lines down'),
    test_data(cmd='_vi_j', initial_text=(''.join('abc\n' * 60)), regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'count': 50, 'xpos': 1},
              expected=region_data([(50, 1), (50, 1)]), actual_func=first_sel_wrapper, msg='move many lines down'),
    test_data(cmd='_vi_j', initial_text='foo\nfoo bar\nfoo bar', regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'count': 1, 'xpos': 1},
              expected=region_data([(1, 1), (1, 1)]), actual_func=first_sel_wrapper, msg='move onto longer line'),
    test_data(cmd='_vi_j', initial_text='foo bar\nfoo\nbar', regions=[[5, 5]], cmd_params={'mode': modes.NORMAL, 'count': 1, 'xpos': 5},
              expected=region_data([(1, 4), (1, 4)]), actual_func=first_sel_wrapper, msg='move onto shorter line'),
    test_data(cmd='_vi_j', initial_text='\nfoo\nbar', regions=[[0, 0]], cmd_params={'mode': modes.NORMAL, 'count': 1, 'xpos': 0},
              expected=region_data([(1, 0), (1, 0)]), actual_func=first_sel_wrapper, msg='move from empty line'),

    test_data(cmd='_vi_j', initial_text='\n\nbar', regions=[[0, 0]], cmd_params={'mode': modes.NORMAL, 'count': 1, 'xpos': 0},
              expected=region_data([(1, 0), (1, 0)]), actual_func=first_sel_wrapper, msg='move from empty line'),
    test_data(cmd='_vi_j', initial_text='foo\nbar\nbaz', regions=[[0, 0]], cmd_params={'mode': modes.NORMAL, 'count': 1, 'xpos': 0},
              expected=region_data([(1, 0), (1, 0)]), actual_func=first_sel_wrapper, msg='move from empty line'),

    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[1, 2]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 1},
              expected=region_data([(0, 1), (1, 2)]), actual_func=first_sel_wrapper, msg='move from empty line'),
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[10, 1]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 1},
              expected=region_data([(0, 10), (1, 1)]), actual_func=first_sel_wrapper, msg='move from empty line'),
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[6, 1]], cmd_params={'mode': modes.VISUAL, 'count': 2, 'xpos': 1},
              expected=region_data([(0, 5), (2, 2)]), actual_func=first_sel_wrapper, msg='move from empty line'),
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[6, 1]], cmd_params={'mode': modes.VISUAL, 'count': 100, 'xpos': 1},
              expected=region_data([(0, 5), (2, 2)]), actual_func=first_sel_wrapper, msg='xxxx'),
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[6, 1]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 1},
              expected=region_data([(1, 1), (0, 6)]), actual_func=first_sel_wrapper, msg='move from empty line'),
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[6, 5]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 1},
              expected=region_data([(0, 5), (2, 2)]), actual_func=first_sel_wrapper, msg='move from empty line'),
    test_data(cmd='_vi_j', initial_text=('abc\n' * 60), regions=[[1, 2]], cmd_params={'mode': modes.VISUAL, 'count': 50, 'xpos': 1},
              expected=region_data([(0, 1), (50, 2)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='foo\nfoo bar\nfoo bar', regions=[[1, 2]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 1},
              expected=region_data([(0, 1), (1, 2)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='foo bar\nfoo\nbar', regions=[[5, 6]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 5},
              expected=region_data([(0, 5), (1, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='\nfoo\nbar', regions=[[0, 1]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 0},
              expected=region_data([(0, 0), (1, 1)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='\n\nbar', regions=[[0, 1]], cmd_params={'mode': modes.VISUAL, 'count': 1, 'xpos': 0},
              expected=region_data([(0, 0), (1, 1)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='foo\nbar\nbaz', regions=[[1, 2]], cmd_params={'mode': modes.VISUAL, 'count': 10000, 'xpos': 1},
              expected=region_data([(0, 1), (2, 2)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[1, 1]], cmd_params={'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 1},
              expected=region_data([(0, 0), (1, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text=('abc\n' * 60), regions=[[1, 1]], cmd_params={'mode': modes.INTERNAL_NORMAL, 'count': 50, 'xpos': 1},
              expected=region_data([(0, 0), (50, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='foo\nfoo bar\nfoo bar', regions=[[1, 1]], cmd_params={'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 1},
              expected=region_data([(0, 0), (1, 8)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='foo bar\nfoo\nbar', regions=[[5, 5]], cmd_params={'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 5},
              expected=region_data([(0, 0), (1, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='\nfoo\nbar', regions=[[0, 0]], cmd_params={'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 0},
              expected=region_data([(0, 0), (1, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='\n\nbar', regions=[[0, 0]], cmd_params={'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 0},
              expected=region_data([(0, 0), (1, 1)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='foo\nbar\nbaz', regions=[[1, 1]], cmd_params={'mode': modes.INTERNAL_NORMAL, 'count': 10000, 'xpos': 1},
              expected=region_data([(0, 0), (2, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[0, 4]], cmd_params={'mode': modes.VISUAL_LINE, 'count': 1, 'xpos': 1},
              expected=region_data([(0, 0), (1, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text=('abc\n' * 60), regions=[[0, 4]], cmd_params={'mode': modes.VISUAL_LINE, 'count': 50, 'xpos': 1},
              expected=region_data([(0, 0), (50, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='\nfoo\nbar', regions=[[0, 1]], cmd_params={'mode': modes.VISUAL_LINE, 'count': 1, 'xpos': 0},
              expected=region_data([(0, 0), (1, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='\n\nbar', regions=[[1, 0]], cmd_params={'mode': modes.VISUAL_LINE, 'count': 1, 'xpos': 0},
              expected=region_data([(0, 0), (1, 1)]), actual_func=first_sel_wrapper, msg='move many lines'),
    test_data(cmd='_vi_j', initial_text='foo\nbar\nbaz', regions=[[0, 4]], cmd_params={'mode': modes.VISUAL_LINE, 'count': 10000, 'xpos': 1},
              expected=region_data([(0, 0), (2, 4)]), actual_func=first_sel_wrapper, msg='move many lines'),
    )


TESTS = TESTS_MODES


class Test_vi_j(ViewTest):
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
