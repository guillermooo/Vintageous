from collections import namedtuple

from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import second_sel
from Vintageous.tests import ViewTest


test_data = namedtuple('test_data', 'initial_text regions cmd_params expected actual_func msg')

TESTS = (
    test_data('abc',           [[(0, 0), (0, 2)]],                   {'mode': modes.INTERNAL_NORMAL}, [(0, 0), (0, 0)], first_sel, ''),
    test_data('abc\nabc',      [[(0, 1), (0, 1)], [(1, 1), (1, 1)]], {'mode': modes.INTERNAL_NORMAL}, [(0, 0), (0, 0)], first_sel, ''),
    test_data('abc\nabc',      [[(0, 1), (0, 1)], [(1, 1), (1, 1)]], {'mode': modes.INTERNAL_NORMAL}, [(1, 0), (1, 0)], second_sel, ''),
    test_data('abc',           [[(0, 0), (0, 2)]],                   {'mode': modes.VISUAL},           [(0, 0), (0, 0)], first_sel, ''),
    test_data('abc\nabc',      [[(0, 1), (0, 2)], [(1, 1), (1, 2)]], {'mode': modes.VISUAL},           [(0, 0), (0, 0)], first_sel, ''),
    test_data('abc\nabc',      [[(0, 1), (0, 2)], [(1, 1), (1, 2)]], {'mode': modes.VISUAL},           [(1, 0), (1, 0)], second_sel, ''),
    test_data('abc\nabc\nabc', [[(0, 0), (1, 4)]],                   {'mode': modes.VISUAL_LINE},      [(0, 0), (0, 0)], first_sel, ''),
    test_data('abc\nabc\nabc', [[(1, 0), (2, 4)]],                   {'mode': modes.VISUAL_LINE},      [(1, 0), (1, 0)], first_sel, ''),
    test_data('abc\nabc',      [[(0, 2), (0, 3)], [(1, 2), (1, 3)]], {'mode': modes.VISUAL_BLOCK},     [(0, 2), (0, 2)], first_sel, ''),
    test_data('abc\nabc',      [[(0, 2), (0, 3)], [(1, 2), (1, 3)]], {'mode': modes.VISUAL_BLOCK},     [(1, 2), (1, 2)], second_sel, ''),
)


class Test_vi_big_i(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            set_text(self.view, data.initial_text)
            for region in data.regions:
                self.add_sel(self.R(*region))

            self.view.run_command('_vi_big_i', data.cmd_params)

            msg = "[{0}] {1}".format(i, data.msg)
            actual = data.actual_func(self.view)
            self.assertEqual(self.R(*data.expected), actual, msg)
