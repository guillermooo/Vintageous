from Vintageous.vi.utils import modes

from collections import namedtuple

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


test_data = namedtuple('test_data', 'cmd initial_text regions cmd_params expected actual_func msg')
region_data = namedtuple('region_data', 'regions')


def get_text(test):
    return test.view.substr(test.R(0, test.view.size()))

def  first_sel_wrapper(test):
    return first_sel(test.view)


TESTS_MODES = (
    # NORMAL mode
    test_data(cmd='_vi_h', initial_text='abc', regions=[[1, 1]], cmd_params={'mode': modes.NORMAL},
              expected=region_data([0, 0]), actual_func=first_sel_wrapper, msg='should move back one char (normal mode)'),
    test_data(cmd='_vi_h', initial_text='foo bar baz', regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'count': 10},
              expected=region_data([0, 0]), actual_func=first_sel_wrapper, msg='should move back one char with count (normal mode)'),
    test_data(cmd='_vi_h', initial_text='abc', regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'count': 10000},
              expected=region_data([0, 0]), actual_func=first_sel_wrapper, msg='should move back one char with large count (normal mode)'),

    test_data(cmd='_vi_h', initial_text='abc', regions=[[1, 1]], cmd_params={'mode': modes.INTERNAL_NORMAL},
              expected=region_data([1, 0]), actual_func=first_sel_wrapper, msg='should select one char (internal normal mode)'),
    test_data(cmd='_vi_h', initial_text='foo bar baz', regions=[[10, 10]], cmd_params={'mode': modes.INTERNAL_NORMAL},
              expected=region_data([10, 9]), actual_func=first_sel_wrapper, msg='should select one char from eol (internal normal mode)'),
    test_data(cmd='_vi_h', initial_text='foo bar baz', regions=[[1, 1]], cmd_params={'mode': modes.INTERNAL_NORMAL, 'count': 10000},
              expected=region_data([1, 0]), actual_func=first_sel_wrapper, msg='should select one char large count (internal normal mode)'),

    test_data(cmd='_vi_h', initial_text='abc', regions=[[1, 2]], cmd_params={'mode': modes.VISUAL},
              expected=region_data([2, 0]), actual_func=first_sel_wrapper, msg='should select one char (visual mode)'),
    test_data(cmd='_vi_h', initial_text='abc', regions=[[1, 3]], cmd_params={'mode': modes.VISUAL, 'count': 1},
              expected=region_data([1, 2]), actual_func=first_sel_wrapper, msg='should deselect one char (visual mode)'),
    test_data(cmd='_vi_h', initial_text='abc', regions=[[1, 3]], cmd_params={'mode': modes.VISUAL, 'count': 2},
              expected=region_data([2, 0]), actual_func=first_sel_wrapper, msg='should go back two chars (visual mode) crossing over'),

    test_data(cmd='_vi_h', initial_text='abc', regions=[[1, 3]], cmd_params={'mode': modes.VISUAL, 'count': 100},
              expected=region_data([2, 0]), actual_func=first_sel_wrapper, msg='can move reversed cross over large count visual mode'),
    test_data(cmd='_vi_h', initial_text='foo bar fuzz buzz', regions=[[11, 12]], cmd_params={'mode': modes.VISUAL, 'count': 10},
              expected=region_data([12, 1]), actual_func=first_sel_wrapper, msg='can move with count visual mode'),
    test_data(cmd='_vi_h', initial_text='abc\n', regions=[[1, 2]], cmd_params={'mode': modes.VISUAL, 'count': 10000},
              expected=region_data([2, 0]), actual_func=first_sel_wrapper, msg='stops at left end'),

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