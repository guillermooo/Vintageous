import unittest
from collections import namedtuple

import sublime

from Vintageous import state
from Vintageous.vi.utils import modes
from Vintageous.vi.utils import translate_char
from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import make_region
from Vintageous.tests import ViewTest
from Vintageous.tests import ViewTest
from Vintageous.vi.keys import to_bare_command_name
from Vintageous.vi.keys import KeySequenceTokenizer
from Vintageous.vi.keys import seqs
from Vintageous.vi import variables


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
    ('<tab>',        '<tab>',        'tab key'),
    ('<Leader>',     '\\',     'leader key'),
)


class Test_KeySequenceTokenizer_tokenize_one(ViewTest):
    def setUp(self):
        super().setUp()
        self.old_vars = variables._VARIABLES
        variables._VARIABLES = {}

    def parse(self, input_):
        tokenizer = KeySequenceTokenizer(input_)
        return tokenizer.tokenize_one()

    def testAll(self):
        for (i, t) in enumerate(_tests_tokenizer):
            input_, expected, msg = t
            self.assertEqual(self.parse(input_), expected, "{0} - {1}".format(i, msg))

    def tearDown(self):
        super().tearDown()
        variables._VARIABLES = self.old_vars


_tests_iter_tokenize = (
    ('pp',         ['p', 'p'],                     'sequence'),
    ('<C-p>',      ['<C-p>'],                      'sequence'),
    ('<C-P>x',     ['<C-P>', 'x'],                 'sequence'),
    ('<C-S-.>',    ['<C-S-.>'],                    'sequence'),
    ('<Esc>ai',    ['<esc>', 'a', 'i'],            'sequence'),
    ('<lt><lt>',   ['<lt>', '<lt>'],               'sequence'),
    ('<DoWn>abc.', ['<down>', 'a', 'b', 'c', '.'], 'sequence'),
    ('0<down>',    ['0', '<down>'],                'sequence'),
    ('<c-m-.>',    ['<C-M-.>'],                    'sequence'),
)


class Test_KeySequenceTokenizer_iter_tokenize(ViewTest):
    def parse(self, input_):
        tokenizer = KeySequenceTokenizer(input_)
        return list(tokenizer.iter_tokenize())

    def testAll(self):
        for (i, t) in enumerate(_tests_iter_tokenize):
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


class Test_to_bare_command_name(ViewTest):
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


class Test_translate_char(ViewTest):
    def testAll(self):
        for (i, t) in enumerate(_tranlation_tests):
            input_, expected, msg = t
            self.assertEqual(translate_char(input_), expected, "{0} - {1}".format(i, msg))


seq_test = namedtuple('seq_test', 'actual expected')


