import logging
import re

from Vintageous import local_logger
from Vintageous.vi import inputs
from Vintageous.vi import utils
from Vintageous.vi.cmd_defs import cmd_defs
from Vintageous.vi.cmd_defs import cmds
from Vintageous.vi.utils import input_types
from Vintageous.vi.utils import modes


_logger = local_logger(__name__)


class mapping_scopes:
    """
    Scopes for mappings.
    """
    DEFAULT =      0
    USER =         1
    PLUGIN =       2
    NAME_SPACE =   3
    LEADER =       4
    LOCAL_LEADER = 5


class seqs:
    """
    Vim's built-in key sequences plus Sublime Text 3 staple commands.

    These are the sequences of key presses known to Vintageous. Any other
    sequence pressed will be treated as 'unmapped'.
    """

    A =                            'a'
    ALT_CTRL_P =                   '<C-M-p>'
    AMPERSAND =                    '&'
    AW =                           'aw'
    B =                            'b'
    GE =                           'ge'
    UP =                           '<up>'
    DOWN =                         '<down>'
    LEFT =                         '<left>'
    RIGHT =                        '<right>'
    HOME =                         '<home>'
    END =                          '<end>'
    BACKTICK =                     '`'
    BIG_A =                        'A'
    SPACE =                        '<space>'
    BIG_B =                        'B'
    CTRL_E =                       '<C-e>'
    CTRL_Y =                       '<C-y>'
    BIG_C =                        'C'
    BIG_D =                        'D'
    GH =                           'gh'
    BIG_E =                        'E'
    BIG_F =                        'F'
    BIG_G =                        'G'
    CTRL_W =                       '<C-w>'
    CTRL_W_Q =                     '<C-w>q'

    CTRL_W_V =                     '<C-w>v'
    CTRL_W_L =                     '<C-w>l'
    CTRL_W_BIG_L =                 '<C-w>L'
    CTRL_K =                       '<C-k>'
    CTRL_K_CTRL_B =                '<C-k><C-b>'
    CTRL_BIG_F =                   '<C-F>'
    CTRL_BIG_P =                   '<C-P>'
    CTRL_W_H =                     '<C-w>h'
    Q =                            'q'
    AT =                           '@'
    CTRL_W_BIG_H =                 '<C-w>H'
    BIG_H =                        'H'

    BIG_J =                        'J'
    BIG_Z =                        'Z'
    G_BIG_J =                      'gJ'
    CTRL_R=                        '<C-r>'
    CTRL_R_EQUAL =                 '<C-r>='
    CTRL_A =                       '<C-a>'
    CTRL_X =                       '<C-x>'
    Z =                            'z'
    Z_ENTER =                      'z<cr>'
    ZT =                           'zt'
    ZZ =                           'zz'
    Z_MINUS =                      'z-'
    ZB =                           'zb'

    BIG_I =                        'I'
    BIG_Z_BIG_Z =                  'ZZ'
    BIG_Z_BIG_Q =                  'ZQ'
    GV =                           'gv'
    BIG_J =                        'J'
    BIG_K =                        'K'
    BIG_L =                        'L'
    BIG_M =                        'M'
    BIG_N =                        'N'
    BIG_O =                        'O'
    BIG_P =                        'P'
    BIG_Q =                        'Q'
    BIG_R =                        'R'
    BIG_S =                        'S'
    BIG_T =                        'T'
    BIG_U =                        'U'
    BIG_V =                        'V'
    BIG_W =                        'W'
    BIG_X =                        'X'
    BIG_Y =                        'Y'
    BIG_Z =                        'Z'
    C =                            'c'
    CC =                           'cc'
    COLON =                        ':'
    COMMA =                        ','
    CTRL_D =                       '<C-d>'
    CTRL_F12 =                     '<C-f12>'
    F11 =                          'f11'
    CTRL_l =                       '<C-l>'
    CTRL_B =                       '<C-b>'
    CTRL_F =                       '<C-f>'
    CTRL_G =                       '<C-g>'
    CTRL_P =                       '<C-p>'
    CTRL_U =                       '<C-u>'
    CTRL_V =                       '<C-v>'
    D =                            'd'
    DD =                           'dd'
    DOLLAR =                       '$'
    DOT =                          '.'
    DOUBLE_QUOTE =                 '"'
    E =                            'e'
    ENTER =                        '<cr>' # Or rather <Enter>?
    SHIFT_ENTER =                  '<S-cr>'
    EQUAL =                        '='
    EQUAL_EQUAL =                  '=='
    ESC =                          '<esc>'
    F =                            'f'
    F1 =                           '<f1>'
    F10 =                          '<f10>'
    F11 =                          '<f11>'
    F12 =                          '<f12>'
    F12 =                          '<f12>'
    F13 =                          '<f13>'
    F14 =                          '<f14>'
    F15 =                          '<f15>'
    F2 =                           '<f2>'
    F3 =                           '<f3>'
    SHIFT_F3 =                     '<S-f3>'
    SHIFT_F4 =                     '<S-f4>'
    F4 =                           '<f4>'
    F5 =                           '<f5>'
    F6 =                           '<f6>'
    F7 =                           '<f7>'
    F8 =                           '<f8>'
    F9 =                           '<f9>'
    G =                            'g'
    G_BIG_D =                      'gD'
    G_BIG_U =                      'gU'
    G_BIG_U_BIG_U =                'gUU'
    G_BIG_U_G_BIG_U =              'gUgU'
    G_TILDE =                      'g~'
    G_TILDE_G_TILDE =              'g~g~'
    G_TILDE_TILDE =                'g~~'
    G_UNDERSCORE =                 'g_'
    GD =                           'gd'
    GG =                           'gg'
    GJ =                           'gj'
    GK =                           'gk'
    GQ =                           'gq'
    GT =                           'gt'
    G_BIG_T =                      'gT'
    GU =                           'gu'
    GUGU =                         'gugu'
    GUU =                          'guu'
    GREATER_THAN =                 '>'
    GREATER_THAN_GREATER_THAN =    '>>'
    H =                            'h'
    HAT =                          '^'
    I =                            'i'
    J =                            'j'
    K =                            'k'
    L =                            'l'
    LEFT_BRACE =                   '{'
    LEFT_SQUARE_BRACKET =          '['
    LEFT_PAREN =                   '('
    LESS_THAN =                    '<lt>'
    LESS_THAN_LESS_THAN =          '<lt><lt>'
    M =                            'm'
    N =                            'n'
    O =                            'o'
    P =                            'p'
    OCTOTHORP =                    '#'
    PERCENT =                      '%'
    PIPE =                         '|'
    QUESTION_MARK =                '?'
    QUOTE =                        "'"
    QUOTE_QUOTE =                  "''"
    R =                            'r'
    RIGHT_BRACE =                  '}'
    RIGHT_SQUARE_BRACKET =         ']'
    RIGHT_PAREN =                  ')'
    S =                            's'
    SEMICOLON =                    ';'
    SHIFT_CTRL_F12 =               '<C-S-f12>'
    SLASH =                        '/'
    STAR =                         '*'
    T =                            't'
    TILDE =                        '~'
    U =                            'u'
    UNDERSCORE =                   '_'
    V =                            'v'
    W =                            'w'
    X =                            'x'
    Y =                            'y'
    YY =                           'yy'
    ZERO =                         '0'


def seq_to_command(state, seq, mode=None):
    """
    Returns the command definition mapped to @seq, or a 'missing' command
    if none is found.

    @mode
        Forces the use of this mode instead of the global state's.
    """
    mode = mode or state.mode

    _logger().info('[seq_to_command] state/seq: {0}/{1}'.format(mode, seq))

    if state.mode in mappings:
        command = mappings[mode].get(seq, mappings['_missing'])
        return command
    return mappings['_missing']


