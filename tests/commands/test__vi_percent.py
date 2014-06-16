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
    test_data('abc (abc) abc', [[(0, 6), (0, 7)]], {'mode': modes.VISUAL},           [(0, 7), (0, 4)], first_sel, 'visual not on bracket A'),
    test_data('abc (abc) abc', [[(0, 7), (0, 6)]], {'mode': modes.VISUAL},           [(0, 7), (0, 4)], first_sel, 'visual not on bracket B'),
    test_data('0(2)4',         [[(0, 0), (0, 2)]], {'mode': modes.VISUAL},           [(0, 0), (0, 4)], first_sel, 'visual right A'),
    test_data('0(2)4',         [[(0, 1), (0, 2)]], {'mode': modes.VISUAL},           [(0, 1), (0, 4)], first_sel, 'visual right B'),
    test_data('0(2)4',         [[(0, 5), (0, 3)]], {'mode': modes.VISUAL},           [(0, 5), (0, 1)], first_sel, 'visual left A'),
    test_data('0(2)4',         [[(0, 4), (0, 3)]], {'mode': modes.VISUAL},           [(0, 4), (0, 1)], first_sel, 'visual left B'),
    test_data('0(2)4',         [[(0, 2), (0, 4)]], {'mode': modes.VISUAL},           [(0, 3), (0, 1)], first_sel, 'visual right->left A'),
    test_data('0(2)4',         [[(0, 3), (0, 4)]], {'mode': modes.VISUAL},           [(0, 4), (0, 1)], first_sel, 'visual right->left B'),
    test_data('0(2)4',         [[(0, 3), (0, 1)]], {'mode': modes.VISUAL},           [(0, 2), (0, 4)], first_sel, 'visual left->right A'),
    test_data('0(2)4',         [[(0, 2), (0, 1)]], {'mode': modes.VISUAL},           [(0, 1), (0, 4)], first_sel, 'visual left->right B'),
    test_data('()',            [[(0, 0), (0, 1)]], {'mode': modes.VISUAL},           [(0, 0), (0, 2)], first_sel, 'visual off by one right'),
    test_data('()',            [[(0, 2), (0, 1)]], {'mode': modes.VISUAL},           [(0, 2), (0, 0)], first_sel, 'visual off by one left'),
    test_data('()',            [[(0, 1), (0, 2)]], {'mode': modes.VISUAL},           [(0, 2), (0, 0)], first_sel, 'visual off by one right->left'),
    test_data('()',            [[(0, 1), (0, 0)]], {'mode': modes.VISUAL},           [(0, 0), (0, 2)], first_sel, 'visual off by one left->right'),
    test_data('abc (abc) abc', [[(0, 6), (0, 6)]], {'mode': modes.INTERNAL_NORMAL},  [(0, 7), (0, 4)], first_sel, ''),
    test_data('abc (abc) abc', [[(0, 8), (0, 8)]], {'mode': modes.INTERNAL_NORMAL},  [(0, 9), (0, 4)], first_sel, ''),
    test_data('abc (abc) abc', [[(0, 4), (0, 4)]], {'mode': modes.INTERNAL_NORMAL},  [(0, 4), (0, 9)], first_sel, ''),
    test_data('abc (abc) abc', [[(0, 0), (0, 0)]], {'mode': modes.INTERNAL_NORMAL},  [(0, 0), (0, 9)], first_sel, ''),
    # TODO: test multiline brackets, etc.
)


class Test__vi_percent(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            self.write(data.initial_text)
            for region in data.regions:
                self.clear_sel()
                self.add_sel(self.R(*region))

            self.view.run_command('_vi_percent', data.cmd_params)

            msg = "[{0}] {1}".format(i, data.msg)
            actual = data.actual_func(self.view)
            self.assertEqual(self.R(*data.expected), actual, msg)
