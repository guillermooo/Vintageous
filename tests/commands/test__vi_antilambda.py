from collections import namedtuple

from Vintageous.vi.utils import modes

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import second_sel
from Vintageous.tests import ViewTest


test_data = namedtuple('test_data', 'initial_text regions cmd_params expected msg')

TESTS = (
    test_data('    abc',                   [[(0, 0), (0, 0)]],                   {'mode': modes.INTERNAL_NORMAL, 'count': 1}, 'abc',               'failed in {0}'),
    test_data('        abc',               [[(0, 0), (0, 0)]],                   {'mode': modes.INTERNAL_NORMAL, 'count': 1}, '    abc',           'failed in {0}'),
    test_data('    abc\n    abc',          [[(0, 0), (0, 0)]],                   {'mode': modes.INTERNAL_NORMAL, 'count': 2}, 'abc\nabc',          'failed in {0}'),
    test_data('    abc\n    abc\n    abc', [[(0, 0), (0, 0)]],                   {'mode': modes.INTERNAL_NORMAL, 'count': 3}, 'abc\nabc\nabc',     'failed in {0}'),
    test_data('    abc\n    abc\n    abc', [[(0, 0), (0, 0)], [(1, 0), (1, 0)]], {'mode': modes.INTERNAL_NORMAL, 'count': 1}, 'abc\nabc\n    abc', 'failed in {0}'),
)


class Test__vi_double_antilambda(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            self.write(data.initial_text)
            for region in data.regions:
                add_sel(self.view, self.R(*region))

            self.view.run_command('_vi_less_than_less_than', data.cmd_params)

            msg = "[{0}] {1}".format(i, data.msg)
            actual = self.view.substr(self.R(0, self.view.size()))
            self.assertEqual(data.expected, actual, msg.format(i))