# Mappings 'key sequence' ==> 'command definition'
#
# 'key sequence' is a sequence of key presses.
#
mappings = {
    modes.NORMAL: {
        seqs.A:                         cmd_defs[modes.NORMAL][cmds.A],
        seqs.ALT_CTRL_P:                cmd_defs[modes.NORMAL][cmds.ALT_CTRL_P],
        seqs.AT:                        cmd_defs[modes.NORMAL][cmds.AT],
        seqs.B:                         cmd_defs[modes.NORMAL][cmds.B],
        seqs.BACKTICK:                  cmd_defs[modes.NORMAL][cmds.BACKTICK],
        seqs.BIG_A:                     cmd_defs[modes.NORMAL][cmds.BIG_A],
        seqs.BIG_B:                     cmd_defs[modes.NORMAL][cmds.BIG_B],
        seqs.BIG_B:                     cmd_defs[modes.NORMAL][cmds.BIG_B],
        seqs.BIG_C:                     cmd_defs[modes.NORMAL][cmds.BIG_C],
        seqs.BIG_D:                     cmd_defs[modes.NORMAL][cmds.BIG_D],
        seqs.BIG_E:                     cmd_defs[modes.NORMAL][cmds.BIG_E],
        seqs.BIG_F:                     cmd_defs[modes.NORMAL][cmds.BIG_F],
        seqs.BIG_G:                     cmd_defs[modes.NORMAL][cmds.BIG_G],
        seqs.BIG_H:                     cmd_defs[modes.NORMAL][cmds.BIG_H],
        seqs.BIG_I:                     cmd_defs[modes.NORMAL][cmds.BIG_I],
        seqs.BIG_J:                     cmd_defs[modes.NORMAL][cmds.BIG_J],
        seqs.BIG_J:                     cmd_defs[modes.NORMAL][cmds.BIG_J],
        seqs.BIG_L:                     cmd_defs[modes.NORMAL][cmds.BIG_L],
        seqs.BIG_M:                     cmd_defs[modes.NORMAL][cmds.BIG_M],
        seqs.BIG_N:                     cmd_defs[modes.NORMAL][cmds.BIG_N],
        seqs.BIG_O:                     cmd_defs[modes.NORMAL][cmds.BIG_O],
        seqs.BIG_P:                     cmd_defs[modes.NORMAL][cmds.BIG_P],
        seqs.BIG_R:                     cmd_defs[modes.NORMAL][cmds.BIG_R],
        seqs.BIG_S:                     cmd_defs[modes.NORMAL][cmds.BIG_S],
        seqs.BIG_T:                     cmd_defs[modes.NORMAL][cmds.BIG_T],
        seqs.BIG_V:                     cmd_defs[modes.NORMAL][cmds.BIG_V],
        seqs.BIG_W:                     cmd_defs[modes.NORMAL][cmds.BIG_W],
        seqs.BIG_X:                     cmd_defs[modes.NORMAL][cmds.BIG_X],
        seqs.BIG_Y:                     cmd_defs[modes.NORMAL][cmds.BIG_Y],
        seqs.BIG_Z:                     cmd_defs[modes.NORMAL][cmds.BIG_Z],
        seqs.BIG_Z:                     cmd_defs[modes.NORMAL][cmds.BIG_Z],
        seqs.BIG_Z_BIG_Q:               cmd_defs[modes.NORMAL][cmds.BIG_Z_BIG_Q],
        seqs.BIG_Z_BIG_Z:               cmd_defs[modes.NORMAL][cmds.BIG_Z_BIG_Z],
        seqs.C:                         cmd_defs[modes.NORMAL][cmds.C],
        seqs.CC:                        cmd_defs[modes.NORMAL][cmds.CC],
        seqs.COLON:                     cmd_defs[modes.NORMAL][cmds.COLON],
        seqs.COMMA:                     cmd_defs[modes.NORMAL][cmds.COMMA],
        seqs.CTRL_A:                    cmd_defs[modes.NORMAL][cmds.CTRL_A],
        seqs.CTRL_B:                    cmd_defs[modes.NORMAL][cmds.CTRL_B],
        seqs.CTRL_BIG_F:                cmd_defs[modes.NORMAL][cmds.CTRL_BIG_F],
        seqs.CTRL_BIG_P:                cmd_defs[modes.NORMAL][cmds.CTRL_BIG_P],
        seqs.CTRL_D:                    cmd_defs[modes.NORMAL][cmds.CTRL_D],
        seqs.CTRL_E:                    cmd_defs[modes.NORMAL][cmds.CTRL_E],
        seqs.CTRL_F12:                  cmd_defs[modes.NORMAL][cmds.CTRL_F12],
        seqs.CTRL_F:                    cmd_defs[modes.NORMAL][cmds.CTRL_F],
        seqs.CTRL_G:                    cmd_defs[modes.NORMAL][cmds.CTRL_G],
        seqs.CTRL_K:                    cmd_defs[modes.NORMAL][cmds.CTRL_K],
        seqs.CTRL_K_CTRL_B:             cmd_defs[modes.NORMAL][cmds.CTRL_K_CTRL_B],
        seqs.CTRL_P:                    cmd_defs[modes.NORMAL][cmds.CTRL_P],
        seqs.CTRL_R:                    cmd_defs[modes.NORMAL][cmds.CTRL_R],
        seqs.CTRL_R_EQUAL:              cmd_defs[modes.NORMAL][cmds.CTRL_R_EQUAL],
        seqs.CTRL_U:                    cmd_defs[modes.NORMAL][cmds.CTRL_U],
        seqs.CTRL_V:                    cmd_defs[modes.NORMAL][cmds.CTRL_V],
        seqs.CTRL_W:                    cmd_defs[modes.NORMAL][cmds.CTRL_W],
        seqs.CTRL_W_BIG_L:              cmd_defs[modes.NORMAL][cmds.CTRL_W_BIG_L],
        seqs.CTRL_W_H:                  cmd_defs[modes.NORMAL][cmds.CTRL_W_H],
        seqs.CTRL_W_L:                  cmd_defs[modes.NORMAL][cmds.CTRL_W_L],
        seqs.CTRL_W_Q:                  cmd_defs[modes.NORMAL][cmds.CTRL_W_Q],
        seqs.CTRL_W_V:                  cmd_defs[modes.NORMAL][cmds.CTRL_W_V],
        seqs.CTRL_X:                    cmd_defs[modes.NORMAL][cmds.CTRL_X],
        seqs.CTRL_Y:                    cmd_defs[modes.NORMAL][cmds.CTRL_Y],
        seqs.D:                         cmd_defs[modes.NORMAL][cmds.D],
        seqs.D:                         cmd_defs[modes.NORMAL][cmds.D],
        seqs.DD:                        cmd_defs[modes.NORMAL][cmds.DD],
        seqs.DOLLAR:                    cmd_defs[modes.NORMAL][cmds.DOLLAR],
        seqs.DOT:                       cmd_defs[modes.NORMAL][cmds.DOT],
        seqs.DOUBLE_QUOTE:              cmd_defs[modes.NORMAL][cmds.DOUBLE_QUOTE],
        seqs.DOWN:                      cmd_defs[modes.NORMAL][cmds.J],
        seqs.E:                         cmd_defs[modes.NORMAL][cmds.E],
        seqs.END:                       cmd_defs[modes.NORMAL][cmds.DOLLAR],
        seqs.ENTER:                     cmd_defs[modes.NORMAL][cmds.ENTER],
        seqs.EQUAL:                     cmd_defs[modes.NORMAL][cmds.EQUAL],
        seqs.EQUAL_EQUAL:               cmd_defs[modes.NORMAL][cmds.EQUAL_EQUAL],
        seqs.ESC:                       cmd_defs[modes.NORMAL][cmds.ESC],
        seqs.F11:                       cmd_defs[modes.NORMAL][cmds.F11],
        seqs.F12:                       cmd_defs[modes.NORMAL][cmds.F12],
        seqs.F3:                        cmd_defs[modes.NORMAL][cmds.F3],
        seqs.F4:                        cmd_defs[modes.NORMAL][cmds.F4],
        seqs.F7:                        cmd_defs[modes.NORMAL][cmds.F7],
        seqs.F:                         cmd_defs[modes.NORMAL][cmds.F],
        seqs.G:                         cmd_defs[modes.NORMAL][cmds.G],
        seqs.G_BIG_D:                   cmd_defs[modes.NORMAL][cmds.G_BIG_D],
        seqs.G_BIG_J:                   cmd_defs[modes.NORMAL][cmds.G_BIG_J],
        seqs.G_BIG_T:                   cmd_defs[modes.NORMAL][cmds.G_BIG_T],
        seqs.G_BIG_U:                   cmd_defs[modes.NORMAL][cmds.G_BIG_U],
        seqs.G_BIG_U_BIG_U:             cmd_defs[modes.NORMAL][cmds.G_BIG_U_BIG_U],
        seqs.G_BIG_U_G_BIG_U:           cmd_defs[modes.NORMAL][cmds.G_BIG_U_G_BIG_U],
        seqs.G_TILDE:                   cmd_defs[modes.NORMAL][cmds.G_TILDE],
        seqs.G_TILDE_G_TILDE:           cmd_defs[modes.NORMAL][cmds.G_TILDE_G_TILDE],
        seqs.G_TILDE_TILDE:             cmd_defs[modes.NORMAL][cmds.G_TILDE_TILDE],
        seqs.G_UNDERSCORE:              cmd_defs[modes.NORMAL][cmds.G_UNDERSCORE],
        seqs.GD:                        cmd_defs[modes.NORMAL][cmds.GD],
        seqs.GE:                        cmd_defs[modes.NORMAL][cmds.GE],
        seqs.GG:                        cmd_defs[modes.NORMAL][cmds.GG],
        seqs.GH:                        cmd_defs[modes.NORMAL][cmds.GH],
        seqs.GJ:                        cmd_defs[modes.NORMAL][cmds.GJ],
        seqs.GK:                        cmd_defs[modes.NORMAL][cmds.GK],
        seqs.GQ:                        cmd_defs[modes.NORMAL][cmds.GQ],
        seqs.GREATER_THAN:              cmd_defs[modes.NORMAL][cmds.GREATER_THAN],
        seqs.GREATER_THAN_GREATER_THAN: cmd_defs[modes.NORMAL][cmds.GREATER_THAN_GREATER_THAN],
        seqs.GT:                        cmd_defs[modes.NORMAL][cmds.GT],
        seqs.GU:                        cmd_defs[modes.NORMAL][cmds.GU],
        seqs.GUGU:                      cmd_defs[modes.NORMAL][cmds.GUGU],
        seqs.GUU:                       cmd_defs[modes.NORMAL][cmds.GUU],
        seqs.GV:                        cmd_defs[modes.NORMAL][cmds.GV],
        seqs.H:                         cmd_defs[modes.NORMAL][cmds.H],
        seqs.HAT:                       cmd_defs[modes.NORMAL][cmds.HAT],
        seqs.HOME:                      cmd_defs[modes.NORMAL][cmds.ZERO],
        seqs.I:                         cmd_defs[modes.NORMAL][cmds.I],
        seqs.J:                         cmd_defs[modes.NORMAL][cmds.J],
        seqs.K:                         cmd_defs[modes.NORMAL][cmds.K],
        seqs.L:                         cmd_defs[modes.NORMAL][cmds.L],
        seqs.LEFT:                      cmd_defs[modes.NORMAL][cmds.H],
        seqs.LEFT_BRACE:                cmd_defs[modes.NORMAL][cmds.LEFT_BRACE],
        seqs.LEFT_PAREN:                cmd_defs[modes.NORMAL][cmds.LEFT_PAREN],
        seqs.LEFT_SQUARE_BRACKET:       cmd_defs[modes.NORMAL][cmds.LEFT_SQUARE_BRACKET],
        seqs.LESS_THAN:                 cmd_defs[modes.NORMAL][cmds.LESS_THAN],
        seqs.LESS_THAN:                 cmd_defs[modes.NORMAL][cmds.LESS_THAN],
        seqs.LESS_THAN_LESS_THAN:       cmd_defs[modes.NORMAL][cmds.LESS_THAN_LESS_THAN],
        seqs.M:                         cmd_defs[modes.NORMAL][cmds.M],
        seqs.N:                         cmd_defs[modes.NORMAL][cmds.N],
        seqs.O:                         cmd_defs[modes.NORMAL][cmds.O],
        seqs.OCTOTHORP:                 cmd_defs[modes.NORMAL][cmds.OCTOTHORP],
        seqs.P:                         cmd_defs[modes.NORMAL][cmds.P],
        seqs.PERCENT:                   cmd_defs[modes.NORMAL][cmds.PERCENT],
        seqs.PIPE:                      cmd_defs[modes.NORMAL][cmds.PIPE],
        seqs.Q:                         cmd_defs[modes.NORMAL][cmds.Q],
        seqs.QUESTION_MARK:             cmd_defs[modes.NORMAL][cmds.QUESTION_MARK],
        seqs.QUOTE:                     cmd_defs[modes.NORMAL][cmds.QUOTE],
        seqs.QUOTE_QUOTE:               cmd_defs[modes.NORMAL][cmds.QUOTE_QUOTE],
        seqs.R:                         cmd_defs[modes.NORMAL][cmds.R],
        seqs.RIGHT:                     cmd_defs[modes.NORMAL][cmds.L],
        seqs.RIGHT_BRACE:               cmd_defs[modes.NORMAL][cmds.RIGHT_BRACE],
        seqs.RIGHT_PAREN:               cmd_defs[modes.NORMAL][cmds.RIGHT_PAREN],
        seqs.RIGHT_SQUARE_BRACKET:      cmd_defs[modes.NORMAL][cmds.RIGHT_SQUARE_BRACKET],
        seqs.S:                         cmd_defs[modes.NORMAL][cmds.S],
        seqs.S:                         cmd_defs[modes.NORMAL][cmds.S],
        seqs.SEMICOLON:                 cmd_defs[modes.NORMAL][cmds.SEMICOLON],
        seqs.SHIFT_CTRL_F12:            cmd_defs[modes.NORMAL][cmds.SHIFT_CTRL_F12],
        seqs.SHIFT_ENTER:               cmd_defs[modes.NORMAL][cmds.SHIFT_ENTER],
        seqs.SHIFT_F3:                  cmd_defs[modes.NORMAL][cmds.SHIFT_F3],
        seqs.SHIFT_F4:                  cmd_defs[modes.NORMAL][cmds.SHIFT_F4],
        seqs.SLASH:                     cmd_defs[modes.NORMAL][cmds.SLASH],
        seqs.SPACE:                     cmd_defs[modes.NORMAL][cmds.SPACE],
        seqs.STAR:                      cmd_defs[modes.NORMAL][cmds.STAR],
        seqs.T:                         cmd_defs[modes.NORMAL][cmds.T],
        seqs.TILDE:                     cmd_defs[modes.NORMAL][cmds.TILDE],
        seqs.U:                         cmd_defs[modes.NORMAL][cmds.U],
        seqs.UNDERSCORE:                cmd_defs[modes.NORMAL][cmds.UNDERSCORE],
        seqs.UP:                        cmd_defs[modes.NORMAL][cmds.K],
        seqs.V:                         cmd_defs[modes.NORMAL][cmds.V],
        seqs.W:                         cmd_defs[modes.NORMAL][cmds.W],
        seqs.X:                         cmd_defs[modes.NORMAL][cmds.X],
        seqs.X:                         cmd_defs[modes.NORMAL][cmds.X],
        seqs.Y:                         cmd_defs[modes.NORMAL][cmds.Y],
        seqs.Y:                         cmd_defs[modes.NORMAL][cmds.Y],
        seqs.YY:                        cmd_defs[modes.NORMAL][cmds.YY],
        seqs.Z:                         cmd_defs[modes.NORMAL][cmds.Z],
        seqs.Z_ENTER:                   cmd_defs[modes.NORMAL][cmds.Z_ENTER],
        seqs.Z_MINUS:                   cmd_defs[modes.NORMAL][cmds.Z_MINUS],
        seqs.ZB:                        cmd_defs[modes.NORMAL][cmds.ZB],
        seqs.ZERO:                      cmd_defs[modes.NORMAL][cmds.ZERO],
        seqs.ZT:                        cmd_defs[modes.NORMAL][cmds.ZT],
        seqs.ZZ:                        cmd_defs[modes.NORMAL][cmds.ZZ],
        seqs.ZZ:                        cmd_defs[modes.NORMAL][cmds.ZZ],
    },

    # Visual Mode ============================================================
    # XXX: We probably don't need to define all of these; select those that
    #      are actually legal visual mode key sequences.

    modes.VISUAL: {
        seqs.B:                     cmd_defs[modes.VISUAL][cmds.B],
        seqs.BACKTICK:              cmd_defs[modes.VISUAL][cmds.BACKTICK],
        seqs.BIG_B:                 cmd_defs[modes.VISUAL][cmds.BIG_B],
        seqs.BIG_C:                 cmd_defs[modes.VISUAL][cmds.BIG_C],
        seqs.BIG_D:                 cmd_defs[modes.VISUAL][cmds.BIG_D],
        seqs.BIG_E:                 cmd_defs[modes.VISUAL][cmds.BIG_E],
        seqs.BIG_F:                 cmd_defs[modes.VISUAL][cmds.BIG_F],
        seqs.BIG_G:                 cmd_defs[modes.VISUAL][cmds.BIG_G],
        seqs.BIG_H:                 cmd_defs[modes.VISUAL][cmds.BIG_H],
        seqs.BIG_J:                 cmd_defs[modes.VISUAL][cmds.BIG_J],
        seqs.BIG_L:                 cmd_defs[modes.VISUAL][cmds.BIG_L],
        seqs.BIG_M:                 cmd_defs[modes.VISUAL][cmds.BIG_M],
        seqs.BIG_N:                 cmd_defs[modes.VISUAL][cmds.BIG_N],
        seqs.BIG_O:                 cmd_defs[modes.VISUAL][cmds.BIG_O],
        seqs.BIG_P:                 cmd_defs[modes.VISUAL][cmds.BIG_P],
        seqs.BIG_T:                 cmd_defs[modes.VISUAL][cmds.BIG_T],
        seqs.BIG_U:                 cmd_defs[modes.VISUAL][cmds.BIG_U],
        seqs.BIG_V:                 cmd_defs[modes.VISUAL][cmds.BIG_V],
        seqs.BIG_W:                 cmd_defs[modes.VISUAL][cmds.BIG_W],
        seqs.BIG_X:                 cmd_defs[modes.VISUAL][cmds.BIG_X],
        seqs.BIG_Y:                 cmd_defs[modes.VISUAL][cmds.BIG_Y],
        seqs.C:                     cmd_defs[modes.VISUAL][cmds.C],
        seqs.COLON:                 cmd_defs[modes.VISUAL][cmds.COLON],
        seqs.COMMA:                 cmd_defs[modes.VISUAL][cmds.COMMA],
        seqs.CTRL_D:                cmd_defs[modes.VISUAL][cmds.CTRL_D],
        seqs.CTRL_E:                cmd_defs[modes.VISUAL][cmds.CTRL_E],
        seqs.CTRL_K:                cmd_defs[modes.VISUAL][cmds.CTRL_K],
        seqs.CTRL_K_CTRL_B:         cmd_defs[modes.NORMAL][cmds.CTRL_K_CTRL_B],
        seqs.CTRL_P:                cmd_defs[modes.VISUAL][cmds.CTRL_P],
        seqs.CTRL_U:                cmd_defs[modes.VISUAL][cmds.CTRL_U],
        seqs.CTRL_W:                cmd_defs[modes.VISUAL][cmds.CTRL_W],
        seqs.CTRL_W_BIG_H:          cmd_defs[modes.VISUAL][cmds.CTRL_W_BIG_H],
        seqs.CTRL_W_BIG_L:          cmd_defs[modes.VISUAL][cmds.CTRL_W_BIG_L],
        seqs.CTRL_W_H:              cmd_defs[modes.VISUAL][cmds.CTRL_W_H],
        seqs.CTRL_W_L:              cmd_defs[modes.VISUAL][cmds.CTRL_W_L],
        seqs.CTRL_W_Q:              cmd_defs[modes.VISUAL][cmds.CTRL_W_Q],
        seqs.CTRL_W_V:              cmd_defs[modes.VISUAL][cmds.CTRL_W_V],
        seqs.CTRL_X:                cmd_defs[modes.VISUAL][cmds.CTRL_X],
        seqs.CTRL_Y:                cmd_defs[modes.VISUAL][cmds.CTRL_Y],
        seqs.D:                     cmd_defs[modes.VISUAL][cmds.D],
        seqs.DOLLAR:                cmd_defs[modes.VISUAL][cmds.DOLLAR],
        seqs.DOT:                   cmd_defs[modes.VISUAL][cmds.DOT],
        seqs.DOUBLE_QUOTE:          cmd_defs[modes.VISUAL][cmds.DOUBLE_QUOTE],
        seqs.DOWN:                  cmd_defs[modes.VISUAL][cmds.J],
        seqs.E:                     cmd_defs[modes.VISUAL][cmds.E],
        seqs.END:                   cmd_defs[modes.VISUAL][cmds.DOLLAR],
        seqs.ENTER:                 cmd_defs[modes.VISUAL][cmds.ENTER],
        seqs.EQUAL:                 cmd_defs[modes.VISUAL][cmds.EQUAL],
        seqs.ESC:                   cmd_defs[modes.VISUAL][cmds.ESC],
        seqs.F11:                   cmd_defs[modes.VISUAL][cmds.F11],
        seqs.F12:                   cmd_defs[modes.VISUAL][cmds.F12],
        seqs.F7:                    cmd_defs[modes.VISUAL][cmds.F7],
        seqs.F:                     cmd_defs[modes.VISUAL][cmds.F],
        seqs.G:                     cmd_defs[modes.VISUAL][cmds.G],
        seqs.G_BIG_J:               cmd_defs[modes.VISUAL][cmds.G_BIG_J],
        seqs.G_BIG_U:               cmd_defs[modes.VISUAL][cmds.G_BIG_U],
        seqs.G_TILDE:               cmd_defs[modes.VISUAL][cmds.G_TILDE],
        seqs.G_UNDERSCORE:          cmd_defs[modes.VISUAL][cmds.G_UNDERSCORE],
        seqs.GD:                    cmd_defs[modes.VISUAL][cmds.GD],
        seqs.GE:                    cmd_defs[modes.VISUAL][cmds.GE],
        seqs.GG:                    cmd_defs[modes.VISUAL][cmds.GG],
        seqs.GH:                    cmd_defs[modes.VISUAL][cmds.GH],
        seqs.GJ:                    cmd_defs[modes.VISUAL][cmds.GJ],
        seqs.GK:                    cmd_defs[modes.VISUAL][cmds.GK],
        seqs.GQ:                    cmd_defs[modes.VISUAL][cmds.GQ],
        seqs.GREATER_THAN:          cmd_defs[modes.VISUAL][cmds.GREATER_THAN],
        seqs.GU:                    cmd_defs[modes.VISUAL][cmds.GU],
        seqs.GV:                    cmd_defs[modes.VISUAL][cmds.GV],
        seqs.H:                     cmd_defs[modes.VISUAL][cmds.H],
        seqs.HAT:                   cmd_defs[modes.VISUAL][cmds.HAT],
        seqs.HOME:                  cmd_defs[modes.VISUAL][cmds.ZERO],
        seqs.I:                     cmd_defs[modes.VISUAL][cmds.I],
        seqs.J:                     cmd_defs[modes.VISUAL][cmds.J],
        seqs.K:                     cmd_defs[modes.VISUAL][cmds.K],
        seqs.L:                     cmd_defs[modes.VISUAL][cmds.L],
        seqs.LEFT:                  cmd_defs[modes.VISUAL][cmds.H],
        seqs.LEFT_BRACE:            cmd_defs[modes.VISUAL][cmds.LEFT_BRACE],
        seqs.LEFT_PAREN:            cmd_defs[modes.VISUAL][cmds.LEFT_PAREN],
        seqs.LEFT_SQUARE_BRACKET:   cmd_defs[modes.VISUAL][cmds.LEFT_SQUARE_BRACKET],
        seqs.LESS_THAN:             cmd_defs[modes.VISUAL][cmds.LESS_THAN],
        seqs.N:                     cmd_defs[modes.VISUAL][cmds.N],
        seqs.O:                     cmd_defs[modes.VISUAL][cmds.O],
        seqs.OCTOTHORP:             cmd_defs[modes.VISUAL][cmds.OCTOTHORP],
        seqs.P:                     cmd_defs[modes.VISUAL][cmds.P],
        seqs.PERCENT:               cmd_defs[modes.VISUAL][cmds.PERCENT],
        seqs.PIPE:                  cmd_defs[modes.VISUAL][cmds.PIPE],
        seqs.QUESTION_MARK:         cmd_defs[modes.VISUAL][cmds.QUESTION_MARK],
        seqs.QUOTE:                 cmd_defs[modes.VISUAL][cmds.QUOTE],
        seqs.R:                     cmd_defs[modes.VISUAL][cmds.R],
        seqs.RIGHT:                 cmd_defs[modes.VISUAL][cmds.L],
        seqs.RIGHT_BRACE:           cmd_defs[modes.VISUAL][cmds.RIGHT_BRACE],
        seqs.RIGHT_SQUARE_BRACKET:  cmd_defs[modes.VISUAL][cmds.RIGHT_SQUARE_BRACKET],
        seqs.S:                     cmd_defs[modes.VISUAL][cmds.S],
        seqs.SEMICOLON:             cmd_defs[modes.VISUAL][cmds.SEMICOLON],
        seqs.SHIFT_CTRL_F12:        cmd_defs[modes.VISUAL][cmds.SHIFT_CTRL_F12],
        seqs.SHIFT_ENTER:           cmd_defs[modes.VISUAL][cmds.SHIFT_ENTER],
        seqs.SLASH:                 cmd_defs[modes.VISUAL][cmds.SLASH],
        seqs.STAR:                  cmd_defs[modes.VISUAL][cmds.STAR],
        seqs.T:                     cmd_defs[modes.VISUAL][cmds.T],
        seqs.TILDE:                 cmd_defs[modes.NORMAL][cmds.TILDE],
        seqs.U:                     cmd_defs[modes.VISUAL][cmds.U],
        seqs.UNDERSCORE:            cmd_defs[modes.VISUAL][cmds.UNDERSCORE],
        seqs.UP:                    cmd_defs[modes.VISUAL][cmds.K],
        seqs.V:                     cmd_defs[modes.VISUAL][cmds.V],
        seqs.W:                     cmd_defs[modes.VISUAL][cmds.W],
        seqs.X:                     cmd_defs[modes.VISUAL][cmds.X],
        seqs.Y:                     cmd_defs[modes.VISUAL][cmds.Y],
        seqs.Z:                     cmd_defs[modes.VISUAL][cmds.Z],
        seqs.Z_ENTER:               cmd_defs[modes.VISUAL][cmds.Z_ENTER],
        seqs.Z_MINUS:               cmd_defs[modes.VISUAL][cmds.Z_MINUS],
        seqs.ZB:                    cmd_defs[modes.VISUAL][cmds.ZB],
        seqs.ZERO:                  cmd_defs[modes.VISUAL][cmds.ZERO],
        seqs.ZT:                    cmd_defs[modes.VISUAL][cmds.ZT],
        seqs.ZZ:                    cmd_defs[modes.VISUAL][cmds.ZZ],
    },

    modes.OPERATOR_PENDING: {
        seqs.A:                 cmd_defs[modes.OPERATOR_PENDING][cmds.A],
        seqs.B:                 cmd_defs[modes.OPERATOR_PENDING][cmds.B],
        seqs.BACKTICK:          cmd_defs[modes.OPERATOR_PENDING][cmds.BACKTICK],
        seqs.BIG_B:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_B],
        seqs.BIG_E:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_E],
        seqs.BIG_F:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_F],
        seqs.BIG_G:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_G],
        seqs.BIG_H:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_H],
        seqs.BIG_L:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_L],
        seqs.BIG_M:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_M],
        seqs.BIG_N:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_N],
        seqs.BIG_T:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_T],
        seqs.BIG_W:             cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_W],
        seqs.COLON:             cmd_defs[modes.OPERATOR_PENDING][cmds.COLON],
        seqs.COMMA:             cmd_defs[modes.OPERATOR_PENDING][cmds.COMMA],
        seqs.CTRL_B:            cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_B],
        seqs.CTRL_D:            cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_D],
        seqs.CTRL_E:            cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_E],
        seqs.CTRL_F:            cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_F],
        seqs.CTRL_U:            cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_U],
        seqs.CTRL_Y:            cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_Y],
        seqs.DOLLAR:            cmd_defs[modes.OPERATOR_PENDING][cmds.DOLLAR],
        seqs.DOWN:              cmd_defs[modes.OPERATOR_PENDING][cmds.J],
        seqs.E:                 cmd_defs[modes.OPERATOR_PENDING][cmds.E],
        seqs.END:               cmd_defs[modes.OPERATOR_PENDING][cmds.DOLLAR],
        seqs.ENTER:             cmd_defs[modes.OPERATOR_PENDING][cmds.ENTER],
        seqs.F:                 cmd_defs[modes.OPERATOR_PENDING][cmds.F],
        seqs.G:                 cmd_defs[modes.OPERATOR_PENDING][cmds.G],
        seqs.G_UNDERSCORE:      cmd_defs[modes.OPERATOR_PENDING][cmds.G_UNDERSCORE],
        seqs.GD:                cmd_defs[modes.OPERATOR_PENDING][cmds.GD],
        seqs.GE:                cmd_defs[modes.OPERATOR_PENDING][cmds.GE],
        seqs.GG:                cmd_defs[modes.OPERATOR_PENDING][cmds.GG],
        seqs.GJ:                cmd_defs[modes.OPERATOR_PENDING][cmds.GJ],
        seqs.GK:                cmd_defs[modes.OPERATOR_PENDING][cmds.GK],
        seqs.H:                 cmd_defs[modes.OPERATOR_PENDING][cmds.H],
        seqs.I:                 cmd_defs[modes.OPERATOR_PENDING][cmds.I],
        seqs.HAT:               cmd_defs[modes.OPERATOR_PENDING][cmds.HAT],
        seqs.HOME:              cmd_defs[modes.OPERATOR_PENDING][cmds.ZERO],
        seqs.J:                 cmd_defs[modes.OPERATOR_PENDING][cmds.J],
        seqs.K:                 cmd_defs[modes.OPERATOR_PENDING][cmds.K],
        seqs.L:                 cmd_defs[modes.OPERATOR_PENDING][cmds.L],
        seqs.LEFT:              cmd_defs[modes.OPERATOR_PENDING][cmds.H],
        seqs.LEFT_BRACE:        cmd_defs[modes.OPERATOR_PENDING][cmds.LEFT_BRACE],
        seqs.LEFT_PAREN:        cmd_defs[modes.OPERATOR_PENDING][cmds.LEFT_PAREN],
        seqs.N:                 cmd_defs[modes.OPERATOR_PENDING][cmds.N],
        seqs.OCTOTHORP:         cmd_defs[modes.OPERATOR_PENDING][cmds.OCTOTHORP],
        seqs.PERCENT:           cmd_defs[modes.OPERATOR_PENDING][cmds.PERCENT],
        seqs.PIPE:              cmd_defs[modes.OPERATOR_PENDING][cmds.PIPE],
        seqs.QUESTION_MARK:     cmd_defs[modes.OPERATOR_PENDING][cmds.QUESTION_MARK],
        seqs.QUOTE:             cmd_defs[modes.OPERATOR_PENDING][cmds.QUOTE],
        seqs.RIGHT:             cmd_defs[modes.OPERATOR_PENDING][cmds.L],
        seqs.RIGHT_BRACE:       cmd_defs[modes.OPERATOR_PENDING][cmds.RIGHT_BRACE],
        seqs.RIGHT_PAREN:       cmd_defs[modes.OPERATOR_PENDING][cmds.RIGHT_PAREN],
        seqs.SEMICOLON:         cmd_defs[modes.OPERATOR_PENDING][cmds.SEMICOLON],
        seqs.SHIFT_ENTER:       cmd_defs[modes.OPERATOR_PENDING][cmds.SHIFT_ENTER],
        seqs.SLASH:             cmd_defs[modes.OPERATOR_PENDING][cmds.SLASH],
        seqs.SPACE:             cmd_defs[modes.OPERATOR_PENDING][cmds.SPACE],
        seqs.STAR:              cmd_defs[modes.OPERATOR_PENDING][cmds.STAR],
        seqs.T:                 cmd_defs[modes.OPERATOR_PENDING][cmds.T],
        seqs.UNDERSCORE:        cmd_defs[modes.OPERATOR_PENDING][cmds.UNDERSCORE],
        seqs.UP:                cmd_defs[modes.OPERATOR_PENDING][cmds.K],
        seqs.W:                 cmd_defs[modes.OPERATOR_PENDING][cmds.W],
        seqs.ZERO:              cmd_defs[modes.OPERATOR_PENDING][cmds.ZERO],
    },

    # Visual Line Mode =======================================================

    modes.VISUAL_LINE: {
        seqs.A:                         cmd_defs[modes.VISUAL_LINE][cmds.A],
        seqs.ALT_CTRL_P:                cmd_defs[modes.VISUAL_LINE][cmds.ALT_CTRL_P],
        seqs.B:                         cmd_defs[modes.VISUAL_LINE][cmds.B],
        seqs.BACKTICK:                  cmd_defs[modes.VISUAL_LINE][cmds.BACKTICK],
        seqs.DOWN:                      cmd_defs[modes.VISUAL_LINE][cmds.J],
        seqs.END:                       cmd_defs[modes.VISUAL_LINE][cmds.BIG_G],
        seqs.HOME:                      cmd_defs[modes.VISUAL_LINE][cmds.GG],
        seqs.LEFT:                      cmd_defs[modes.VISUAL_LINE][cmds.H],
        seqs.RIGHT:                     cmd_defs[modes.VISUAL_LINE][cmds.L],
        seqs.UP:                        cmd_defs[modes.VISUAL_LINE][cmds.K],
        seqs.BIG_A:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_A],
        seqs.BIG_B:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_B],
        seqs.BIG_B:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_B],
        seqs.BIG_C:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_C],
        seqs.BIG_D:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_D],
        seqs.BIG_E:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_E],
        seqs.BIG_F:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_F],
        seqs.BIG_G:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_G],
        seqs.BIG_H:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_H],
        seqs.BIG_I:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_I],
        seqs.BIG_J:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_J],
        seqs.BIG_L:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_L],
        seqs.BIG_M:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_M],
        seqs.BIG_N:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_N],
        seqs.BIG_O:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_O],
        seqs.BIG_P:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_P],
        seqs.BIG_R:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_R],
        seqs.BIG_S:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_S],
        seqs.BIG_T:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_T],
        seqs.BIG_U:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_U],
        seqs.BIG_V:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_V],
        seqs.BIG_W:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_W],
        seqs.BIG_X:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_X],
        seqs.BIG_Y:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_Y],
        seqs.BIG_Z:                     cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_Z],
        seqs.BIG_Z:                     cmd_defs[modes.VISUAL_LINE][cmds.BIG_Z],
        seqs.BIG_Z_BIG_Q:               cmd_defs[modes.VISUAL_LINE][cmds.BIG_Z_BIG_Q],
        seqs.BIG_Z_BIG_Z:               cmd_defs[modes.VISUAL_LINE][cmds.BIG_Z_BIG_Z],
        seqs.C:                         cmd_defs[modes.VISUAL_LINE][cmds.C],
        seqs.CC:                        cmd_defs[modes.VISUAL_LINE][cmds.CC],
        seqs.COLON:                     cmd_defs[modes.VISUAL_LINE][cmds.COLON],
        seqs.COMMA:                     cmd_defs[modes.VISUAL_LINE][cmds.COMMA],
        seqs.CTRL_A:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_A],
        seqs.CTRL_B:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_B],
        seqs.CTRL_BIG_P:                cmd_defs[modes.VISUAL_LINE][cmds.CTRL_BIG_P],
        seqs.CTRL_D:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_D],
        seqs.CTRL_E:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_E],
        seqs.CTRL_F12:                  cmd_defs[modes.VISUAL_LINE][cmds.CTRL_F12],
        seqs.CTRL_F:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_F],
        seqs.CTRL_K_CTRL_B:             cmd_defs[modes.VISUAL_LINE][cmds.CTRL_K_CTRL_B],
        seqs.CTRL_P:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_P],
        seqs.CTRL_R:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_R],
        seqs.CTRL_R_EQUAL:              cmd_defs[modes.VISUAL_LINE][cmds.CTRL_R_EQUAL],
        seqs.CTRL_U:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_U],
        seqs.CTRL_W:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W],
        seqs.CTRL_W_BIG_L:              cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_BIG_L],
        seqs.CTRL_W_H:                  cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_H],
        seqs.CTRL_W_L:                  cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_L],
        seqs.CTRL_W_Q:                  cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_Q],
        seqs.CTRL_W_V:                  cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_V],
        seqs.CTRL_X:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_X],
        seqs.CTRL_Y:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_Y],
        seqs.D:                         cmd_defs[modes.VISUAL_LINE][cmds.D],
        seqs.D:                         cmd_defs[modes.VISUAL_LINE][cmds.D],
        seqs.DD:                        cmd_defs[modes.VISUAL_LINE][cmds.DD],
        seqs.DOLLAR:                    cmd_defs[modes.VISUAL_LINE][cmds.DOLLAR],
        seqs.CTRL_V:                    cmd_defs[modes.VISUAL_LINE][cmds.CTRL_V],
        seqs.DOT:                       cmd_defs[modes.VISUAL_LINE][cmds.DOT],
        seqs.DOUBLE_QUOTE:              cmd_defs[modes.VISUAL_LINE][cmds.DOUBLE_QUOTE],
        seqs.E:                         cmd_defs[modes.VISUAL_LINE][cmds.E],
        seqs.ENTER:                     cmd_defs[modes.VISUAL_LINE][cmds.ENTER],
        seqs.EQUAL:                     cmd_defs[modes.VISUAL_LINE][cmds.EQUAL],
        seqs.ESC:                       cmd_defs[modes.VISUAL_LINE][cmds.ESC],
        seqs.F11:                       cmd_defs[modes.VISUAL_LINE][cmds.F11],
        seqs.F12:                       cmd_defs[modes.VISUAL_LINE][cmds.F12],
        seqs.F7:                        cmd_defs[modes.VISUAL_LINE][cmds.F7],
        seqs.F:                         cmd_defs[modes.VISUAL_LINE][cmds.F],
        seqs.G:                         cmd_defs[modes.VISUAL_LINE][cmds.G],
        seqs.G_BIG_J:                   cmd_defs[modes.VISUAL_LINE][cmds.G_BIG_J],
        seqs.G_BIG_T:                   cmd_defs[modes.VISUAL_LINE][cmds.G_BIG_T],
        seqs.G_BIG_U:                   cmd_defs[modes.VISUAL_LINE][cmds.G_BIG_U],
        seqs.G_TILDE:                   cmd_defs[modes.VISUAL_LINE][cmds.G_TILDE],
        seqs.G_TILDE_G_TILDE:           cmd_defs[modes.VISUAL_LINE][cmds.G_TILDE_G_TILDE],
        seqs.G_UNDERSCORE:              cmd_defs[modes.VISUAL_LINE][cmds.G_UNDERSCORE],
        seqs.GD:                        cmd_defs[modes.VISUAL_LINE][cmds.GD],
        seqs.GE:                        cmd_defs[modes.VISUAL_LINE][cmds.GE],
        seqs.GG:                        cmd_defs[modes.VISUAL_LINE][cmds.GG],
        seqs.GJ:                        cmd_defs[modes.VISUAL_LINE][cmds.GJ],
        seqs.GK:                        cmd_defs[modes.VISUAL_LINE][cmds.GK],
        seqs.GQ:                        cmd_defs[modes.VISUAL_LINE][cmds.GQ],
        seqs.GREATER_THAN:              cmd_defs[modes.VISUAL_LINE][cmds.GREATER_THAN],
        seqs.GT:                        cmd_defs[modes.VISUAL_LINE][cmds.GT],
        seqs.GU:                        cmd_defs[modes.VISUAL_LINE][cmds.GU],
        seqs.GV:                        cmd_defs[modes.VISUAL_LINE][cmds.GV],
        seqs.H:                         cmd_defs[modes.VISUAL_LINE][cmds.H],
        seqs.HAT:                       cmd_defs[modes.VISUAL_LINE][cmds.HAT],
        seqs.I:                         cmd_defs[modes.VISUAL_LINE][cmds.I],
        seqs.J:                         cmd_defs[modes.VISUAL_LINE][cmds.J],
        seqs.K:                         cmd_defs[modes.VISUAL_LINE][cmds.K],
        seqs.L:                         cmd_defs[modes.VISUAL_LINE][cmds.L],
        seqs.LEFT_BRACE:                cmd_defs[modes.VISUAL_LINE][cmds.LEFT_BRACE],
        seqs.LEFT_PAREN:                cmd_defs[modes.VISUAL_LINE][cmds.LEFT_PAREN],
        seqs.LESS_THAN:                 cmd_defs[modes.VISUAL_LINE][cmds.LESS_THAN],
        seqs.M:                         cmd_defs[modes.VISUAL_LINE][cmds.M],
        seqs.N:                         cmd_defs[modes.VISUAL_LINE][cmds.N],
        seqs.O:                         cmd_defs[modes.VISUAL_LINE][cmds.O],
        seqs.OCTOTHORP:                 cmd_defs[modes.VISUAL_LINE][cmds.OCTOTHORP],
        seqs.P:                         cmd_defs[modes.VISUAL_LINE][cmds.P],
        seqs.PERCENT:                   cmd_defs[modes.VISUAL_LINE][cmds.PERCENT],
        seqs.PIPE:                      cmd_defs[modes.VISUAL_LINE][cmds.PIPE],
        seqs.QUESTION_MARK:             cmd_defs[modes.VISUAL_LINE][cmds.QUESTION_MARK],
        seqs.QUOTE:                     cmd_defs[modes.VISUAL_LINE][cmds.QUOTE],
        seqs.QUOTE_QUOTE:               cmd_defs[modes.VISUAL_LINE][cmds.QUOTE_QUOTE],
        seqs.R:                         cmd_defs[modes.VISUAL_LINE][cmds.R],
        seqs.RIGHT_BRACE:               cmd_defs[modes.VISUAL_LINE][cmds.RIGHT_BRACE],
        seqs.RIGHT_PAREN:               cmd_defs[modes.VISUAL_LINE][cmds.RIGHT_PAREN],
        seqs.S:                         cmd_defs[modes.VISUAL_LINE][cmds.S],
        seqs.S:                         cmd_defs[modes.VISUAL_LINE][cmds.S],
        seqs.SEMICOLON:                 cmd_defs[modes.VISUAL_LINE][cmds.SEMICOLON],
        seqs.SHIFT_CTRL_F12:            cmd_defs[modes.VISUAL_LINE][cmds.SHIFT_CTRL_F12],
        seqs.SHIFT_ENTER:               cmd_defs[modes.VISUAL_LINE][cmds.SHIFT_ENTER],
        seqs.SLASH:                     cmd_defs[modes.VISUAL_LINE][cmds.SLASH],
        seqs.STAR:                      cmd_defs[modes.VISUAL_LINE][cmds.STAR],
        seqs.T:                         cmd_defs[modes.VISUAL_LINE][cmds.T],
        seqs.TILDE:                     cmd_defs[modes.NORMAL][cmds.TILDE],
        seqs.U:                         cmd_defs[modes.VISUAL_LINE][cmds.U],
        seqs.UNDERSCORE:                cmd_defs[modes.VISUAL_LINE][cmds.UNDERSCORE],
        seqs.V:                         cmd_defs[modes.VISUAL_LINE][cmds.V],
        seqs.W:                         cmd_defs[modes.VISUAL_LINE][cmds.W],
        seqs.X:                         cmd_defs[modes.VISUAL_LINE][cmds.X],
        seqs.X:                         cmd_defs[modes.VISUAL_LINE][cmds.X],
        seqs.Y:                         cmd_defs[modes.VISUAL_LINE][cmds.Y],
        seqs.Y:                         cmd_defs[modes.VISUAL_LINE][cmds.Y],
        seqs.YY:                        cmd_defs[modes.VISUAL_LINE][cmds.YY],
        seqs.Z:                         cmd_defs[modes.VISUAL_LINE][cmds.Z],
        seqs.Z_ENTER:                   cmd_defs[modes.VISUAL_LINE][cmds.Z_ENTER],
        seqs.Z_MINUS:                   cmd_defs[modes.VISUAL_LINE][cmds.Z_MINUS],
        seqs.ZB:                        cmd_defs[modes.VISUAL_LINE][cmds.ZB],
        seqs.ZERO:                      cmd_defs[modes.VISUAL_LINE][cmds.ZERO],
        seqs.ZT:                        cmd_defs[modes.VISUAL_LINE][cmds.ZT],
        seqs.ZZ:                        cmd_defs[modes.VISUAL_LINE][cmds.ZZ],
        seqs.ZZ:                        cmd_defs[modes.VISUAL_LINE][cmds.ZZ],
    },

    # Mode Visual Block ======================================================

    modes.VISUAL_BLOCK: {
        seqs.DOWN:                      cmd_defs[modes.VISUAL_BLOCK][cmds.J],
        seqs.END:                       cmd_defs[modes.VISUAL_BLOCK][cmds.DOLLAR],
        seqs.HOME:                      cmd_defs[modes.VISUAL_BLOCK][cmds.ZERO],
        seqs.LEFT:                      cmd_defs[modes.VISUAL_BLOCK][cmds.H],
        seqs.RIGHT:                     cmd_defs[modes.VISUAL_BLOCK][cmds.L],
        seqs.UP:                        cmd_defs[modes.VISUAL_BLOCK][cmds.K],
        seqs.A:                         cmd_defs[modes.VISUAL_BLOCK][cmds.A],
        seqs.ALT_CTRL_P:                cmd_defs[modes.VISUAL_BLOCK][cmds.ALT_CTRL_P],
        seqs.B:                         cmd_defs[modes.VISUAL_BLOCK][cmds.B],
        seqs.BACKTICK:                  cmd_defs[modes.VISUAL_BLOCK][cmds.BACKTICK],
        seqs.BIG_B:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_B],
        seqs.BIG_B:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_B],
        seqs.BIG_C:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_C],
        seqs.BIG_D:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_D],
        seqs.BIG_E:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_E],
        seqs.BIG_F:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_F],
        seqs.BIG_G:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_G],
        seqs.BIG_H:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_H],
        seqs.BIG_J:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_J],
        seqs.BIG_L:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_L],
        seqs.BIG_M:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_M],
        seqs.BIG_N:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_N],
        seqs.BIG_O:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_O],
        seqs.BIG_P:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_P],
        seqs.BIG_S:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_S],
        seqs.BIG_T:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_T],
        seqs.BIG_U:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_U],
        seqs.BIG_V:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_V],
        seqs.BIG_W:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_W],
        seqs.BIG_X:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_X],
        seqs.BIG_Y:                     cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_Y],
        seqs.BIG_Z:                     cmd_defs[modes.NORMAL][cmds.BIG_Z],
        seqs.BIG_Z_BIG_Q:               cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_Z_BIG_Q],
        seqs.BIG_Z_BIG_Z:               cmd_defs[modes.VISUAL_BLOCK][cmds.BIG_Z_BIG_Z],
        seqs.C:                         cmd_defs[modes.VISUAL_BLOCK][cmds.C],
        seqs.CC:                        cmd_defs[modes.VISUAL_BLOCK][cmds.CC],
        seqs.COLON:                     cmd_defs[modes.VISUAL_BLOCK][cmds.COLON],
        seqs.COMMA:                     cmd_defs[modes.VISUAL_BLOCK][cmds.COMMA],
        seqs.CTRL_A:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_A],
        seqs.CTRL_B:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_B],
        seqs.CTRL_BIG_P:                cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_BIG_P],
        seqs.CTRL_D:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_D],
        seqs.CTRL_E:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_E],
        seqs.CTRL_F12:                  cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_F12],
        seqs.CTRL_F:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_F],
        seqs.CTRL_K_CTRL_B:             cmd_defs[modes.NORMAL][cmds.CTRL_K_CTRL_B],
        seqs.CTRL_P:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_P],
        seqs.CTRL_R:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_R],
        seqs.CTRL_R_EQUAL:              cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_R_EQUAL],
        seqs.CTRL_U:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_U],
        seqs.CTRL_V:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_V],
        seqs.CTRL_W:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_W],
        seqs.CTRL_W_BIG_H:              cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_W_BIG_H],
        seqs.CTRL_W_BIG_L:              cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_W_BIG_L],
        seqs.CTRL_W_H:                  cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_W_H],
        seqs.CTRL_W_L:                  cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_W_L],
        seqs.CTRL_W_Q:                  cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_W_Q],
        seqs.CTRL_W_V:                  cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_W_V],
        seqs.CTRL_X:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_X],
        seqs.CTRL_Y:                    cmd_defs[modes.VISUAL_BLOCK][cmds.CTRL_Y],
        seqs.D:                         cmd_defs[modes.VISUAL_BLOCK][cmds.D],
        seqs.DD:                        cmd_defs[modes.VISUAL_BLOCK][cmds.DD],
        seqs.DOLLAR:                    cmd_defs[modes.VISUAL_BLOCK][cmds.DOLLAR],
        seqs.DOT:                       cmd_defs[modes.VISUAL_BLOCK][cmds.DOT],
        seqs.DOUBLE_QUOTE:              cmd_defs[modes.VISUAL_BLOCK][cmds.DOUBLE_QUOTE],
        seqs.E:                         cmd_defs[modes.VISUAL_BLOCK][cmds.E],
        seqs.ENTER:                     cmd_defs[modes.VISUAL_BLOCK][cmds.ENTER],
        seqs.EQUAL:                     cmd_defs[modes.VISUAL_BLOCK][cmds.EQUAL],
        seqs.ESC:                       cmd_defs[modes.VISUAL_BLOCK][cmds.ESC],
        seqs.F11:                       cmd_defs[modes.VISUAL_BLOCK][cmds.F11],
        seqs.F12:                       cmd_defs[modes.VISUAL_BLOCK][cmds.F12],
        seqs.F7:                        cmd_defs[modes.VISUAL_BLOCK][cmds.F7],
        seqs.F:                         cmd_defs[modes.VISUAL_BLOCK][cmds.F],
        seqs.G:                         cmd_defs[modes.VISUAL_BLOCK][cmds.G],
        seqs.G_BIG_J:                   cmd_defs[modes.VISUAL_BLOCK][cmds.G_BIG_J],
        seqs.G_BIG_T:                   cmd_defs[modes.VISUAL_BLOCK][cmds.G_BIG_T],
        seqs.G_BIG_U:                   cmd_defs[modes.VISUAL_BLOCK][cmds.G_BIG_U],
        seqs.G_TILDE:                   cmd_defs[modes.VISUAL_BLOCK][cmds.G_TILDE],
        seqs.G_TILDE_G_TILDE:           cmd_defs[modes.VISUAL_BLOCK][cmds.G_TILDE_G_TILDE],
        seqs.G_UNDERSCORE:              cmd_defs[modes.VISUAL_BLOCK][cmds.G_UNDERSCORE],
        seqs.GE:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GE],
        seqs.GG:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GG],
        seqs.GH:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GH],
        seqs.GJ:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GJ],
        seqs.GK:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GK],
        seqs.GQ:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GQ],
        seqs.GREATER_THAN:              cmd_defs[modes.VISUAL_BLOCK][cmds.GREATER_THAN],
        seqs.GREATER_THAN_GREATER_THAN: cmd_defs[modes.VISUAL_BLOCK][cmds.GREATER_THAN_GREATER_THAN],
        seqs.GT:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GT],
        seqs.GU:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GU],
        seqs.GU:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GU],
        seqs.GV:                        cmd_defs[modes.VISUAL_BLOCK][cmds.GV],
        seqs.H:                         cmd_defs[modes.VISUAL_BLOCK][cmds.H],
        seqs.HAT:                       cmd_defs[modes.VISUAL_BLOCK][cmds.HAT],
        seqs.I:                         cmd_defs[modes.VISUAL_BLOCK][cmds.I],
        seqs.J:                         cmd_defs[modes.VISUAL_BLOCK][cmds.J],
        seqs.K:                         cmd_defs[modes.VISUAL_BLOCK][cmds.K],
        seqs.L:                         cmd_defs[modes.VISUAL_BLOCK][cmds.L],
        seqs.LEFT_BRACE:                cmd_defs[modes.VISUAL_BLOCK][cmds.LEFT_BRACE],
        seqs.LEFT_PAREN:                cmd_defs[modes.VISUAL_BLOCK][cmds.LEFT_PAREN],
        seqs.LEFT_SQUARE_BRACKET:       cmd_defs[modes.VISUAL_BLOCK][cmds.LEFT_SQUARE_BRACKET],
        seqs.LESS_THAN:                 cmd_defs[modes.VISUAL_BLOCK][cmds.LESS_THAN],
        seqs.LESS_THAN:                 cmd_defs[modes.VISUAL_BLOCK][cmds.LESS_THAN],
        seqs.LESS_THAN_LESS_THAN:       cmd_defs[modes.VISUAL_BLOCK][cmds.LESS_THAN_LESS_THAN],
        seqs.N:                         cmd_defs[modes.VISUAL_BLOCK][cmds.N],
        seqs.O:                         cmd_defs[modes.VISUAL_BLOCK][cmds.O],
        seqs.O:                         cmd_defs[modes.VISUAL_BLOCK][cmds.O],
        seqs.OCTOTHORP:                 cmd_defs[modes.VISUAL_BLOCK][cmds.OCTOTHORP],
        seqs.P:                         cmd_defs[modes.VISUAL_BLOCK][cmds.P],
        seqs.PERCENT:                   cmd_defs[modes.VISUAL_BLOCK][cmds.PERCENT],
        seqs.PIPE:                      cmd_defs[modes.VISUAL_BLOCK][cmds.PIPE],
        seqs.QUESTION_MARK:             cmd_defs[modes.VISUAL_BLOCK][cmds.QUESTION_MARK],
        seqs.QUOTE:                     cmd_defs[modes.VISUAL_BLOCK][cmds.QUOTE],
        seqs.R:                         cmd_defs[modes.VISUAL_BLOCK][cmds.R],
        seqs.RIGHT_BRACE:               cmd_defs[modes.VISUAL_BLOCK][cmds.RIGHT_BRACE],
        seqs.RIGHT_SQUARE_BRACKET:      cmd_defs[modes.VISUAL_BLOCK][cmds.RIGHT_SQUARE_BRACKET],
        seqs.S:                         cmd_defs[modes.VISUAL_BLOCK][cmds.S],
        seqs.S:                         cmd_defs[modes.VISUAL_BLOCK][cmds.S],
        seqs.SEMICOLON:                 cmd_defs[modes.VISUAL_BLOCK][cmds.SEMICOLON],
        seqs.SHIFT_CTRL_F12:            cmd_defs[modes.VISUAL_BLOCK][cmds.SHIFT_CTRL_F12],
        seqs.SHIFT_ENTER:               cmd_defs[modes.VISUAL_BLOCK][cmds.SHIFT_ENTER],
        seqs.SLASH:                     cmd_defs[modes.VISUAL_BLOCK][cmds.SLASH],
        seqs.STAR:                      cmd_defs[modes.VISUAL_BLOCK][cmds.STAR],
        seqs.T:                         cmd_defs[modes.VISUAL_BLOCK][cmds.T],
        seqs.TILDE:                     cmd_defs[modes.NORMAL][cmds.TILDE],
        seqs.U:                         cmd_defs[modes.VISUAL_BLOCK][cmds.U],
        seqs.UNDERSCORE:                cmd_defs[modes.VISUAL_BLOCK][cmds.UNDERSCORE],
        seqs.V:                         cmd_defs[modes.VISUAL_BLOCK][cmds.V],
        seqs.W:                         cmd_defs[modes.VISUAL_BLOCK][cmds.W],
        seqs.X:                         cmd_defs[modes.VISUAL_BLOCK][cmds.X],
        seqs.X:                         cmd_defs[modes.VISUAL_BLOCK][cmds.X],
        seqs.Y:                         cmd_defs[modes.VISUAL_BLOCK][cmds.Y],
        seqs.Z:                         cmd_defs[modes.VISUAL_BLOCK][cmds.Z],
        seqs.Z_ENTER:                   cmd_defs[modes.VISUAL_BLOCK][cmds.Z_ENTER],
        seqs.Z_MINUS:                   cmd_defs[modes.VISUAL_BLOCK][cmds.Z_MINUS],
        seqs.ZB:                        cmd_defs[modes.VISUAL_BLOCK][cmds.ZB],
        seqs.ZERO:                      cmd_defs[modes.VISUAL_BLOCK][cmds.ZERO],
        seqs.ZT:                        cmd_defs[modes.VISUAL_BLOCK][cmds.ZT],
        seqs.ZZ:                        cmd_defs[modes.VISUAL_BLOCK][cmds.ZZ],
        seqs.ZZ:                        cmd_defs[modes.VISUAL_BLOCK][cmds.ZZ],
    },

    # Mode Select ============================================================

    modes.SELECT: {
        seqs.BIG_A: cmd_defs[modes.SELECT][cmds.BIG_A],
        seqs.BIG_J: cmd_defs[modes.SELECT][cmds.BIG_J],
        seqs.I:     cmd_defs[modes.SELECT][cmds.I],
        seqs.J:     cmd_defs[modes.SELECT][cmds.J],
        seqs.K:     cmd_defs[modes.SELECT][cmds.K],
        seqs.L:     cmd_defs[modes.SELECT][cmds.L],
    },

    # Extra ==================================================================

    '_missing': cmd_defs[modes.NORMAL][cmds.MISSING],
}


