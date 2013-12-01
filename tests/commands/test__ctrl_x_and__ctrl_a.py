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
    test_data('abc aaa100bbb abc', [[(0, 0), (0, 0)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10}, 'abc aaa110bbb abc', ''),
    test_data('abc aaa-100bbb abc', [[(0, 0), (0, 0)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10}, 'abc aaa-90bbb abc', ''),

    test_data('abc aaa100bbb abc', [[(0, 8), (0, 8)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10}, 'abc aaa110bbb abc', ''),
    test_data('abc aaa-100bbb abc', [[(0, 8), (0, 8)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10}, 'abc aaa-90bbb abc', ''),

    test_data('abc aaa100bbb abc\nabc aaa100bbb abc', [[(0, 0), (0, 0)], [(1, 0), (1, 0)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10}, 'abc aaa110bbb abc\nabc aaa110bbb abc', ''),
    test_data('abc aaa-100bbb abc\nabc aaa-100bbb abc', [[(0, 0), (0, 0)], [(1, 0), (1, 0)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10}, 'abc aaa-90bbb abc\nabc aaa-90bbb abc', ''),

    test_data('abc aaa100bbb abc\nabc aaa100bbb abc', [[(0, 8), (0, 8)], [(1, 8), (1, 8)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10}, 'abc aaa110bbb abc\nabc aaa110bbb abc', ''),
    test_data('abc aaa-100bbb abc\nabc aaa-100bbb abc', [[(0, 0), (0, 0)], [(1, 8), (1, 8)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10}, 'abc aaa-90bbb abc\nabc aaa-90bbb abc', ''),

    test_data('abc aaa100bbb abc', [[(0, 0), (0, 0)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10, 'subtract': True}, 'abc aaa90bbb abc', ''),
    test_data('abc aaa-100bbb abc', [[(0, 0), (0, 0)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10, 'subtract': True}, 'abc aaa-110bbb abc', ''),

    test_data('abc aaa100bbb abc', [[(0, 8), (0, 8)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10, 'subtract': True}, 'abc aaa90bbb abc', ''),
    test_data('abc aaa-100bbb abc', [[(0, 8), (0, 8)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10, 'subtract': True}, 'abc aaa-110bbb abc', ''),

    test_data('abc aaa100bbb abc\nabc aaa100bbb abc', [[(0, 0), (0, 0)], [(1, 0), (1, 0)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10, 'subtract': True}, 'abc aaa90bbb abc\nabc aaa90bbb abc', ''),
    test_data('abc aaa-100bbb abc\nabc aaa-100bbb abc', [[(0, 0), (0, 0)], [(1, 0), (1, 0)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10, 'subtract': True}, 'abc aaa-110bbb abc\nabc aaa-110bbb abc', ''),

    test_data('abc aaa100bbb abc\nabc aaa100bbb abc', [[(0, 8), (0, 8)], [(1, 8), (1, 8)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10, 'subtract': True}, 'abc aaa90bbb abc\nabc aaa90bbb abc', ''),
    test_data('abc aaa-100bbb abc\nabc aaa-100bbb abc', [[(0, 0), (0, 0)], [(1, 8), (1, 8)]], {'mode':_MODE_INTERNAL_NORMAL, 'count': 10, 'subtract': True}, 'abc aaa-110bbb abc\nabc aaa-110bbb abc', ''),

    # TODO: Test with sels on same line.
    # TODO: Test with standalone number.
    # TODO: Test with number followed by suffix.
)


class Test__vi_ctrl_x(BufferTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            set_text(self.view, data.initial_text)
            for region in data.regions:
                add_sel(self.view, self.R(*region))

            self.view.run_command('_vi_modify_numbers', data.cmd_params)

            msg = "[{0}] {1}".format(i, data.msg)
            actual = self.view.substr(self.R(0, self.view.size()))
            self.assertEqual(data.expected, actual, msg)
