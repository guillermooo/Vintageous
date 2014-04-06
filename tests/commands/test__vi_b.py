from collections import namedtuple

from Vintageous.vi.utils import modes

from Vintageous.tests import first_sel
from Vintageous.tests import second_sel
from Vintageous.tests import ViewTest


test_data = namedtuple('test_data', 'initial_text regions cmd_params expected actual_func msg')

TESTS_NORMAL_MODE_SINGLE_SEL = (
    test_data(initial_text='abc',     regions=[[(0, 2), (0, 2)]], cmd_params={'mode': modes.NORMAL},  expected=[(0, 0), (0, 0)], actual_func=first_sel,  msg=''),
    test_data(initial_text='abc abc', regions=[[(0, 4), (0, 4)]], cmd_params={'mode': modes.NORMAL},  expected=[(0, 0), (0, 0)], actual_func=first_sel,  msg=''),
    test_data(initial_text='abc a',   regions=[[(0, 4), (0, 4)]], cmd_params={'mode': modes.NORMAL},  expected=[(0, 0), (0, 0)], actual_func=first_sel,  msg=''),
    )

TESTS_VISUAL_MODE_SINGLE_SEL_START_LEN_1 = (
    test_data(initial_text='abc',   regions=[[(0, 2), (0, 3)]], cmd_params={'mode': modes.VISUAL},  expected=[(0, 3), (0, 0)], actual_func=first_sel,  msg=''),
    test_data(initial_text='abc a', regions=[[(0, 4), (0, 5)]], cmd_params={'mode': modes.VISUAL},  expected=[(0, 5), (0, 0)], actual_func=first_sel,  msg=''),
    )

TESTS = TESTS_NORMAL_MODE_SINGLE_SEL + TESTS_VISUAL_MODE_SINGLE_SEL_START_LEN_1


class Test_vi_b(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            self.write(data.initial_text)
            for region in data.regions:
                self.add_sel(self.R(*region))

            self.view.run_command('_vi_b', data.cmd_params)

            msg = "failed at test index {0} {1}".format(i, data.msg)
            actual = data.actual_func(self.view)
            self.assertEqual(self.R(*data.expected), actual, msg)