# TODO: Add a timeout for ambiguous commands.
# Key sequence to command mapping. Mappings are set by the user.
#
# Returns a partial definition containing the user-pressed keys so that we
# can replay the command exactly as it was typed in.
user_mappings = {
    # 'jkl': dict(name='dd', type=cmd_types.USER),
}


EOF = -2

class key_names:
    """
    Names of special keys.
    """
    BACKSPACE   = '<bs>'
    CR          = '<cr>'
    ENTER       = '<enter>'
    ESCAPE      = '<esc>'
    F1          = '<f1>'
    F2          = '<f2>'
    F3          = '<f3>'
    F4          = '<f4>'
    F5          = '<f5>'
    F6          = '<f6>'
    F7          = '<f7>'
    F8          = '<f8>'
    F9          = '<f9>'
    F10         = '<f10>'
    F11         = '<f11>'
    F12         = '<f12>'
    F13         = '<f13>'
    F14         = '<f14>'
    F15         = '<f15>'
    LESS_THAN   = '<lt>'
    SPACE       = '<sp>'
    SPACE_LONG  = '<space>'

    as_list = [
        LESS_THAN,
        ENTER,
        ESCAPE,
        CR,
        BACKSPACE,
        SPACE,
        SPACE_LONG,
        F1,
        F2,
        F3,
        F4,
        F5,
        F6,
        F7,
        F8,
        F9,
        F10,
        F11,
        F12,
        F13,
        F14,
        F15,
    ]

    max_len = len('<space>')


