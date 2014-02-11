import unittest

import sublime

from Vintageous import state
from Vintageous.vi.utils import modes
from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import make_region
from Vintageous.tests import BufferTest
from Vintageous.vi.keys import parse_sequence


_tests = (
    ('p', ['p'], 'lower letter key'),
    ('P', ['P'], 'upper case letter key'),
    ('<ctrl+p>', ['<ctrl+p>'], 'ctrl-modified lower case letter key'),
    ('<ctrl+P>', ['<ctrl+P>'], 'ctrl-modified upper case letter key'),
    ('<ctrl+alt+p>', ['<ctrl+alt+p>'], 'ctrl-alt modified lower case letter key'),
    ('<alt+ctrl+p>', ['<alt+ctrl+p>'], 'alt-ctrl modified lower case letter key'),
    ('<Esc>', ['<Esc>'], 'esc key title case'),
    ('<esc>', ['<esc>'], 'esc key lowercase'),
    ('<eSc>', ['<eSc>'], 'esc key mixed case'),
    ('<', ['<'], 'less than key'),
    ('<space>', ['<'], 'space key'),
)


class StateTestCase(BufferTest):
    def parse(self, input_):
        return list(parse_sequence(input_))

    def testAll(self):
        for (i, t) in enumerate(_tests):
            input_, expected, msg = t
            self.assertEqual(self.parse(input_), expected, "{0} - {1}".format(i, msg))
