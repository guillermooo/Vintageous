import unittest
from collections import namedtuple

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import BufferTest


test_data = namedtuple('test_data', 'initial_text regions cmd_params expected msg')

TESTS = (
    test_data('abc\nabc\nabc',                           [[(0, 0), (0, 0)]], {'mode': _MODE_INTERNAL_NORMAL, 'count': 1}, 'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\n    abc\nabc',                       [[(0, 0), (0, 0)]], {'mode': _MODE_INTERNAL_NORMAL, 'count': 1}, 'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 0), (0, 0)]], {'mode': _MODE_INTERNAL_NORMAL, 'count': 2}, 'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\n    abc\nabc',                       [[(0, 0), (0, 0)]], {'mode': _MODE_INTERNAL_NORMAL, 'count': 2}, 'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 0), (0, 0)]], {'mode': _MODE_INTERNAL_NORMAL, 'count': 3}, 'abc abc abc',         'should join 3 lines'),
    test_data('abc\n    abc\n    abc',                   [[(0, 0), (0, 0)]], {'mode': _MODE_INTERNAL_NORMAL, 'count': 3}, 'abc abc abc',         'should join 3 lines'),
    test_data('abc\nabc\nabc\nabc\nabc',                 [[(0, 0), (0, 0)]], {'mode': _MODE_INTERNAL_NORMAL, 'count': 5}, 'abc abc abc abc abc', 'should join 5 lines'),
    test_data('abc\n    abc\n    abc\n    abc\n    abc', [[(0, 0), (0, 0)]], {'mode': _MODE_INTERNAL_NORMAL, 'count': 5}, 'abc abc abc abc abc', 'should join 5 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 0), (0, 1)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\n    abc\nabc',                       [[(0, 0), (0, 1)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 0), (0, 1)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\n    abc\nabc',                       [[(0, 0), (0, 1)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 1), (0, 0)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\n    abc\nabc',                       [[(0, 1), (0, 0)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 1), (0, 0)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\n    abc\nabc',                       [[(0, 1), (0, 0)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 0), (1, 1)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\n    abc\nabc',                       [[(0, 0), (1, 1)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\nabc\nabc',                           [[(1, 1), (0, 0)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\n    abc\nabc',                       [[(1, 1), (0, 0)]], {'mode': MODE_VISUAL},                       'abc abc\nabc',        'should join 2 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 0), (2, 1)]], {'mode': MODE_VISUAL},                       'abc abc abc',         'should join 3 lines'),
    test_data('abc\n    abc\nabc',                       [[(0, 0), (2, 1)]], {'mode': MODE_VISUAL},                       'abc abc abc',         'should join 3 lines'),
    test_data('abc\nabc\nabc',                           [[(2, 1), (0, 0)]], {'mode': MODE_VISUAL},                       'abc abc abc',         'should join 3 lines'),
    test_data('abc\n    abc\nabc',                       [[(2, 1), (0, 0)]], {'mode': MODE_VISUAL},                       'abc abc abc',         'should join 3 lines'),
    test_data('abc\nabc\nabc',                           [[(0, 0), (1, 1)]], {'mode': MODE_VISUAL, 'count': 3},           'abc abc\nabc',        'should join 2 lines - count shouldn\'t matter'),
    test_data('abc\n    abc\nabc',                       [[(0, 0), (1, 1)]], {'mode': MODE_VISUAL, 'count': 3},           'abc abc\nabc',        'should join 2 lines - count shouldn\'t matter'),
)


class Test_vi_big_j(BufferTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            set_text(self.view, data.initial_text)
            for region in data.regions:
                add_sel(self.view, self.R(*region))

            self.view.run_command('_vi_big_j', data.cmd_params)

            actual = self.view.substr(self.R(0, self.view.size()))
            msg = "[{0}] {1}".format(i, data.msg)
            self.assertEqual(data.expected, actual, msg)