class KeySequenceTokenizer(object):
    """
    Takes in a sequence of key names and tokenizes it.
    """
    def __init__(self, source):
        """
        @source
          A sequence of key names in Vim notation.
        """
        self.idx = -1
        self.source = source
        self.in_named_key = False

    def consume(self):
        self.idx += 1
        if self.idx >= len(self.source):
            self.idx -= -1
            return EOF
        return self.source[self.idx]

    def peek_one(self):
        if (self.idx + 1) >= len(self.source):
            return EOF
        return self.source[self.idx + 1]

    def is_named_key(self, key):
        return key.lower() in key_names.as_list

    def sort_modifiers(self, modifiers):
        """
        Ensures consistency in the order of modifier letters according to:

          c > m > s
        """
        if len(modifiers) == 2:
            if modifiers.startswith('s-') and modifiers.endswith('c-'):
                modifiers = 'c-s-'
            elif modifiers.startswith('s-') and modifiers.endswith('m-'):
                modifiers = 'm-s-'
            elif modifiers.startswith('m-') and modifiers.endswith('c-'):
                modifiers = 'c-m-'
        elif len(modifiers) == 6:
            modifiers = 'c-m-s-'
        return modifiers

    def long_key_name(self):
        self.in_named_key = True
        key_name = ''
        modifiers = ''

        while True:
            c = self.consume()

            if c == EOF:
                raise ValueError("expected '>' at index {0}".format(self.idx))

            elif (c.lower() in ('c', 's', 'm')) and (self.peek_one() == '-'):
                if c.lower() in modifiers.lower():
                    raise ValueError('invalid modifier sequence: {0}'.format(self.source))

                modifiers += c + self.consume()

            elif c == '>' and self.peek_one() == '>':
                modifiers = self.sort_modifiers(modifiers.lower())

                if len(key_name) == 0:
                    return '<' + modifiers.upper() + self.consume() + '>'

                else:
                    raise ValueError('wrong key {0}'.format(key_name))

            elif c == '>':
                modifiers = self.sort_modifiers(modifiers.lower())

                if len(key_name) == 1:
                    if not modifiers:
                        raise ValueError('wrong sequence {0}'.format(self.source))
                    return '<' + modifiers.upper() + key_name + '>'

                elif self.is_named_key('<' + key_name + '>'):
                    self.in_named_key = False
                    return '<' + modifiers.upper() + key_name.lower() + '>'

                else:
                    raise ValueError("'{0}' is not a known key".format(key_name))

            else:
                key_name += c

    def tokenize_one(self):
        c = self.consume()

        if c == '<':
            return self.long_key_name()
        else:
            return c

    def iter_tokenize(self):
        while True:
            token = self.tokenize_one()
            yield token
            if token == EOF:
                break


def to_bare_command_name(seq):
    """
    Strips register and count data from @seq.
    """
    # Special case.
    if seq == '0':
        return seq

    new_seq = re.sub(r'^(?:".)?(?:[1-9]+)?', '', seq)
    # Account for d2d and similar sequences.
    new_seq = list(KeySequenceTokenizer(new_seq).iter_tokenize())[:-1]

    return ''.join(k for k in new_seq if not k.isdigit())