TESTS_KNOWN_SEQUENCES = (
    seq_test(actual=seqs.A,          expected='a'),
    seq_test(actual=seqs.ALT_CTRL_P, expected='<C-M-p>'),
    seq_test(actual=seqs.AMPERSAND , expected='&'),
    seq_test(actual=seqs.AW,         expected='aw'),
    seq_test(actual=seqs.B,          expected='b'),
    seq_test(actual=seqs.BACKSPACE,  expected='<bs>'),
    seq_test(actual=seqs.GE,         expected='ge'),
    seq_test(actual=seqs.G_BIG_E,    expected='gE'),
    seq_test(actual=seqs.UP,         expected='<up>'),
    seq_test(actual=seqs.DOWN,       expected='<down>'),
    seq_test(actual=seqs.LEFT,       expected='<left>'),
    seq_test(actual=seqs.RIGHT,      expected='<right>'),
    seq_test(actual=seqs.HOME,       expected='<home>'),
    seq_test(actual=seqs.END,        expected='<end>'),
    seq_test(actual=seqs.BACKTICK,   expected='`'),
    seq_test(actual=seqs.BIG_A,      expected='A'),
    seq_test(actual=seqs.SPACE,      expected='<space>'),
    seq_test(actual=seqs.BIG_B,      expected='B'),
    seq_test(actual=seqs.CTRL_E,     expected='<C-e>'),
    seq_test(actual=seqs.CTRL_Y,     expected='<C-y>'),
    seq_test(actual=seqs.BIG_C,      expected='C'),
    seq_test(actual=seqs.BIG_D,      expected='D'),
    seq_test(actual=seqs.GH,         expected='gh'),
    seq_test(actual=seqs.G_BIG_H,    expected='gH'),
    seq_test(actual=seqs.BIG_E,      expected='E'),
    seq_test(actual=seqs.BIG_F,      expected='F'),
    seq_test(actual=seqs.BIG_G,      expected='G'),

    seq_test(actual=seqs.CTRL_0,    expected='<C-0>'),
    seq_test(actual=seqs.CTRL_1,    expected='<C-1>'),
    seq_test(actual=seqs.CTRL_2,    expected='<C-2>'),
    seq_test(actual=seqs.CTRL_3,    expected='<C-3>'),
    seq_test(actual=seqs.CTRL_4,    expected='<C-4>'),
    seq_test(actual=seqs.CTRL_5,    expected='<C-5>'),
    seq_test(actual=seqs.CTRL_6,    expected='<C-6>'),
    seq_test(actual=seqs.CTRL_7,    expected='<C-7>'),
    seq_test(actual=seqs.CTRL_8,    expected='<C-8>'),
    seq_test(actual=seqs.CTRL_9,    expected='<C-9>'),

    seq_test(actual=seqs.CTRL_C,               expected='<C-c>'),
    seq_test(actual=seqs.CTRL_ENTER,           expected='<C-cr>'),
    seq_test(actual=seqs.CTRL_SHIFT_B,         expected='<C-S-b>'),
    seq_test(actual=seqs.CTRL_SHIFT_ENTER,     expected='<C-S-cr>'),
    seq_test(actual=seqs.CTRL_DOT,             expected='<C-.>'),
    seq_test(actual=seqs.CTRL_SHIFT_DOT,       expected='<C-S-.>'),
    seq_test(actual=seqs.CTRL_LEFT_SQUARE_BRACKET, expected='<C-[>'),

    seq_test(actual=seqs.CTRL_W,     expected='<C-w>'),
    seq_test(actual=seqs.CTRL_W_Q,   expected='<C-w>q'),

    seq_test(actual=seqs.CTRL_W_V,        expected='<C-w>v'),
    seq_test(actual=seqs.CTRL_W_L,        expected='<C-w>l'),
    seq_test(actual=seqs.CTRL_W_BIG_L,    expected='<C-w>L'),
    seq_test(actual=seqs.CTRL_K,          expected='<C-k>'),
    seq_test(actual=seqs.CTRL_K_CTRL_B,   expected='<C-k><C-b>'),
    seq_test(actual=seqs.CTRL_BIG_F,      expected='<C-F>'),
    seq_test(actual=seqs.CTRL_BIG_P,      expected='<C-P>'),
    seq_test(actual=seqs.CTRL_W_H,        expected='<C-w>h'),
    seq_test(actual=seqs.Q,               expected='q'),
    seq_test(actual=seqs.AT,              expected='@'),
    seq_test(actual=seqs.CTRL_W_BIG_H,    expected='<C-w>H'),
    seq_test(actual=seqs.BIG_H,           expected='H'),

    seq_test(actual=seqs.G_BIG_J,         expected='gJ'),
    seq_test(actual=seqs.CTRL_R,          expected='<C-r>'),
    seq_test(actual=seqs.CTRL_R_EQUAL,    expected='<C-r>='),
    seq_test(actual=seqs.CTRL_A,          expected='<C-a>'),
    seq_test(actual=seqs.CTRL_I,          expected='<C-i>'),
    seq_test(actual=seqs.CTRL_O,          expected='<C-o>'),
    seq_test(actual=seqs.CTRL_X,          expected='<C-x>'),
    seq_test(actual=seqs.CTRL_X_CTRL_L,   expected='<C-x><C-l>'),
    seq_test(actual=seqs.Z,               expected='z'),
    seq_test(actual=seqs.Z_ENTER,         expected='z<cr>'),
    seq_test(actual=seqs.ZT,              expected='zt'),
    seq_test(actual=seqs.ZZ,              expected='zz'),
    seq_test(actual=seqs.Z_MINUS,         expected='z-'),
    seq_test(actual=seqs.ZB,              expected='zb'),

    seq_test(actual=seqs.BIG_I,                expected='I'),
    seq_test(actual=seqs.BIG_Z_BIG_Z,          expected='ZZ'),
    seq_test(actual=seqs.BIG_Z_BIG_Q,          expected='ZQ'),
    seq_test(actual=seqs.GV,                   expected='gv'),
    seq_test(actual=seqs.BIG_J,                expected='J'),
    seq_test(actual=seqs.BIG_K,                expected='K'),
    seq_test(actual=seqs.BIG_L,                expected='L'),
    seq_test(actual=seqs.BIG_M,                expected='M'),
    seq_test(actual=seqs.BIG_N,                expected='N'),
    seq_test(actual=seqs.BIG_O,                expected='O'),
    seq_test(actual=seqs.BIG_P,                expected='P'),
    seq_test(actual=seqs.BIG_Q,                expected='Q'),
    seq_test(actual=seqs.BIG_R,                expected='R'),
    seq_test(actual=seqs.BIG_S,                expected='S'),
    seq_test(actual=seqs.BIG_T,                expected='T'),
    seq_test(actual=seqs.BIG_U,                expected='U'),
    seq_test(actual=seqs.BIG_V,                expected='V'),
    seq_test(actual=seqs.BIG_W,                expected='W'),
    seq_test(actual=seqs.BIG_X,                expected='X'),
    seq_test(actual=seqs.BIG_Y,                expected='Y'),
    seq_test(actual=seqs.BIG_Z,                expected='Z'),
    seq_test(actual=seqs.C,                    expected= 'c'),
    seq_test(actual=seqs.CC,                   expected='cc'),
    seq_test(actual=seqs.COLON,                expected=':'),
    seq_test(actual=seqs.COMMA,                expected=','),
    seq_test(actual=seqs.CTRL_D,               expected='<C-d>'),
    seq_test(actual=seqs.CTRL_F12,             expected='<C-f12>'),
    seq_test(actual=seqs.CTRL_L,               expected='<C-l>'),
    seq_test(actual=seqs.CTRL_B,               expected='<C-b>'),
    seq_test(actual=seqs.CTRL_F,               expected='<C-f>'),
    seq_test(actual=seqs.CTRL_G,               expected='<C-g>'),
    seq_test(actual=seqs.CTRL_P,               expected='<C-p>'),
    seq_test(actual=seqs.CTRL_U,               expected='<C-u>'),
    seq_test(actual=seqs.CTRL_V,               expected='<C-v>'),
    seq_test(actual=seqs.D,                    expected='d'),
    seq_test(actual=seqs.DD,                   expected='dd'),
    seq_test(actual=seqs.DOLLAR,               expected='$'),
    seq_test(actual=seqs.DOT,                  expected='.'),
    seq_test(actual=seqs.DOUBLE_QUOTE,         expected='"'),
    seq_test(actual=seqs.E,                    expected='e'),
    seq_test(actual=seqs.ENTER,                expected='<cr>'),
    seq_test(actual=seqs.SHIFT_ENTER,          expected='<S-cr>'),
    seq_test(actual=seqs.EQUAL,                expected='='),
    seq_test(actual=seqs.EQUAL_EQUAL,          expected='=='),
    seq_test(actual=seqs.ESC,                  expected='<esc>'),
    seq_test(actual=seqs.F,                    expected='f'),
    seq_test(actual=seqs.F1,                   expected='<f1>'),
    seq_test(actual=seqs.F10,                  expected='<f10>'),
    seq_test(actual=seqs.F11,                  expected='<f11>'),
    seq_test(actual=seqs.F12,                  expected='<f12>'),
    seq_test(actual=seqs.F13,                  expected='<f13>'),
    seq_test(actual=seqs.F14,                  expected='<f14>'),
    seq_test(actual=seqs.F15,                  expected='<f15>'),
    seq_test(actual=seqs.F2,                   expected='<f2>'),
    seq_test(actual=seqs.F3,                   expected='<f3>'),
    seq_test(actual=seqs.SHIFT_F2,             expected='<S-f2>'),
    seq_test(actual=seqs.SHIFT_F3,             expected='<S-f3>'),
    seq_test(actual=seqs.SHIFT_F4,             expected='<S-f4>'),
    seq_test(actual=seqs.F4,                   expected='<f4>'),
    seq_test(actual=seqs.F5,                   expected='<f5>'),
    seq_test(actual=seqs.F6,                   expected='<f6>'),
    seq_test(actual=seqs.F7,                   expected='<f7>'),
    seq_test(actual=seqs.F8,                   expected='<f8>'),
    seq_test(actual=seqs.F9,                   expected='<f9>'),
    seq_test(actual=seqs.CTRL_F2,              expected='<C-f2>'),
    seq_test(actual=seqs.CTRL_SHIFT_F2,        expected='<C-S-f2>'),
    seq_test(actual=seqs.G,                    expected='g'),
    seq_test(actual=seqs.G_BIG_C,              expected='gC'),
    seq_test(actual=seqs.G_BIG_D,              expected='gD'),
    seq_test(actual=seqs.G_BIG_U,              expected='gU'),
    seq_test(actual=seqs.G_BIG_U_BIG_U,        expected='gUU'),
    seq_test(actual=seqs.G_BIG_U_G_BIG_U,      expected='gUgU'),
    seq_test(actual=seqs.G_TILDE,              expected='g~'),
    seq_test(actual=seqs.G_TILDE_G_TILDE,      expected='g~g~'),
    seq_test(actual=seqs.G_TILDE_TILDE,        expected='g~~'),
    seq_test(actual=seqs.G_UNDERSCORE,         expected='g_'),
    seq_test(actual=seqs.GC,                   expected='gc'),
    seq_test(actual=seqs.GCC,                  expected='gcc'),
    seq_test(actual=seqs.GD,                   expected='gd'),
    seq_test(actual=seqs.GG,                   expected='gg'),
    seq_test(actual=seqs.GJ,                   expected='gj'),
    seq_test(actual=seqs.GK,                   expected='gk'),
    seq_test(actual=seqs.GQ,                   expected='gq'),
    seq_test(actual=seqs.GT,                   expected='gt'),
    seq_test(actual=seqs.G_BIG_T,              expected= 'gT'),
    seq_test(actual=seqs.GM,                   expected= 'gm'),
    seq_test(actual=seqs.GU,                   expected= 'gu'),
    seq_test(actual=seqs.GUGU,                 expected= 'gugu'),
    seq_test(actual=seqs.GUU,                  expected= 'guu'),
    seq_test(actual=seqs.GREATER_THAN,         expected= '>'),
    seq_test(actual=seqs.GREATER_THAN_GREATER_THAN, expected= '>>'),
    seq_test(actual=seqs.H,                      expected= 'h'),
    seq_test(actual=seqs.HAT,                    expected= '^'),
    seq_test(actual=seqs.I,                      expected= 'i'),
    seq_test(actual=seqs.J,                      expected= 'j'),
    seq_test(actual=seqs.K,                      expected= 'k'),
    seq_test(actual=seqs.L,                      expected= 'l'),
    seq_test(actual=seqs.LEFT_BRACE,             expected= '{'),
    seq_test(actual=seqs.LEFT_SQUARE_BRACKET,    expected= '['),
    seq_test(actual=seqs.LEFT_PAREN,             expected= '('),
    seq_test(actual=seqs.LESS_THAN,              expected= '<lt>'),
    seq_test(actual=seqs.LESS_THAN_LESS_THAN,    expected= '<lt><lt>'),
    seq_test(actual=seqs.MINUS,                  expected= '-'),
    seq_test(actual=seqs.M,                      expected= 'm'),
    seq_test(actual=seqs.N,                      expected= 'n'),
    seq_test(actual=seqs.O,                      expected= 'o'),
    seq_test(actual=seqs.P,                      expected= 'p'),
    seq_test(actual=seqs.PLUS,                   expected= '+'),
    seq_test(actual=seqs.OCTOTHORP,              expected= '#'),
    seq_test(actual=seqs.PAGE_DOWN,              expected= 'pagedown'),
    seq_test(actual=seqs.PAGE_UP,                expected= 'pageup'),
    seq_test(actual=seqs.PERCENT,                expected= '%'),
    seq_test(actual=seqs.PIPE,                   expected= '|'),
    seq_test(actual=seqs.QUESTION_MARK,          expected= '?'),
    seq_test(actual=seqs.QUOTE,                  expected= "'"),
    seq_test(actual=seqs.QUOTE_QUOTE,            expected= "''"),
    seq_test(actual=seqs.R,                      expected= 'r'),
    seq_test(actual=seqs.RIGHT_BRACE,            expected= '}'),
    seq_test(actual=seqs.RIGHT_SQUARE_BRACKET,   expected= ']'),
    seq_test(actual=seqs.RIGHT_PAREN,            expected= ')'),
    seq_test(actual=seqs.S,                      expected= 's'),
    seq_test(actual=seqs.SEMICOLON,              expected= ';'),
    seq_test(actual=seqs.SHIFT_CTRL_F12,         expected= '<C-S-f12>'),
    seq_test(actual=seqs.SHIFT_F11,              expected='<S-f11>'),
    seq_test(actual=seqs.SLASH,                  expected= '/'),
    seq_test(actual=seqs.STAR,                   expected= '*'),
    seq_test(actual=seqs.T,                      expected= 't'),
    seq_test(actual=seqs.TAB,                    expected= '<tab>'),
    seq_test(actual=seqs.TILDE,                  expected='~'),
    seq_test(actual=seqs.U,                      expected='u'),
    seq_test(actual=seqs.UNDERSCORE,             expected='_'),
    seq_test(actual=seqs.V,                      expected='v'),
    seq_test(actual=seqs.W,                      expected='w'),
    seq_test(actual=seqs.X,                      expected='x'),
    seq_test(actual=seqs.Y,                      expected='y'),
    seq_test(actual=seqs.YY,                     expected='yy'),
    seq_test(actual=seqs.ZERO,                   expected='0'),
)


class Test_KeySequenceNames(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS_KNOWN_SEQUENCES):
            self.assertEqual(data.actual, data.expected,
                             "failed at index {0}".format(i))

    def testAllKeySequenceNamesAreTested(self):
        tested_seqs = [k.actual for k in TESTS_KNOWN_SEQUENCES]
        self.assertEqual(sorted(tested_seqs),
                         sorted([v for (k, v) in seqs.__dict__.items()
                                if k.isupper()]))
