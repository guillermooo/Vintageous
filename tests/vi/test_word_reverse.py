import unittest
from collections import namedtuple

from Vintageous.vi.text_objects import word_reverse
from Vintageous.vi.utils import modes
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


test_data = namedtuple('test_data', 'content args expected msg')


TESTS = (
    test_data(content='abc',           args=(2, 1), expected=0, msg='find word start from the middle of a word'),
    test_data(content='abc abc abc',   args=(8, 1), expected=4, msg='find word start from next word'),
    test_data(content='abc abc abc',   args=(8, 2), expected=0, msg='find word start from next word (count: 2)'),
    test_data(content='abc\nabc\nabc', args=(8, 1), expected=4, msg='find word start from different line'),
    test_data(content='abc\n\nabc',    args=(5, 1), expected=4, msg='stop at empty line'),
    test_data(content='abc a abc',     args=(6, 1), expected=4, msg='stop at single-char word'),
    test_data(content='(abc) abc',     args=(6, 1), expected=4, msg='skip over punctuation simple'),
    test_data(content='abc.(abc)',     args=(5, 1), expected=3, msg='skip over punctuation complex'),
    test_data(content='abc == abc',    args=(7, 1), expected=4, msg='stop at isolated punctuation word'),
)


class Test_word_reverse(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            self.write(data.content)
            actual = word_reverse(self.view, *data.args)

            msg = "failed at test index {0}: {1}".format(i, data.msg)
            self.assertEqual(data.expected, actual, msg)
