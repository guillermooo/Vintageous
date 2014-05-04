import unittest
from collections import namedtuple

from Vintageous.vi.text_objects import word_end_reverse
from Vintageous.vi.utils import modes
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


test_data = namedtuple('test_data', 'content args expected msg')


TESTS = (
    test_data(content='abc',           args=(2, 1), expected=0, msg='go to bof from first word'),
    test_data(content='abc abc abc',   args=(8, 1), expected=6, msg='go to previous word end'),
    test_data(content='abc abc abc',   args=(8, 2), expected=2, msg='go to previous word end (count: 2)'),
    test_data(content='abc\nabc\nabc', args=(8, 1), expected=6, msg='go to previous word end over white space'),
    test_data(content='abc\n\nabc',    args=(5, 1), expected=3, msg='stop at empty line'),
    test_data(content='abc a abc',     args=(6, 1), expected=4, msg='stop at single-char word'),
    test_data(content='abc == abc',    args=(7, 1), expected=5, msg='stop at isolated punctuation word'),
    test_data(content='abc =',         args=(4, 1), expected=2, msg='stop at word end from isolated punctuation'),
    test_data(content='abc abc.abc',   args=(7, 1), expected=6, msg='stop at previous word end from contiguous punctuation'),

    test_data(content='abc abc.abc',   args=(10, 1, True), expected=2, msg='skip over punctuation'),
    test_data(content='abc ',          args=(3, 1), expected=2, msg='stop at previous word end if starting from contiguous space'),
)


class Test_word_end_reverse(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            self.write(data.content)
            actual = word_end_reverse(self.view, *data.args)

            msg = "failed at test index {0}: {1}".format(i, data.msg)
            self.assertEqual(data.expected, actual, msg)
