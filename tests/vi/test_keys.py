import unittest

import sublime

from Vintageous import state
from Vintageous.vi.utils import modes
from Vintageous.vi.utils import translate_char
from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import make_region
from Vintageous.tests import BufferTest
from Vintageous.vi.keys import to_bare_command_name
from Vintageous.vi.keys import KeySequenceTokenizer


_tests_tokenizer = (
    ('p',            'p',            'lower letter key'),
    ('P',            'P',            'upper case letter key'),
    ('<C-p>',        '<C-p>',        'ctrl-modified lower case letter key'),
    ('<C-P>',        '<C-P>',        'ctrl-modified upper case letter key'),
    ('<C-S-.>',      '<C-S-.>',      'ctrl-shift modified period key'),
    ('<Esc>',        '<esc>',        'esc key title case'),
    ('<esc>',        '<esc>',        'esc key lowercase'),
    ('<eSc>',        '<esc>',        'esc key mixed case'),
    ('<lt>',         '<lt>',         'less than key'),
    ('<HOME>',       '<home>',       'less than key'),
    ('<enD>',        '<end>',        'less than key'),
    ('<uP>',         '<up>',         'less than key'),
    ('<DoWn>',       '<down>',       'less than key'),
    ('<left>',       '<left>',       'less than key'),
    ('<RigHt>',      '<right>',      'less than key'),
    ('<Space>',      '<space>',      'space key'),
    ('<c-Space>',    '<C-space>',    'ctrl-space key'),
    ('0',            '0',            'zero key'),
    ('<c-m-.>',      '<C-M-.>',      'ctrl-alt-period key'),
)


class Test_KeySequenceTokenizer(BufferTest):
    def parse(self, input_):
        tokenizer = KeySequenceTokenizer(input_)
        return tokenizer.tokenize_one()

    def testAll(self):
        for (i, t) in enumerate(_tests_tokenizer):
            input_, expected, msg = t
            self.assertEqual(self.parse(input_), expected, "{0} - {1}".format(i, msg))


_command_name_tests = (
    ('daw', 'daw', ''),
    ('2daw', 'daw', ''),
    ('d2aw', 'daw', ''),
    ('2d2aw', 'daw', ''),
    ('"a2d2aw', 'daw', ''),
    ('"12d2aw', 'daw', ''),
    ('<f7>', '<f7>', ''),
    ('10<f7>', '<f7>', ''),
    ('"a10<f7>', '<f7>', ''),
    ('"a10<f7>', '<f7>', ''),
    ('"210<f7>', '<f7>', ''),
    ('0', '0', ''),
)


class Test_to_bare_command_name(BufferTest):
    def transform(self, input_):
        return to_bare_command_name(input_)

    def testAll(self):
        for (i, t) in enumerate(_command_name_tests):
            input_, expected, msg = t
            self.assertEqual(self.transform(input_), expected, "{0} - {1}".format(i, msg))


_tranlation_tests = (
    ('<enter>', '\n', ''),
    ('<cr>', '\n', ''),
    ('<sp>', ' ', ''),
    ('<space>', ' ', ''),
    ('<lt>', '<', ''),
    ('a', 'a', ''),
)


class Test_translate_char(BufferTest):
    def testAll(self):
        for (i, t) in enumerate(_tranlation_tests):
            input_, expected, msg = t
            self.assertEqual(translate_char(input_), expected, "{0} - {1}".format(i, msg))
