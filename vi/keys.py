import re
import logging

from Vintageous.vi import inputs
from Vintageous.vi.utils import input_types
from Vintageous.vi.utils import modes
from Vintageous.vi import utils
from Vintageous import local_logger


_logger = local_logger(__name__)


class mapping_scopes:
    """
    Scopes for mappings.
    """
    DEFAULT = 0
    USER = 1
    PLUGIN = 2
    NAME_SPACE = 3
    LEADER = 4
    LOCAL_LEADER = 5


class cmds:
    """
    Vim commands' names.
    """
    # QUESTION_MARK = 'vi_question_mark'
    A = 'vi_a'
    ALT_CTRL_P = 'vi_ctrl_alt_p'
    AMPERSAND = 'vi_ampersand'
    B = 'vi_b'
    BACKTICK = 'vi_backtick'
    BIG_A = 'vi_big_a'
    BIG_B = 'vi_big_b'
    BIG_C = 'vi_big_c'
    BIG_D = 'vi_big_d'
    CTRL_K_CTRL_B = 'vi_ctrl_k_ctrl_b'
    GH = 'vi_gh'
    Q = 'vi_q'
    AT = 'vi_at'
    BIG_E = 'vi_big_e'
    BIG_F = 'vi_big_f'
    BIG_G = 'vi_big_g'
    BIG_H = 'vi_H'
    BIG_I = 'vi_big_i'
    BIG_V = 'vi_big_v'
    BIG_Z_BIG_Z = 'vi_big_z_big_z'
    BIG_Z_BIG_Q = 'vi_big_z_big_q'
    GV = 'vi_gv'

    CTRL_E = 'vi_ctrl_e'
    CTRL_Y = 'vi_ctrl_y'
    BIG_J = 'vi_big_j'
    G_BIG_J = 'vi_g_big_j'
    Z = 'open_name_space'
    BIG_Z = 'open_name_space'
    Z_ENTER = 'vi_z_enter'
    ZT = 'vi_z_t'
    ZZ = 'vi_zz'
    Z_MINUS = 'vi_z_minus'
    ZB = 'vi_z_b'

    CTRL_R= 'open_name_space'
    CTRL_R_EQUAL = 'vi_ctrl_r_equal'
    CTRL_A = 'vi_ctrl_a'
    CTRL_X = 'vi_ctrl_x'

    CTRL_W_Q = 'vi_ctrl_w_q'
    CTRL_BIG_P = 'vi_ctrl_big_p'
    CTRL_W_V = 'vi_ctrl_w_v'
    CTRL_W_L = 'vi_ctrl_w_l'
    CTRL_W_BIG_L = 'vi_ctrl_w_big_l'
    CTRL_W_H = 'vi_ctrl_w_h'
    CTRL_W_BIG_H = 'vi_ctrl_w_big_h'
    A_TEXT_OBJECT = 'vi_a_text_object'
    I_TEXT_OBJECT = 'vi_i_text_object'
    BIG_J = 'vi_big_j'
    BIG_K = 'vi_big_k'
    BIG_L = 'vi_L'
    BIG_M = 'vi_M'
    BIG_N = 'vi_big_n'
    BIG_O = 'vi_big_o'
    BIG_P = 'vi_big_p'
    BIG_Q = 'vi_big_q'
    BIG_R = 'vi_big_r'
    BIG_S = 'vi_big_s'
    BIG_T = 'vi_big_t'
    BIG_U = 'vi_U'
    BIG_W = 'vi_W'
    BIG_X = 'vi_big_x'
    BIG_Y = 'vi_big_y'
    BIG_Z = 'vi_Z'
    C = 'vi_c'
    CC = 'vi_cc'
    COLON = 'vi_colon'
    COMMA = 'vi_comma'
    CTRL_B = 'vi_ctrl_b'
    CTRL_D = 'vi_ctrl_d'
    CTRL_F = 'vi_ctrl_f'
    CTRL_F12 = 'vi_ctrl_f12'
    CTRL_F11 = 'vi_ctrl_f11'
    CTRL_L = 'vi_ctrl_l'
    CTRL_P = 'vi_ctrl_p'
    CTRL_R = 'vi_ctrl_r'
    CTRL_U = 'vi_ctrl_u'
    D = 'vi_d'
    DD = 'vi_dd'
    DOLLAR = 'vi_dollar'
    DOT = 'vi_dot'
    DOUBLE_QUOTE = 'vi_double_quote'
    E = 'vi_e'
    EN_DASH = 'vi_en_dash'
    ENTER = 'vi_enter'
    SHIFT_ENTER = 'vi_shift_enter'
    EQUAL = 'vi_equal'
    EQUAL_EQUAL = 'vi_equal_equal'
    ESC = 'vi_esc'
    EXCLAMATION = 'vi_exclamation'
    F = 'vi_f'
    F1 = 'vi_f1'
    F10 = 'vi_f10'
    F11 = 'vi_f11'
    F12 = 'vi_f12'
    F12 = 'vi_f12'
    F13 = 'vi_f13'
    F14 = 'vi_f14'
    F15 = 'vi_f15'
    F2 = 'vi_f2'
    F3 = 'vi_f3'
    F4 = 'vi_f4'
    F5 = 'vi_f5'
    F6 = 'vi_f6'
    F7 = 'vi_f7'
    F8 = 'vi_f8'
    F9 = 'vi_f9'
    G = 'vi_g'
    G_BIG_D = 'vi_g_big_d'
    G_BIG_U = 'vi_gU'
    G_TILDE = 'vi_g_tilde'
    G_TILDE_G_TILDE = 'vi_g_tilde_g_tilde'
    G_TILDE_TILDE = 'vi_g_tilde_tilde'
    G_UNDERSCORE = 'vi_g__'
    GD = 'vi_gd'
    GE = 'vi_ge'
    GG = 'vi_gg'
    GJ = 'vi_g_j'
    GK = 'vi_g_k'
    GQ = 'vi_gq'
    GT = 'vi_gt'
    G_BIG_T = 'vi_g_big_t'
    GU = 'vi_gu'
    GREATER_THAN = 'vi_greater_than'
    GREATER_THAN = 'vi_greater_than'
    GREATER_THAN_GREATER_THAN = 'vi_greater_than_greater_than'
    H = 'vi_h'
    HAT = 'vi_hat'
    I = 'vi_i'
    J = 'vi_j'
    K = 'vi_k'
    L = 'vi_l'
    LEFT_BRACE = 'vi_left_brace'
    LEFT_CURLY_BRACE = 'vi_left_curly_brace'
    LEFT_PAREN = 'vi_left_paren'
    LESS_THAN = 'vi_less_than'
    LESS_THAN_LESS_THAN = 'vi_less_than_less_than'
    M = 'vi_m'
    MISSING = '_missing'
    N = 'vi_n'
    O = 'vi_o'
    P = 'vi_p'
    OCTOTHORP = 'vi_octothorp'
    OPEN_NAME_SPACE = 'open_name_space'
    OPEN_REGISTERS = 'open_registers'
    PERCENT = 'vi_percent'
    PIPE = 'vi_pipe'
    PLUS = 'vi_plus'
    QUESTION_MARK = 'vi_question_mark'
    QUOTE = 'vi_quote'
    QUOTE_QUOTE = 'vi_quote_quote'
    R = 'vi_r'
    RIGHT_BRACE = 'vi_right_brace'
    RIGHT_CURLY_BRACE = 'vi_right_curly_brace'
    RIGHT_PAREN = 'vi_right_paren'
    RIGHT_PAREN = 'vi_right_paren'
    S = 'vi_s'
    CTRL_W = 'open_name_space'
    SEMICOLON = 'vi_semicolon'
    SHIFT_CTRL_F12 = 'vi_shift_ctrl_f12'
    SHIFT_ENTER = 'vi_shift_enter'
    SLASH = 'vi_slash'
    SLASH_IMPL = 'vi_slash_impl'
    QUESTION_MARK_IMPL = 'vi_question_mark_impl'
    STAR = 'vi_star'
    T = 'vi_t'
    U = 'vi_u'
    UNDERSCORE = 'vi_underscore'
    V = 'vi_v'
    W = 'vi_w'
    X = 'vi_x'
    Y = 'vi_y'
    YY = 'vi_yy'
    ZERO = 'vi_0'


class seqs:
    """
    Vim's default key sequences.
    """
    A = 'a'
    ALT_CTRL_P = '<ctrl+alt+p>'
    AMPERSAND = '&'
    AW = 'aw'
    B = 'b'
    GE = 'ge'
    UP = '<up>'
    DOWN = '<down>'
    LEFT = '<left>'
    RIGHT = '<right>'
    HOME = '<home>'
    END = '<end>'
    BACKTICK = '`'
    BIG_A = 'A'
    SPACE = '<space>'
    BIG_B = 'B'
    CTRL_E = '<ctrl+e>'
    CTRL_Y = '<ctrl+y>'
    BIG_C = 'C'
    BIG_D = 'D'
    GH = 'gh'
    BIG_E = 'E'
    BIG_F = 'F'
    BIG_G = 'G'
    CTRL_W = '<ctrl+w>'
    CTRL_W_Q = '<ctrl+w>q'

    CTRL_W_V = '<ctrl+w>v'
    CTRL_W_L = '<ctrl+w>l'
    CTRL_W_BIG_L = '<ctrl+w>L'
    CTRL_K_CTRL_B = '<ctrl+l><ctrl+b>'
    CTRL_BIG_P = '<ctrl+P>'
    CTRL_W_H = '<ctrl+w>h'
    Q = 'q'
    AT = '@'
    CTRL_W_BIG_H = '<ctrl+w>H'
    BIG_H = 'H'

    BIG_J = 'J'
    BIG_Z = 'Z'
    G_BIG_J = 'gJ'
    CTRL_R= '<ctrl+r>'
    CTRL_R_EQUAL = '<ctrl+r>='
    CTRL_A = '<ctrl+a>'
    CTRL_X = '<ctrl+x>'
    Z = 'z'
    Z_ENTER = 'z<CR>'
    ZT = 'zt'
    ZZ = 'zz'
    Z_MINUS = 'z-'
    ZB = 'zb'

    BIG_I = 'I'
    BIG_Z_BIG_Z = 'ZZ'
    BIG_Z_BIG_Q = 'ZQ'
    GV = 'gv'
    BIG_J = 'J'
    BIG_K = 'K'
    BIG_L = 'L'
    BIG_M = 'M'
    BIG_N = 'N'
    BIG_O = 'O'
    BIG_P = 'P'
    BIG_Q = 'Q'
    BIG_R = 'R'
    BIG_S = 'S'
    BIG_T = 'T'
    BIG_U = 'U'
    BIG_V = 'V'
    BIG_W = 'W'
    BIG_X = 'X'
    BIG_Y = 'Y'
    BIG_Z = 'Z'
    C = 'c'
    CC = 'cc'
    COLON = ':'
    COMMA = ','
    CTRL_D = '<ctrl+d>'
    CTRL_F12 = '<ctrl+f12>'
    F11 = 'f11'
    CTRL_l = '<ctrl+l>'
    CTRL_B = '<ctrl+b>'
    CTRL_F = '<ctrl+f>'
    CTRL_P = '<ctrl+p>'
    CTRL_R = '<ctrl+r>'
    CTRL_U = '<ctrl+u>'
    D = 'd'
    DD = 'dd'
    DOLLAR = '$'
    DOT = '.'
    DOUBLE_QUOTE = '"'
    E = 'e'
    ENTER = '<CR>' # Or rather <Enter>?
    SHIFT_ENTER = '<shift+cr>'
    EQUAL = '='
    EQUAL_EQUAL = '=='
    ESC = '<esc>'
    F = 'f'
    F1 = '<f1>'
    F10 = '<f10>'
    F11 = '<f11>'
    F12 = '<f12>'
    F12 = '<f12>'
    F13 = '<f13>'
    F14 = '<f14>'
    F15 = '<f15>'
    F2 = '<f2>'
    F3 = '<f3>'
    F4 = '<f4>'
    F5 = '<f5>'
    F6 = '<f6>'
    F7 = '<f7>'
    F8 = '<f8>'
    F9 = '<f9>'
    G = 'g'
    G_BIG_D = 'gD'
    G_BIG_U = 'gU'
    G_TILDE = 'g~'
    G_TILDE_G_TILDE = 'g~g~'
    G_TILDE_TILDE = 'g~~'
    G_UNDERSCORE = 'g_'
    GD = 'gd'
    GG = 'gg'
    GJ = 'gj'
    GK = 'gk'
    GQ ='gq'
    GT ='gt'
    G_BIG_T ='gT'
    GU ='gu'
    GREATER_THAN = '>'
    GREATER_THAN_GREATER_THAN = '>>'
    H = 'h'
    HAT = '^'
    I = 'i'
    J = 'j'
    K = 'k'
    L = 'l'
    LEFT_BRACE = '{'
    LEFT_PAREN = '('
    LESS_THAN = '<'
    LESS_THAN_LESS_THAN = '<<'
    M = 'm'
    N = 'n'
    O = 'o'
    P = 'p'
    OCTOTHORP = '#'
    PERCENT = '%'
    PIPE = '|'
    QUESTION_MARK = '?'
    QUOTE = "'"
    QUOTE_QUOTE = "''"
    R = 'r'
    RIGHT_BRACE = '}'
    RIGHT_PAREN = ')'
    S = 's'
    SEMICOLON = ';'
    SHIFT_CTRL_F12 = '<shift+ctrl+f12>'
    SLASH = '/'
    STAR = '*'
    T = 't'
    U = 'u'
    UNDERSCORE = '_'
    V = 'v'
    W = 'w'
    X = 'x'
    Y = 'y'
    YY = 'yy'
    ZERO = '0'


class cmd_types:
    """
    Types of command.
    """
    MOTION = 1
    ACTION = 2
    ANY = 3
    OTHER = 4
    USER = 5


# class input_types:
#     """
#     Types of input parsers.
#     """
#     INMEDIATE = 1


# Command name to command definition mapping.
#
# cmd_defs['vi_k'] => definition for vi_k
cmd_defs = {
    modes.NORMAL: {
        cmds.F:                         dict(name=cmds.F,                           input='vi_f',               type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.GG:                        dict(name=cmds.GG,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_G:                     dict(name=cmds.BIG_G,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.H:                         dict(name=cmds.H,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.J:                         dict(name=cmds.J,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.B:                         dict(name=cmds.B,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_B:                     dict(name=cmds.BIG_B,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_E:                     dict(name=cmds.BIG_E,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_N:                     dict(name=cmds.BIG_N,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.CTRL_B:                    dict(name=cmds.CTRL_B,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.CTRL_F:                    dict(name=cmds.CTRL_F,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.ENTER:                     dict(name=cmds.ENTER,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.GE:                        dict(name=cmds.GE,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.N:                         dict(name=cmds.N,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.QUESTION_MARK:             dict(name=cmds.QUESTION_MARK,               input='vi_question_mark',   type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.SHIFT_ENTER:               dict(name=cmds.SHIFT_ENTER,                 input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.LEFT_PAREN:                dict(name=cmds.LEFT_PAREN,                  input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.RIGHT_PAREN:               dict(name=cmds.RIGHT_PAREN,                 input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.K:                         dict(name=cmds.K,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.L:                         dict(name=cmds.L,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.W:                         dict(name=cmds.W,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.UNDERSCORE:                dict(name=cmds.UNDERSCORE,                  input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.HAT:                       dict(name=cmds.HAT,                         input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.PERCENT:                   dict(name=cmds.PERCENT,                     input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.E:                         dict(name=cmds.E,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.LEFT_BRACE:                dict(name=cmds.LEFT_BRACE,                  input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.RIGHT_BRACE:               dict(name=cmds.RIGHT_BRACE,                 input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.ZERO:                      dict(name=cmds.ZERO,                        input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_W:                     dict(name=cmds.BIG_W,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.STAR:                      dict(name=cmds.STAR,                        input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.OCTOTHORP:                 dict(name=cmds.OCTOTHORP,                   input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.DOLLAR:                    dict(name=cmds.DOLLAR,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.COMMA:                     dict(name=cmds.COMMA,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.G_UNDERSCORE:              dict(name=cmds.G_UNDERSCORE,                input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.SEMICOLON:                 dict(name=cmds.SEMICOLON,                   input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.T:                         dict(name=cmds.T,                           input='vi_t',               type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_F:                     dict(name=cmds.BIG_F,                       input='vi_big_f',           type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_T:                     dict(name=cmds.BIG_T,                       input='vi_big_t',           type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_H:                     dict(name=cmds.BIG_H,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.BIG_L:                     dict(name=cmds.BIG_L,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.CTRL_U:                    dict(name=cmds.CTRL_U,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.CTRL_D:                    dict(name=cmds.CTRL_D,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.PIPE:                      dict(name=cmds.PIPE,                        input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_M:                     dict(name=cmds.BIG_M,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.GK:                        dict(name=cmds.GK,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.GJ:                        dict(name=cmds.GJ,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.QUOTE:                     dict(name=cmds.QUOTE,                       input='vi_quote',           type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.BACKTICK:                  dict(name=cmds.BACKTICK,                    input='vi_backtick',        type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),

        cmds.SLASH:                     dict(name=cmds.SLASH,                       input='vi_slash',           type=cmd_types.MOTION, multi_step=True, updates_xpos=True, scroll_into_view=True),
        cmds.QUESTION_MARK:             dict(name=cmds.QUESTION_MARK,               input='vi_question_mark',   type=cmd_types.MOTION, multi_step=True, updates_xpos=True, scroll_into_view=True),
        cmds.SLASH_IMPL:                dict(name=cmds.SLASH_IMPL,                  input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.QUESTION_MARK_IMPL:        dict(name=cmds.QUESTION_MARK_IMPL,          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),

        cmds.BIG_J:                     dict(name=cmds.BIG_J,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.GV:                        dict(name=cmds.GV,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.G_BIG_J:                   dict(name=cmds.G_BIG_J,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),


        cmds.M:                         dict(name=cmds.M,                           input='vi_m',               type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.D:                         dict(name=cmds.D,                           input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.Y:                         dict(name=cmds.Y,                           input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=False),
        cmds.BIG_D:                     dict(name=cmds.BIG_D,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.BIG_C:                     dict(name=cmds.BIG_C,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.Y:                         dict(name=cmds.Y,                           input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=False),
        cmds.EQUAL:                     dict(name=cmds.EQUAL,                       input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=True, repeatable=True),
        cmds.GREATER_THAN:              dict(name=cmds.GREATER_THAN,                input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=True, repeatable=True),
        cmds.LESS_THAN:                 dict(name=cmds.LESS_THAN,                   input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=True, repeatable=True),
        cmds.C:                         dict(name=cmds.C,                           input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.S:                         dict(name=cmds.S,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.R:                         dict(name=cmds.R,                           input='vi_r',               type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.G_TILDE:                   dict(name=cmds.G_TILDE,                     input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.G_BIG_U:                   dict(name=cmds.G_BIG_U,                     input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),

        cmds.CTRL_R:                    dict(name=cmds.CTRL_R,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.DD:                        dict(name=cmds.DD,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.BIG_Y:                     dict(name=cmds.BIG_Y,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_Z_BIG_Z:               dict(name=cmds.BIG_Z_BIG_Z,                 input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_Z_BIG_Q:               dict(name=cmds.BIG_Z_BIG_Q,                 input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.BIG_O:                     dict(name=cmds.BIG_O,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.Q:                         dict(name=cmds.Q,                           input='vi_q',               type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.AT:                         dict(name=cmds.AT,                         input='vi_at',              type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.O:                         dict(name=cmds.O,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.GH:                        dict(name=cmds.GH,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_X:                     dict(name=cmds.BIG_X,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.P:                         dict(name=cmds.P,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.BIG_P:                     dict(name=cmds.BIG_P,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),

        cmds.GREATER_THAN_GREATER_THAN: dict(name=cmds.GREATER_THAN_GREATER_THAN,   input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.EQUAL_EQUAL:               dict(name=cmds.EQUAL_EQUAL,                 input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.CC:                        dict(name=cmds.CC,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.BIG_S:                     dict(name=cmds.BIG_S,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.G_TILDE_G_TILDE:           dict(name=cmds.G_TILDE_G_TILDE,             input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.G_TILDE_TILDE:             dict(name=cmds.G_TILDE_TILDE,               input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),

        cmds.GU:                        dict(name=cmds.GU,                          input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.GQ:                        dict(name=cmds.GQ,                          input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.GT:                        dict(name=cmds.GT,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.G_BIG_T:                   dict(name=cmds.G_BIG_T,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.CTRL_W_Q:                  dict(name=cmds.CTRL_W_Q,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_V:                  dict(name=cmds.CTRL_W_V,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_L:                  dict(name=cmds.CTRL_W_L,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_BIG_L:              dict(name=cmds.CTRL_W_BIG_L,                input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_H:                  dict(name=cmds.CTRL_W_H,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_BIG_H:              dict(name=cmds.CTRL_W_BIG_H,                input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.Z_ENTER:                   dict(name=cmds.Z_ENTER,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.ZT:                        dict(name=cmds.ZT,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.ZZ:                        dict(name=cmds.ZZ,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.Z_MINUS:                   dict(name=cmds.Z_MINUS,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.ZB:                        dict(name=cmds.ZB,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.CTRL_R_EQUAL:              dict(name=cmds.CTRL_R_EQUAL,                input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_A:                    dict(name=cmds.CTRL_A,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.CTRL_X:                    dict(name=cmds.CTRL_X,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),

        cmds.I:                         dict(name=cmds.I,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_V:                     dict(name=cmds.BIG_V,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_R:                     dict(name=cmds.BIG_R,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.S:                         dict(name=cmds.S,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.LESS_THAN_LESS_THAN:       dict(name=cmds.LESS_THAN_LESS_THAN,         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.U:                         dict(name=cmds.U,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.V:                         dict(name=cmds.V,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.X:                         dict(name=cmds.X,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.A:                         dict(name=cmds.A,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_A:                     dict(name=cmds.BIG_A,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_I:                     dict(name=cmds.BIG_I,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.X:                         dict(name=cmds.X,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.YY:                        dict(name=cmds.YY,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.DOT:                       dict(name=cmds.DOT,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_E:                    dict(name=cmds.CTRL_E,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_Y:                    dict(name=cmds.CTRL_Y,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.G_BIG_D:                   dict(name=cmds.G_BIG_D,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.GD:                        dict(name=cmds.GD,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.QUOTE_QUOTE:               dict(name=cmds.QUOTE_QUOTE,                 input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.COLON:                     dict(name=cmds.COLON,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.ESC:                       dict(name=cmds.ESC,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        # Enable some Sublime Text key bindings.
        cmds.ALT_CTRL_P:                dict(name=cmds.ALT_CTRL_P,                  input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_BIG_P:                dict(name=cmds.CTRL_BIG_P,                  input=None,                type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_F12:                  dict(name=cmds.CTRL_F12,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_K_CTRL_B:             dict(name=cmds.CTRL_K_CTRL_B,               input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_P:                    dict(name=cmds.CTRL_P,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.F11:                       dict(name=cmds.F11,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.F12:                       dict(name=cmds.F12,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.F4:                        dict(name=cmds.F4,                          input=None,                type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.F7:                        dict(name=cmds.F7,                          input=None,                type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.SHIFT_CTRL_F12:            dict(name=cmds.SHIFT_CTRL_F12,              input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.CTRL_W:                    dict(name=cmds.OPEN_NAME_SPACE,             input=None,                type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_Z:                     dict(name=cmds.OPEN_NAME_SPACE,             input=None,                type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.Z:                         dict(name=cmds.OPEN_NAME_SPACE,             input=None,                type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.G:                         dict(name=cmds.OPEN_NAME_SPACE,             input=None,                type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.DOUBLE_QUOTE:              dict(name=cmds.OPEN_REGISTERS,              input=None,                type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),

        cmds.MISSING:                   dict(name=cmds.MISSING,                     input=None,                type=cmd_types.ANY, motion_required=False, multi_step=False)
    }
}

cmd_defs[modes.OPERATOR_PENDING] = cmd_defs[modes.NORMAL].copy()
cmd_defs[modes.VISUAL] = cmd_defs[modes.NORMAL].copy()
cmd_defs[modes.VISUAL][cmds.O] =              dict(name=cmds.O,                     input=None,                 type=cmd_types.ACTION, multi_step=False, motion_required=False, repeatable=False)
cmd_defs[modes.VISUAL][cmds.A] =              dict(name=cmds.A_TEXT_OBJECT,         input='vi_a_text_object',   type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.VISUAL][cmds.I] =              dict(name=cmds.I_TEXT_OBJECT,         input='vi_a_text_object',   type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.OPERATOR_PENDING][cmds.I] =    dict(name=cmds.I_TEXT_OBJECT,         input='vi_a_text_object',   type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.OPERATOR_PENDING][cmds.A] =    dict(name=cmds.A_TEXT_OBJECT,         input='vi_i_text_object',   type=cmd_types.MOTION, multi_step=False)

cmd_defs[modes.VISUAL_LINE] = cmd_defs[modes.NORMAL].copy()

cmd_defs[modes.SELECT] = {}
cmd_defs[modes.SELECT][cmds.I] = dict(name=cmds.I, input=None, type=cmd_types.ACTION, multi_step=False, motion_required=False, repeatable=False)
cmd_defs[modes.SELECT][cmds.J] = dict(name=cmds.J, input=None, type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.SELECT][cmds.L] = dict(name=cmds.L, input=None, type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.SELECT][cmds.K] = dict(name=cmds.K, input=None, type=cmd_types.MOTION, multi_step=False)


def seq_to_command(state, seq):
    _logger().info('[seq_to_command] state {0}'.format(state.mode))
    if state.mode in mappings:
        command = mappings[state.mode].get(seq, mappings['_missing'])
        return command
    return mappings['_missing']


# Key sequence to command mapping.
#
# mappings['d'] => definition for 'vi_d'
mappings = {
    modes.NORMAL: {
        seqs.A: cmd_defs[modes.NORMAL][cmds.A],
        seqs.UNDERSCORE: cmd_defs[modes.NORMAL][cmds.UNDERSCORE],
        seqs.B: cmd_defs[modes.NORMAL][cmds.B],
        seqs.BIG_B: cmd_defs[modes.NORMAL][cmds.BIG_B],
        seqs.CTRL_R: cmd_defs[modes.NORMAL][cmds.CTRL_R],
        seqs.CTRL_R_EQUAL: cmd_defs[modes.NORMAL][cmds.CTRL_R_EQUAL],
        seqs.CTRL_A: cmd_defs[modes.NORMAL][cmds.CTRL_A],
        seqs.HOME: cmd_defs[modes.NORMAL][cmds.GG],
        seqs.END: cmd_defs[modes.NORMAL][cmds.BIG_G],
        seqs.CTRL_X: cmd_defs[modes.NORMAL][cmds.CTRL_X],
        seqs.BIG_E: cmd_defs[modes.NORMAL][cmds.BIG_E],
        seqs.BIG_N: cmd_defs[modes.NORMAL][cmds.BIG_N],
        seqs.CTRL_B: cmd_defs[modes.NORMAL][cmds.CTRL_B],
        seqs.BIG_Z: cmd_defs[modes.NORMAL][cmds.BIG_Z],
        seqs.CTRL_F: cmd_defs[modes.NORMAL][cmds.CTRL_F],
        seqs.BIG_Z_BIG_Q: cmd_defs[modes.NORMAL][cmds.BIG_Z_BIG_Q],
        seqs.GV: cmd_defs[modes.NORMAL][cmds.GV],
        seqs.UP: cmd_defs[modes.NORMAL][cmds.K],
        seqs.DOWN: cmd_defs[modes.NORMAL][cmds.J],
        seqs.LEFT: cmd_defs[modes.NORMAL][cmds.H],
        seqs.RIGHT: cmd_defs[modes.NORMAL][cmds.L],
        seqs.CTRL_K_CTRL_B: cmd_defs[modes.NORMAL][cmds.CTRL_K_CTRL_B],
        seqs.ENTER: cmd_defs[modes.NORMAL][cmds.ENTER],
        seqs.GE: cmd_defs[modes.NORMAL][cmds.GE],
        seqs.N: cmd_defs[modes.NORMAL][cmds.N],
        seqs.QUESTION_MARK: cmd_defs[modes.NORMAL][cmds.QUESTION_MARK],
        seqs.SHIFT_ENTER: cmd_defs[modes.NORMAL][cmds.SHIFT_ENTER],
        seqs.R: cmd_defs[modes.NORMAL][cmds.R],
        seqs.CTRL_BIG_P: cmd_defs[modes.NORMAL][cmds.CTRL_BIG_P],
        seqs.BIG_A: cmd_defs[modes.NORMAL][cmds.BIG_A],
        seqs.BIG_I: cmd_defs[modes.NORMAL][cmds.BIG_I],
        seqs.ALT_CTRL_P: cmd_defs[modes.NORMAL][cmds.ALT_CTRL_P],
        seqs.CTRL_U: cmd_defs[modes.NORMAL][cmds.CTRL_U],
        seqs.CTRL_D: cmd_defs[modes.NORMAL][cmds.CTRL_D],
        seqs.BIG_Y: cmd_defs[modes.NORMAL][cmds.BIG_Y],
        seqs.BIG_F: cmd_defs[modes.NORMAL][cmds.BIG_F],
        seqs.EQUAL: cmd_defs[modes.NORMAL][cmds.EQUAL],
        seqs.ZZ: cmd_defs[modes.NORMAL][cmds.ZZ],
        seqs.BIG_O: cmd_defs[modes.NORMAL][cmds.BIG_O],
        seqs.O: cmd_defs[modes.NORMAL][cmds.O],
        seqs.BIG_X: cmd_defs[modes.NORMAL][cmds.BIG_X],
        seqs.GH: cmd_defs[modes.NORMAL][cmds.GH],
        seqs.P: cmd_defs[modes.NORMAL][cmds.P],
        seqs.BIG_P: cmd_defs[modes.NORMAL][cmds.BIG_P],
        seqs.Y: cmd_defs[modes.NORMAL][cmds.Y],
        seqs.EQUAL_EQUAL: cmd_defs[modes.NORMAL][cmds.EQUAL_EQUAL],
        seqs.GREATER_THAN: cmd_defs[modes.NORMAL][cmds.GREATER_THAN],
        seqs.AT: cmd_defs[modes.NORMAL][cmds.AT],
        seqs.BIG_B: cmd_defs[modes.NORMAL][cmds.BIG_B],
        seqs.BIG_G: cmd_defs[modes.NORMAL][cmds.BIG_G],
        seqs.BIG_T: cmd_defs[modes.NORMAL][cmds.BIG_T],
        seqs.LESS_THAN: cmd_defs[modes.NORMAL][cmds.LESS_THAN],
        seqs.BIG_V: cmd_defs[modes.NORMAL][cmds.BIG_V],
        seqs.LESS_THAN_LESS_THAN: cmd_defs[modes.NORMAL][cmds.LESS_THAN_LESS_THAN],
        seqs.C: cmd_defs[modes.NORMAL][cmds.C],
        seqs.D: cmd_defs[modes.NORMAL][cmds.D],
        seqs.E: cmd_defs[modes.NORMAL][cmds.E],
        seqs.S: cmd_defs[modes.NORMAL][cmds.S],
        seqs.LEFT_PAREN: cmd_defs[modes.NORMAL][cmds.LEFT_PAREN],
        seqs.RIGHT_PAREN: cmd_defs[modes.NORMAL][cmds.RIGHT_PAREN],
        seqs.COLON: cmd_defs[modes.NORMAL][cmds.COLON],
        seqs.DOUBLE_QUOTE: cmd_defs[modes.NORMAL][cmds.DOUBLE_QUOTE],
        seqs.COMMA: cmd_defs[modes.NORMAL][cmds.COMMA],
        seqs.PIPE: cmd_defs[modes.NORMAL][cmds.PIPE],
        seqs.CTRL_W_Q: cmd_defs[modes.NORMAL][cmds.CTRL_W_Q],
        seqs.CTRL_W_V: cmd_defs[modes.NORMAL][cmds.CTRL_W_V],
        seqs.CTRL_W_L: cmd_defs[modes.NORMAL][cmds.CTRL_W_L],
        seqs.CTRL_W_BIG_L: cmd_defs[modes.NORMAL][cmds.CTRL_W_BIG_L],
        seqs.CTRL_W_H: cmd_defs[modes.NORMAL][cmds.CTRL_W_H],
        seqs.BIG_Z: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_Z],
        seqs.BIG_Z_BIG_Z: cmd_defs[modes.NORMAL][cmds.BIG_Z_BIG_Z],
        seqs.Z: cmd_defs[modes.NORMAL][cmds.Z],
        seqs.Z_ENTER: cmd_defs[modes.NORMAL][cmds.Z_ENTER],
        seqs.ZT: cmd_defs[modes.NORMAL][cmds.ZT],
        seqs.ZZ: cmd_defs[modes.NORMAL][cmds.ZZ],
        seqs.Z_MINUS: cmd_defs[modes.NORMAL][cmds.Z_MINUS],
        seqs.ZB: cmd_defs[modes.NORMAL][cmds.ZB],
        seqs.GU: cmd_defs[modes.NORMAL][cmds.GU],
        seqs.GQ: cmd_defs[modes.NORMAL][cmds.GQ],
        seqs.GT: cmd_defs[modes.NORMAL][cmds.GT],
        seqs.G_BIG_T: cmd_defs[modes.NORMAL][cmds.G_BIG_T],
        seqs.CTRL_F12: cmd_defs[modes.NORMAL][cmds.CTRL_F12],
        seqs.CTRL_P: cmd_defs[modes.NORMAL][cmds.CTRL_P],
        seqs.CTRL_R: cmd_defs[modes.NORMAL][cmds.CTRL_R],
        seqs.Q: cmd_defs[modes.NORMAL][cmds.Q],
        seqs.D: cmd_defs[modes.NORMAL][cmds.D],
        seqs.RIGHT_BRACE: cmd_defs[modes.NORMAL][cmds.RIGHT_BRACE],
        seqs.LEFT_BRACE: cmd_defs[modes.NORMAL][cmds.LEFT_BRACE],
        seqs.ZERO: cmd_defs[modes.NORMAL][cmds.ZERO],
        seqs.PERCENT: cmd_defs[modes.NORMAL][cmds.PERCENT],
        seqs.BIG_D: cmd_defs[modes.NORMAL][cmds.BIG_D],
        seqs.DD: cmd_defs[modes.NORMAL][cmds.DD],
        seqs.CC: cmd_defs[modes.NORMAL][cmds.CC],
        seqs.GJ: cmd_defs[modes.NORMAL][cmds.GJ],
        seqs.GK: cmd_defs[modes.NORMAL][cmds.GK],
        seqs.DOT: cmd_defs[modes.NORMAL][cmds.DOT],
        seqs.ESC: cmd_defs[modes.NORMAL][cmds.ESC],
        seqs.F12: cmd_defs[modes.NORMAL][cmds.F12],
        seqs.F11: cmd_defs[modes.NORMAL][cmds.F11],
        seqs.BIG_L: cmd_defs[modes.NORMAL][cmds.BIG_L],
        seqs.BIG_M: cmd_defs[modes.NORMAL][cmds.BIG_M],
        seqs.BIG_H: cmd_defs[modes.NORMAL][cmds.BIG_H],
        seqs.STAR: cmd_defs[modes.NORMAL][cmds.STAR],
        seqs.OCTOTHORP: cmd_defs[modes.NORMAL][cmds.OCTOTHORP],
        seqs.F: cmd_defs[modes.NORMAL][cmds.F],
        seqs.G: cmd_defs[modes.NORMAL][cmds.G],
        seqs.GD: cmd_defs[modes.NORMAL][cmds.GD],
        seqs.G_BIG_D: cmd_defs[modes.NORMAL][cmds.G_BIG_D],
        seqs.G_BIG_U: cmd_defs[modes.NORMAL][cmds.G_BIG_U],
        seqs.G_TILDE: cmd_defs[modes.NORMAL][cmds.G_TILDE],
        seqs.G_TILDE_G_TILDE: cmd_defs[modes.NORMAL][cmds.G_TILDE_G_TILDE],
        seqs.G_TILDE_TILDE: cmd_defs[modes.NORMAL][cmds.G_TILDE_TILDE],
        seqs.F7: cmd_defs[modes.NORMAL][cmds.F7],
        seqs.GG: cmd_defs[modes.NORMAL][cmds.GG],
        seqs.H: cmd_defs[modes.NORMAL][cmds.H],
        seqs.I: cmd_defs[modes.NORMAL][cmds.I],
        seqs.J: cmd_defs[modes.NORMAL][cmds.J],
        seqs.K: cmd_defs[modes.NORMAL][cmds.K],
        seqs.L: cmd_defs[modes.NORMAL][cmds.L],
        seqs.M: cmd_defs[modes.NORMAL][cmds.M],
        seqs.CTRL_E: cmd_defs[modes.NORMAL][cmds.CTRL_E],
        seqs.CTRL_Y: cmd_defs[modes.NORMAL][cmds.CTRL_Y],
        seqs.QUOTE: cmd_defs[modes.NORMAL][cmds.QUOTE],
        seqs.DOLLAR: cmd_defs[modes.NORMAL][cmds.DOLLAR],
        seqs.QUOTE_QUOTE: cmd_defs[modes.NORMAL][cmds.QUOTE_QUOTE],
        seqs.BACKTICK: cmd_defs[modes.NORMAL][cmds.BACKTICK],
        seqs.LESS_THAN: cmd_defs[modes.NORMAL][cmds.LESS_THAN],
        # seqs.QUESTION_MARK: cmd_defs[modes.NORMAL][cmds.QUESTION_MARK],
        seqs.BIG_R: cmd_defs[modes.NORMAL][cmds.BIG_R],
        seqs.BIG_C: cmd_defs[modes.NORMAL][cmds.BIG_C],
        seqs.S: cmd_defs[modes.NORMAL][cmds.S],
        seqs.SEMICOLON: cmd_defs[modes.NORMAL][cmds.SEMICOLON],
        seqs.SHIFT_CTRL_F12: cmd_defs[modes.NORMAL][cmds.SHIFT_CTRL_F12],
        seqs.SLASH: cmd_defs[modes.NORMAL][cmds.SLASH],
        seqs.T: cmd_defs[modes.NORMAL][cmds.T],
        seqs.U: cmd_defs[modes.NORMAL][cmds.U],
        seqs.F4: cmd_defs[modes.NORMAL][cmds.F4],
        seqs.G_UNDERSCORE: cmd_defs[modes.NORMAL][cmds.G_UNDERSCORE],
        seqs.X: cmd_defs[modes.NORMAL][cmds.X],
        seqs.HAT: cmd_defs[modes.NORMAL][cmds.HAT],
        seqs.BIG_J: cmd_defs[modes.NORMAL][cmds.BIG_J],
        seqs.G_BIG_J: cmd_defs[modes.NORMAL][cmds.G_BIG_J],
        seqs.Y: cmd_defs[modes.NORMAL][cmds.Y],
        seqs.YY: cmd_defs[modes.NORMAL][cmds.YY],
        seqs.BIG_S: cmd_defs[modes.NORMAL][cmds.BIG_S],
        seqs.CTRL_W: cmd_defs[modes.NORMAL][cmds.CTRL_W],
        seqs.V: cmd_defs[modes.NORMAL][cmds.V],
        seqs.X: cmd_defs[modes.NORMAL][cmds.X],
        seqs.W: cmd_defs[modes.NORMAL][cmds.W],
        seqs.BIG_W: cmd_defs[modes.NORMAL][cmds.BIG_W],
    },
    modes.VISUAL: {
        seqs.A: cmd_defs[modes.VISUAL][cmds.A],
        seqs.COLON: cmd_defs[modes.VISUAL][cmds.COLON],
        seqs.CTRL_P: cmd_defs[modes.VISUAL][cmds.CTRL_P],

seqs.CTRL_R: cmd_defs[modes.VISUAL][cmds.CTRL_R],
seqs.CTRL_R_EQUAL: cmd_defs[modes.VISUAL][cmds.CTRL_R_EQUAL],
seqs.CTRL_A: cmd_defs[modes.VISUAL][cmds.CTRL_A],
seqs.CTRL_X: cmd_defs[modes.VISUAL][cmds.CTRL_X],

        seqs.B: cmd_defs[modes.VISUAL][cmds.B],
        seqs.BIG_B: cmd_defs[modes.VISUAL][cmds.BIG_B],
        seqs.BIG_E: cmd_defs[modes.VISUAL][cmds.BIG_E],
        seqs.BIG_N: cmd_defs[modes.VISUAL][cmds.BIG_N],
        seqs.CTRL_B: cmd_defs[modes.VISUAL][cmds.CTRL_B],
        seqs.GV: cmd_defs[modes.VISUAL][cmds.GV],
        seqs.CTRL_F: cmd_defs[modes.VISUAL][cmds.CTRL_F],
        seqs.ENTER: cmd_defs[modes.VISUAL][cmds.ENTER],
        seqs.GE: cmd_defs[modes.VISUAL][cmds.GE],
        seqs.N: cmd_defs[modes.VISUAL][cmds.N],
        seqs.QUESTION_MARK: cmd_defs[modes.VISUAL][cmds.QUESTION_MARK],
        seqs.SHIFT_ENTER: cmd_defs[modes.VISUAL][cmds.SHIFT_ENTER],
        seqs.ALT_CTRL_P: cmd_defs[modes.VISUAL][cmds.ALT_CTRL_P],

        seqs.Z: cmd_defs[modes.VISUAL][cmds.Z],
        seqs.Z_ENTER: cmd_defs[modes.VISUAL][cmds.Z_ENTER],
        seqs.ZT: cmd_defs[modes.VISUAL][cmds.ZT],
        seqs.ZZ: cmd_defs[modes.VISUAL][cmds.ZZ],
        seqs.Z_MINUS: cmd_defs[modes.VISUAL][cmds.Z_MINUS],
        seqs.ZB: cmd_defs[modes.VISUAL][cmds.ZB],

        seqs.CTRL_D: cmd_defs[modes.VISUAL][cmds.CTRL_D],
        seqs.BIG_Z_BIG_Q: cmd_defs[modes.VISUAL][cmds.BIG_Z_BIG_Q],
        seqs.CTRL_R: cmd_defs[modes.VISUAL][cmds.CTRL_R],
        seqs.CTRL_BIG_P: cmd_defs[modes.VISUAL][cmds.CTRL_BIG_P],
        seqs.BIG_B: cmd_defs[modes.VISUAL][cmds.BIG_B],
        seqs.BIG_Z: cmd_defs[modes.NORMAL][cmds.BIG_Z],
        seqs.CTRL_K_CTRL_B: cmd_defs[modes.NORMAL][cmds.CTRL_K_CTRL_B],
        seqs.C: cmd_defs[modes.VISUAL][cmds.C],
        seqs.E: cmd_defs[modes.VISUAL][cmds.E],
        seqs.BIG_V: cmd_defs[modes.VISUAL][cmds.BIG_V],
        seqs.BIG_Y: cmd_defs[modes.VISUAL][cmds.BIG_Y],
        seqs.S: cmd_defs[modes.VISUAL][cmds.S],

seqs.GU: cmd_defs[modes.VISUAL][cmds.GU],
seqs.GU: cmd_defs[modes.VISUAL][cmds.GU],
seqs.GQ: cmd_defs[modes.VISUAL][cmds.GQ],
seqs.GT: cmd_defs[modes.VISUAL][cmds.GT],
seqs.G_BIG_T: cmd_defs[modes.VISUAL][cmds.G_BIG_T],

        # seqs.HOME: cmd_defs[modes.VISUAL][cmds.GG],
        # seqs.END: cmd_defs[modes.VISUAL][cmds.BIG_G],
        seqs.R: cmd_defs[modes.VISUAL][cmds.R],
        seqs.STAR: cmd_defs[modes.VISUAL][cmds.STAR],
        seqs.OCTOTHORP: cmd_defs[modes.VISUAL][cmds.OCTOTHORP],
        seqs.LEFT_PAREN: cmd_defs[modes.VISUAL][cmds.LEFT_PAREN],
        seqs.RIGHT_BRACE: cmd_defs[modes.VISUAL][cmds.RIGHT_BRACE],
        seqs.LEFT_BRACE: cmd_defs[modes.VISUAL][cmds.LEFT_BRACE],
        seqs.ZZ: cmd_defs[modes.VISUAL][cmds.ZZ],
        seqs.D: cmd_defs[modes.VISUAL][cmds.D],
seqs.BIG_O: cmd_defs[modes.VISUAL][cmds.BIG_O],
seqs.O: cmd_defs[modes.VISUAL][cmds.O],
seqs.BIG_X: cmd_defs[modes.VISUAL][cmds.BIG_X],
seqs.P: cmd_defs[modes.VISUAL][cmds.P],
seqs.BIG_P: cmd_defs[modes.VISUAL][cmds.BIG_P],
seqs.Y: cmd_defs[modes.VISUAL][cmds.Y],
        seqs.EQUAL: cmd_defs[modes.VISUAL][cmds.EQUAL],
        seqs.CTRL_U: cmd_defs[modes.VISUAL][cmds.CTRL_U],
        seqs.EQUAL_EQUAL: cmd_defs[modes.VISUAL][cmds.EQUAL_EQUAL],
        seqs.GJ: cmd_defs[modes.VISUAL][cmds.GJ],
        seqs.GK: cmd_defs[modes.VISUAL][cmds.GK],
seqs.CTRL_W_Q: cmd_defs[modes.VISUAL][cmds.CTRL_W_Q],
seqs.CTRL_W_V: cmd_defs[modes.VISUAL][cmds.CTRL_W_V],
seqs.CTRL_W_L: cmd_defs[modes.VISUAL][cmds.CTRL_W_L],
seqs.CTRL_W_BIG_L: cmd_defs[modes.VISUAL][cmds.CTRL_W_BIG_L],
seqs.CTRL_W_H: cmd_defs[modes.VISUAL][cmds.CTRL_W_H],
seqs.CTRL_W_BIG_H: cmd_defs[modes.VISUAL][cmds.CTRL_W_BIG_H],

        seqs.PIPE: cmd_defs[modes.VISUAL][cmds.PIPE],
        seqs.F7: cmd_defs[modes.VISUAL][cmds.F7],
        seqs.GREATER_THAN: cmd_defs[modes.VISUAL][cmds.GREATER_THAN],
        seqs.GREATER_THAN_GREATER_THAN: cmd_defs[modes.VISUAL][cmds.GREATER_THAN_GREATER_THAN],
        seqs.LESS_THAN: cmd_defs[modes.VISUAL][cmds.LESS_THAN],
        seqs.LESS_THAN_LESS_THAN: cmd_defs[modes.VISUAL][cmds.LESS_THAN_LESS_THAN],
        seqs.UNDERSCORE: cmd_defs[modes.VISUAL][cmds.UNDERSCORE],

seqs.BIG_J: cmd_defs[modes.VISUAL][cmds.BIG_J],
seqs.G_BIG_J: cmd_defs[modes.VISUAL][cmds.G_BIG_J],

        seqs.ZERO: cmd_defs[modes.VISUAL][cmds.ZERO],
        seqs.DOUBLE_QUOTE: cmd_defs[modes.VISUAL][cmds.DOUBLE_QUOTE],
        seqs.PERCENT: cmd_defs[modes.VISUAL][cmds.PERCENT],
        seqs.BIG_D: cmd_defs[modes.VISUAL][cmds.BIG_D],
        seqs.DD: cmd_defs[modes.VISUAL][cmds.DD],
        seqs.BIG_S: cmd_defs[modes.VISUAL][cmds.BIG_S],
        seqs.CC: cmd_defs[modes.VISUAL][cmds.CC],
        seqs.ESC: cmd_defs[modes.VISUAL][cmds.ESC],
        seqs.F: cmd_defs[modes.VISUAL][cmds.F],
        seqs.G: cmd_defs[modes.VISUAL][cmds.G],
        seqs.G_BIG_U: cmd_defs[modes.VISUAL][cmds.G_BIG_U],
        seqs.G_TILDE: cmd_defs[modes.VISUAL][cmds.G_TILDE],
        seqs.G_TILDE_G_TILDE: cmd_defs[modes.VISUAL][cmds.G_TILDE_G_TILDE],
        seqs.G_TILDE_TILDE: cmd_defs[modes.VISUAL][cmds.G_TILDE_TILDE],
        seqs.GG: cmd_defs[modes.VISUAL][cmds.GG],
        # seqs.UP: cmd_defs[modes.VISUAL][cmds.K],
        # seqs.DOWN: cmd_defs[modes.VISUAL][cmds.J],
        # seqs.LEFT: cmd_defs[modes.VISUAL][cmds.H],
        # seqs.RIGHT: cmd_defs[modes.VISUAL][cmds.L],
        seqs.H: cmd_defs[modes.VISUAL][cmds.H],
        seqs.I: cmd_defs[modes.VISUAL][cmds.I],
        seqs.J: cmd_defs[modes.VISUAL][cmds.J],
        seqs.K: cmd_defs[modes.VISUAL][cmds.K],
        seqs.BIG_H: cmd_defs[modes.VISUAL][cmds.BIG_H],
        seqs.BIG_L: cmd_defs[modes.VISUAL][cmds.BIG_L],
        seqs.BIG_M: cmd_defs[modes.VISUAL][cmds.BIG_M],
        seqs.L: cmd_defs[modes.VISUAL][cmds.L],
        seqs.LESS_THAN: cmd_defs[modes.VISUAL][cmds.LESS_THAN],
        seqs.O: cmd_defs[modes.VISUAL][cmds.O],
        seqs.QUOTE: cmd_defs[modes.VISUAL][cmds.QUOTE],
        seqs.DOLLAR: cmd_defs[modes.VISUAL][cmds.DOLLAR],
        seqs.BACKTICK: cmd_defs[modes.VISUAL][cmds.BACKTICK],
        seqs.S: cmd_defs[modes.VISUAL][cmds.S],
        seqs.DOT: cmd_defs[modes.VISUAL][cmds.DOT],
        seqs.T: cmd_defs[modes.VISUAL][cmds.T],
        seqs.U: cmd_defs[modes.VISUAL][cmds.U],
        seqs.V: cmd_defs[modes.VISUAL][cmds.V],
        seqs.X: cmd_defs[modes.VISUAL][cmds.X],
        seqs.W: cmd_defs[modes.VISUAL][cmds.W],
        seqs.F12: cmd_defs[modes.VISUAL][cmds.F12],
        seqs.F11: cmd_defs[modes.VISUAL][cmds.F11],
        seqs.CTRL_F12: cmd_defs[modes.VISUAL][cmds.CTRL_F12],
        seqs.SHIFT_CTRL_F12: cmd_defs[modes.VISUAL][cmds.SHIFT_CTRL_F12],
        seqs.SLASH: cmd_defs[modes.VISUAL][cmds.SLASH],
        # seqs.QUESTION_MARK: cmd_defs[modes.VISUAL][cmds.QUESTION_MARK],
        seqs.COMMA: cmd_defs[modes.VISUAL][cmds.COMMA],
        seqs.SEMICOLON: cmd_defs[modes.VISUAL][cmds.SEMICOLON],
        seqs.X: cmd_defs[modes.VISUAL][cmds.X],
        seqs.CTRL_W: cmd_defs[modes.VISUAL][cmds.CTRL_W],

        seqs.BIG_F: cmd_defs[modes.VISUAL][cmds.BIG_F],
        seqs.G_UNDERSCORE: cmd_defs[modes.VISUAL][cmds.G_UNDERSCORE],
        seqs.CTRL_E: cmd_defs[modes.VISUAL][cmds.CTRL_E],
        seqs.CTRL_Y: cmd_defs[modes.VISUAL][cmds.CTRL_Y],
        seqs.BIG_G: cmd_defs[modes.VISUAL][cmds.BIG_G],
        seqs.BIG_T: cmd_defs[modes.VISUAL][cmds.BIG_T],
        seqs.HAT: cmd_defs[modes.VISUAL][cmds.HAT],
        seqs.BIG_Z_BIG_Z: cmd_defs[modes.VISUAL][cmds.BIG_Z_BIG_Z],
        seqs.BIG_C: cmd_defs[modes.VISUAL][cmds.BIG_C],
        seqs.BIG_W: cmd_defs[modes.VISUAL][cmds.BIG_W],
    },
    modes.OPERATOR_PENDING: {
        seqs.A: cmd_defs[modes.OPERATOR_PENDING][cmds.A],
        seqs.COLON: cmd_defs[modes.OPERATOR_PENDING][cmds.COLON],

        seqs.HOME: cmd_defs[modes.OPERATOR_PENDING][cmds.GG],
        seqs.END: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_G],
seqs.Z: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_R],
seqs.Z_ENTER: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_R_EQUAL],
seqs.ZT: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_A],
seqs.ZZ: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_X],

        seqs.B: cmd_defs[modes.OPERATOR_PENDING][cmds.B],
        seqs.BIG_B: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_B],
        seqs.BIG_E: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_E],
        seqs.BIG_N: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_N],
        seqs.CTRL_B: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_B],
        seqs.GU: cmd_defs[modes.OPERATOR_PENDING][cmds.GU],
        seqs.GQ: cmd_defs[modes.OPERATOR_PENDING][cmds.GQ],
        seqs.GT: cmd_defs[modes.OPERATOR_PENDING][cmds.GT],
        seqs.G_BIG_T: cmd_defs[modes.OPERATOR_PENDING][cmds.G_BIG_T],
        seqs.CTRL_F: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_F],
        seqs.ENTER: cmd_defs[modes.OPERATOR_PENDING][cmds.ENTER],
        seqs.CTRL_E: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_E],
        seqs.CTRL_Y: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_Y],
        seqs.ZZ: cmd_defs[modes.OPERATOR_PENDING][cmds.ZZ],
        seqs.GE: cmd_defs[modes.OPERATOR_PENDING][cmds.GE],
        seqs.N: cmd_defs[modes.OPERATOR_PENDING][cmds.N],
        seqs.QUESTION_MARK: cmd_defs[modes.OPERATOR_PENDING][cmds.QUESTION_MARK],
        seqs.BIG_Y: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_Y],
        seqs.SHIFT_ENTER: cmd_defs[modes.OPERATOR_PENDING][cmds.SHIFT_ENTER],
        seqs.GV: cmd_defs[modes.OPERATOR_PENDING][cmds.GV],
        seqs.CTRL_P: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_P],
        seqs.CTRL_D: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_D],
        seqs.ALT_CTRL_P: cmd_defs[modes.OPERATOR_PENDING][cmds.ALT_CTRL_P],
        seqs.CTRL_K_CTRL_B: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_K_CTRL_B],
        seqs.UP: cmd_defs[modes.OPERATOR_PENDING][cmds.K],
        seqs.DOWN: cmd_defs[modes.OPERATOR_PENDING][cmds.J],
        seqs.LEFT: cmd_defs[modes.OPERATOR_PENDING][cmds.H],
        seqs.RIGHT: cmd_defs[modes.OPERATOR_PENDING][cmds.L],
        seqs.BIG_B: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_B],
        seqs.UNDERSCORE: cmd_defs[modes.OPERATOR_PENDING][cmds.UNDERSCORE],
        seqs.CTRL_BIG_P: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_BIG_P],
        seqs.HAT: cmd_defs[modes.OPERATOR_PENDING][cmds.HAT],
        seqs.LESS_THAN: cmd_defs[modes.OPERATOR_PENDING][cmds.LESS_THAN],
seqs.BIG_J: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_J],
seqs.G_BIG_J: cmd_defs[modes.OPERATOR_PENDING][cmds.G_BIG_J],

        seqs.BIG_O: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_O],
        seqs.O: cmd_defs[modes.OPERATOR_PENDING][cmds.O],
        seqs.BIG_X: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_X],
        seqs.P: cmd_defs[modes.OPERATOR_PENDING][cmds.P],
        seqs.BIG_P: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_P],
        seqs.Y: cmd_defs[modes.OPERATOR_PENDING][cmds.Y],
        seqs.Z: cmd_defs[modes.OPERATOR_PENDING][cmds.Z],
        seqs.Z_ENTER: cmd_defs[modes.OPERATOR_PENDING][cmds.Z_ENTER],
        seqs.ZT: cmd_defs[modes.OPERATOR_PENDING][cmds.ZT],
        seqs.ZZ: cmd_defs[modes.OPERATOR_PENDING][cmds.ZZ],
        seqs.Z_MINUS: cmd_defs[modes.OPERATOR_PENDING][cmds.Z_MINUS],
        seqs.ZB: cmd_defs[modes.OPERATOR_PENDING][cmds.ZB],
        seqs.LESS_THAN_LESS_THAN: cmd_defs[modes.OPERATOR_PENDING][cmds.LESS_THAN_LESS_THAN],
        seqs.BIG_S: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_S],
        seqs.R: cmd_defs[modes.OPERATOR_PENDING][cmds.R],
        seqs.CTRL_R: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_R],
        seqs.CTRL_W_Q: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_W_Q],
        seqs.BIG_Z_BIG_Q: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_Z_BIG_Q],
        seqs.CTRL_W_V: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_W_V],
        seqs.CTRL_W_L: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_W_L],
        seqs.CTRL_W_BIG_L: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_W_BIG_L],
        seqs.CTRL_W_H: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_W_H],
        seqs.CTRL_W_BIG_H: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_W_BIG_H],
        seqs.EQUAL: cmd_defs[modes.OPERATOR_PENDING][cmds.EQUAL],
        seqs.GJ: cmd_defs[modes.OPERATOR_PENDING][cmds.GJ],
        seqs.CTRL_U: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_U],
        seqs.GK: cmd_defs[modes.OPERATOR_PENDING][cmds.GK],
        seqs.LEFT_PAREN: cmd_defs[modes.OPERATOR_PENDING][cmds.LEFT_PAREN],
        seqs.RIGHT_PAREN: cmd_defs[modes.OPERATOR_PENDING][cmds.RIGHT_PAREN],
        seqs.EQUAL_EQUAL: cmd_defs[modes.OPERATOR_PENDING][cmds.EQUAL_EQUAL],
        seqs.GREATER_THAN: cmd_defs[modes.OPERATOR_PENDING][cmds.GREATER_THAN],
        seqs.GREATER_THAN_GREATER_THAN: cmd_defs[modes.OPERATOR_PENDING][cmds.GREATER_THAN_GREATER_THAN],
        seqs.C: cmd_defs[modes.OPERATOR_PENDING][cmds.C],
        seqs.RIGHT_BRACE: cmd_defs[modes.OPERATOR_PENDING][cmds.RIGHT_BRACE],
        seqs.LEFT_BRACE: cmd_defs[modes.OPERATOR_PENDING][cmds.LEFT_BRACE],
        seqs.STAR: cmd_defs[modes.OPERATOR_PENDING][cmds.STAR],
        seqs.S: cmd_defs[modes.OPERATOR_PENDING][cmds.S],
        seqs.OCTOTHORP: cmd_defs[modes.OPERATOR_PENDING][cmds.OCTOTHORP],
        seqs.PIPE: cmd_defs[modes.OPERATOR_PENDING][cmds.PIPE],
        seqs.CC: cmd_defs[modes.OPERATOR_PENDING][cmds.CC],
        seqs.D: cmd_defs[modes.OPERATOR_PENDING][cmds.D],
        seqs.E: cmd_defs[modes.OPERATOR_PENDING][cmds.E],
        seqs.DOLLAR: cmd_defs[modes.OPERATOR_PENDING][cmds.DOLLAR],
        seqs.X: cmd_defs[modes.OPERATOR_PENDING][cmds.X],
        seqs.DD: cmd_defs[modes.OPERATOR_PENDING][cmds.DD],
        seqs.ESC: cmd_defs[modes.OPERATOR_PENDING][cmds.ESC],
        seqs.PERCENT: cmd_defs[modes.OPERATOR_PENDING][cmds.PERCENT],
        seqs.F: cmd_defs[modes.OPERATOR_PENDING][cmds.F],
        seqs.G: cmd_defs[modes.OPERATOR_PENDING][cmds.G],
        seqs.CTRL_W: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_W],
        seqs.ZERO: cmd_defs[modes.OPERATOR_PENDING][cmds.ZERO],
        seqs.G_BIG_U: cmd_defs[modes.OPERATOR_PENDING][cmds.G_BIG_U],
        seqs.G_TILDE: cmd_defs[modes.OPERATOR_PENDING][cmds.G_TILDE],
        seqs.G_TILDE_G_TILDE: cmd_defs[modes.OPERATOR_PENDING][cmds.G_TILDE_G_TILDE],
        seqs.G_TILDE_TILDE: cmd_defs[modes.OPERATOR_PENDING][cmds.G_TILDE_TILDE],
        seqs.GG: cmd_defs[modes.OPERATOR_PENDING][cmds.GG],
        seqs.BIG_H: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_H],
        seqs.BIG_M: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_M],
        seqs.BIG_L: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_L],
        seqs.H: cmd_defs[modes.OPERATOR_PENDING][cmds.H],
        seqs.I: cmd_defs[modes.OPERATOR_PENDING][cmds.I],
        seqs.J: cmd_defs[modes.OPERATOR_PENDING][cmds.J],
        seqs.K: cmd_defs[modes.OPERATOR_PENDING][cmds.K],
        seqs.L: cmd_defs[modes.OPERATOR_PENDING][cmds.L],
        seqs.LESS_THAN: cmd_defs[modes.OPERATOR_PENDING][cmds.LESS_THAN],
        seqs.S: cmd_defs[modes.OPERATOR_PENDING][cmds.S],
        seqs.DOT: cmd_defs[modes.OPERATOR_PENDING][cmds.DOT],
        seqs.T: cmd_defs[modes.OPERATOR_PENDING][cmds.T],
        seqs.U: cmd_defs[modes.OPERATOR_PENDING][cmds.U],
        seqs.YY: cmd_defs[modes.OPERATOR_PENDING][cmds.YY],
        seqs.V: cmd_defs[modes.OPERATOR_PENDING][cmds.V],
        seqs.X: cmd_defs[modes.OPERATOR_PENDING][cmds.X],
        seqs.W: cmd_defs[modes.OPERATOR_PENDING][cmds.W],
        seqs.F11: cmd_defs[modes.OPERATOR_PENDING][cmds.F11],
        seqs.CTRL_F12: cmd_defs[modes.OPERATOR_PENDING][cmds.CTRL_F12],
        seqs.SHIFT_CTRL_F12: cmd_defs[modes.OPERATOR_PENDING][cmds.SHIFT_CTRL_F12],
        seqs.SLASH: cmd_defs[modes.OPERATOR_PENDING][cmds.SLASH],
        # seqs.QUESTION_MARK: cmd_defs[modes.OPERATOR_PENDING][cmds.QUESTION_MARK],
        seqs.COMMA: cmd_defs[modes.OPERATOR_PENDING][cmds.COMMA],
        seqs.SEMICOLON: cmd_defs[modes.OPERATOR_PENDING][cmds.SEMICOLON],
        seqs.BIG_F: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_F],
        seqs.BIG_G: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_G],
        seqs.BIG_T: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_T],
        seqs.BIG_W: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_W],
        seqs.G_UNDERSCORE: cmd_defs[modes.OPERATOR_PENDING][cmds.G_UNDERSCORE],
        seqs.BIG_Z: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_Z],
        seqs.BIG_Z_BIG_Z: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_Z_BIG_Z],
    },
    modes.VISUAL_LINE: {
        seqs.A: cmd_defs[modes.VISUAL_LINE][cmds.A],
        seqs.UNDERSCORE: cmd_defs[modes.VISUAL_LINE][cmds.UNDERSCORE],
        seqs.B: cmd_defs[modes.VISUAL_LINE][cmds.B],
        seqs.BIG_B: cmd_defs[modes.VISUAL_LINE][cmds.BIG_B],
        seqs.CTRL_R: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_R],
        seqs.CTRL_R_EQUAL: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_R_EQUAL],
        seqs.CTRL_A: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_A],
        seqs.CTRL_X: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_X],
        seqs.BIG_E: cmd_defs[modes.VISUAL_LINE][cmds.BIG_E],
        seqs.BIG_N: cmd_defs[modes.VISUAL_LINE][cmds.BIG_N],
        seqs.CTRL_B: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_B],
        seqs.BIG_Z: cmd_defs[modes.VISUAL_LINE][cmds.BIG_Z],
        seqs.CTRL_F: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_F],
        seqs.BIG_Z_BIG_Q: cmd_defs[modes.VISUAL_LINE][cmds.BIG_Z_BIG_Q],
        seqs.GV: cmd_defs[modes.VISUAL_LINE][cmds.GV],
        seqs.ENTER: cmd_defs[modes.VISUAL_LINE][cmds.ENTER],
        seqs.LESS_THAN: cmd_defs[modes.VISUAL_LINE][cmds.LESS_THAN],
        seqs.GE: cmd_defs[modes.VISUAL_LINE][cmds.GE],
        seqs.N: cmd_defs[modes.VISUAL_LINE][cmds.N],
        seqs.QUESTION_MARK: cmd_defs[modes.VISUAL_LINE][cmds.QUESTION_MARK],
        seqs.SHIFT_ENTER: cmd_defs[modes.VISUAL_LINE][cmds.SHIFT_ENTER],
        seqs.R: cmd_defs[modes.VISUAL_LINE][cmds.R],
        seqs.CTRL_BIG_P: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_BIG_P],
        seqs.BIG_A: cmd_defs[modes.VISUAL_LINE][cmds.BIG_A],
        seqs.BIG_I: cmd_defs[modes.VISUAL_LINE][cmds.BIG_I],
        seqs.ALT_CTRL_P: cmd_defs[modes.VISUAL_LINE][cmds.ALT_CTRL_P],
        seqs.CTRL_U: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_U],
        seqs.CTRL_D: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_D],
        seqs.BIG_Y: cmd_defs[modes.VISUAL_LINE][cmds.BIG_Y],
        seqs.BIG_F: cmd_defs[modes.VISUAL_LINE][cmds.BIG_F],
        seqs.EQUAL: cmd_defs[modes.VISUAL_LINE][cmds.EQUAL],
        seqs.ZZ: cmd_defs[modes.VISUAL_LINE][cmds.ZZ],
        seqs.BIG_O: cmd_defs[modes.VISUAL_LINE][cmds.BIG_O],
        seqs.O: cmd_defs[modes.VISUAL_LINE][cmds.O],
        seqs.BIG_X: cmd_defs[modes.VISUAL_LINE][cmds.BIG_X],
        seqs.P: cmd_defs[modes.VISUAL_LINE][cmds.P],
        seqs.BIG_P: cmd_defs[modes.VISUAL_LINE][cmds.BIG_P],
        seqs.Y: cmd_defs[modes.VISUAL_LINE][cmds.Y],
        seqs.EQUAL_EQUAL: cmd_defs[modes.VISUAL_LINE][cmds.EQUAL_EQUAL],
        seqs.GREATER_THAN: cmd_defs[modes.VISUAL_LINE][cmds.GREATER_THAN],
        seqs.BIG_B: cmd_defs[modes.VISUAL_LINE][cmds.BIG_B],
        seqs.BIG_G: cmd_defs[modes.VISUAL_LINE][cmds.BIG_G],
        seqs.BIG_T: cmd_defs[modes.VISUAL_LINE][cmds.BIG_T],
        seqs.CTRL_K_CTRL_B: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_K_CTRL_B],
        seqs.BIG_V: cmd_defs[modes.VISUAL_LINE][cmds.BIG_V],
        seqs.C: cmd_defs[modes.VISUAL_LINE][cmds.C],
        seqs.D: cmd_defs[modes.VISUAL_LINE][cmds.D],
        seqs.E: cmd_defs[modes.VISUAL_LINE][cmds.E],
        seqs.S: cmd_defs[modes.VISUAL_LINE][cmds.S],
        seqs.LEFT_PAREN: cmd_defs[modes.VISUAL_LINE][cmds.LEFT_PAREN],
        seqs.RIGHT_PAREN: cmd_defs[modes.VISUAL_LINE][cmds.RIGHT_PAREN],
        seqs.COLON: cmd_defs[modes.VISUAL_LINE][cmds.COLON],
        seqs.DOUBLE_QUOTE: cmd_defs[modes.VISUAL_LINE][cmds.DOUBLE_QUOTE],
        seqs.COMMA: cmd_defs[modes.VISUAL_LINE][cmds.COMMA],
        seqs.PIPE: cmd_defs[modes.VISUAL_LINE][cmds.PIPE],
        seqs.CTRL_W_Q: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_Q],
        seqs.CTRL_W_V: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_V],
        seqs.CTRL_W_L: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_L],
        seqs.CTRL_W_BIG_L: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_BIG_L],
        seqs.CTRL_W_H: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W_H],
        seqs.BIG_Z: cmd_defs[modes.OPERATOR_PENDING][cmds.BIG_Z],
        seqs.BIG_Z_BIG_Z: cmd_defs[modes.VISUAL_LINE][cmds.BIG_Z_BIG_Z],
        seqs.Z: cmd_defs[modes.VISUAL_LINE][cmds.Z],
        seqs.Z_ENTER: cmd_defs[modes.VISUAL_LINE][cmds.Z_ENTER],
        seqs.ZT: cmd_defs[modes.VISUAL_LINE][cmds.ZT],
        seqs.ZZ: cmd_defs[modes.VISUAL_LINE][cmds.ZZ],
        seqs.Z_MINUS: cmd_defs[modes.VISUAL_LINE][cmds.Z_MINUS],
        seqs.ZB: cmd_defs[modes.VISUAL_LINE][cmds.ZB],
        seqs.GU: cmd_defs[modes.VISUAL_LINE][cmds.GU],
        seqs.GQ: cmd_defs[modes.VISUAL_LINE][cmds.GQ],
        seqs.GT: cmd_defs[modes.VISUAL_LINE][cmds.GT],
        seqs.G_BIG_T: cmd_defs[modes.VISUAL_LINE][cmds.G_BIG_T],
        seqs.CTRL_F12: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_F12],
        seqs.CTRL_P: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_P],
        seqs.CTRL_R: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_R],
        seqs.D: cmd_defs[modes.VISUAL_LINE][cmds.D],
        seqs.RIGHT_BRACE: cmd_defs[modes.VISUAL_LINE][cmds.RIGHT_BRACE],
        seqs.LEFT_BRACE: cmd_defs[modes.VISUAL_LINE][cmds.LEFT_BRACE],
        seqs.ZERO: cmd_defs[modes.VISUAL_LINE][cmds.ZERO],
        seqs.PERCENT: cmd_defs[modes.VISUAL_LINE][cmds.PERCENT],
        seqs.BIG_D: cmd_defs[modes.VISUAL_LINE][cmds.BIG_D],
        seqs.DD: cmd_defs[modes.VISUAL_LINE][cmds.DD],
        seqs.CC: cmd_defs[modes.VISUAL_LINE][cmds.CC],
        seqs.GJ: cmd_defs[modes.VISUAL_LINE][cmds.GJ],
        seqs.GK: cmd_defs[modes.VISUAL_LINE][cmds.GK],
        seqs.DOT: cmd_defs[modes.VISUAL_LINE][cmds.DOT],
        seqs.ESC: cmd_defs[modes.VISUAL_LINE][cmds.ESC],
        seqs.F12: cmd_defs[modes.VISUAL_LINE][cmds.F12],
        seqs.F11: cmd_defs[modes.VISUAL_LINE][cmds.F11],
        seqs.BIG_L: cmd_defs[modes.VISUAL_LINE][cmds.BIG_L],
        seqs.BIG_M: cmd_defs[modes.VISUAL_LINE][cmds.BIG_M],
        seqs.BIG_H: cmd_defs[modes.VISUAL_LINE][cmds.BIG_H],
        seqs.STAR: cmd_defs[modes.VISUAL_LINE][cmds.STAR],
        seqs.OCTOTHORP: cmd_defs[modes.VISUAL_LINE][cmds.OCTOTHORP],
        seqs.F: cmd_defs[modes.VISUAL_LINE][cmds.F],
        seqs.G: cmd_defs[modes.VISUAL_LINE][cmds.G],
        seqs.GD: cmd_defs[modes.VISUAL_LINE][cmds.GD],
        seqs.G_BIG_D: cmd_defs[modes.VISUAL_LINE][cmds.G_BIG_D],
        seqs.G_BIG_U: cmd_defs[modes.VISUAL_LINE][cmds.G_BIG_U],
        seqs.G_TILDE: cmd_defs[modes.VISUAL_LINE][cmds.G_TILDE],
        seqs.G_TILDE_G_TILDE: cmd_defs[modes.VISUAL_LINE][cmds.G_TILDE_G_TILDE],
        seqs.G_TILDE_TILDE: cmd_defs[modes.VISUAL_LINE][cmds.G_TILDE_TILDE],
        seqs.F7: cmd_defs[modes.VISUAL_LINE][cmds.F7],
        seqs.GG: cmd_defs[modes.VISUAL_LINE][cmds.GG],
        seqs.H: cmd_defs[modes.VISUAL_LINE][cmds.H],
        seqs.I: cmd_defs[modes.VISUAL_LINE][cmds.I],
        seqs.J: cmd_defs[modes.VISUAL_LINE][cmds.J],
        seqs.K: cmd_defs[modes.VISUAL_LINE][cmds.K],
        seqs.L: cmd_defs[modes.VISUAL_LINE][cmds.L],
        seqs.M: cmd_defs[modes.VISUAL_LINE][cmds.M],
        seqs.CTRL_E: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_E],
        seqs.CTRL_Y: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_Y],
        seqs.QUOTE: cmd_defs[modes.VISUAL_LINE][cmds.QUOTE],
        seqs.DOLLAR: cmd_defs[modes.VISUAL_LINE][cmds.DOLLAR],
        seqs.QUOTE_QUOTE: cmd_defs[modes.VISUAL_LINE][cmds.QUOTE_QUOTE],
        seqs.BACKTICK: cmd_defs[modes.VISUAL_LINE][cmds.BACKTICK],
        seqs.BIG_R: cmd_defs[modes.VISUAL_LINE][cmds.BIG_R],
        seqs.BIG_C: cmd_defs[modes.VISUAL_LINE][cmds.BIG_C],
        seqs.S: cmd_defs[modes.VISUAL_LINE][cmds.S],
        seqs.SEMICOLON: cmd_defs[modes.VISUAL_LINE][cmds.SEMICOLON],
        seqs.SHIFT_CTRL_F12: cmd_defs[modes.VISUAL_LINE][cmds.SHIFT_CTRL_F12],
        seqs.SLASH: cmd_defs[modes.VISUAL_LINE][cmds.SLASH],
        seqs.T: cmd_defs[modes.VISUAL_LINE][cmds.T],
        seqs.U: cmd_defs[modes.VISUAL_LINE][cmds.U],
        seqs.G_UNDERSCORE: cmd_defs[modes.VISUAL_LINE][cmds.G_UNDERSCORE],
        seqs.X: cmd_defs[modes.VISUAL_LINE][cmds.X],
        seqs.HAT: cmd_defs[modes.VISUAL_LINE][cmds.HAT],
        seqs.BIG_J: cmd_defs[modes.VISUAL_LINE][cmds.BIG_J],
        seqs.G_BIG_J: cmd_defs[modes.VISUAL_LINE][cmds.G_BIG_J],
        seqs.Y: cmd_defs[modes.VISUAL_LINE][cmds.Y],
        seqs.YY: cmd_defs[modes.VISUAL_LINE][cmds.YY],
        seqs.BIG_S: cmd_defs[modes.VISUAL_LINE][cmds.BIG_S],
        seqs.CTRL_W: cmd_defs[modes.VISUAL_LINE][cmds.CTRL_W],
        seqs.V: cmd_defs[modes.VISUAL_LINE][cmds.V],
        seqs.X: cmd_defs[modes.VISUAL_LINE][cmds.X],
        seqs.W: cmd_defs[modes.VISUAL_LINE][cmds.W],
        seqs.BIG_W: cmd_defs[modes.VISUAL_LINE][cmds.BIG_W],
    },
    modes.SELECT: {
        seqs.I: cmd_defs[modes.SELECT][cmds.I],
        seqs.J: cmd_defs[modes.SELECT][cmds.J],
        seqs.L: cmd_defs[modes.SELECT][cmds.L],
        seqs.K: cmd_defs[modes.SELECT][cmds.K],
    },
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


# matches:
#  <ctrl+p>
#  <Esc>
#  <CR>
#  etc.
# TODO: parse this properly.
_control_key_rx = re.compile(r'<(?:(?:ctrl|alt|altgr|super|shift)(?:\+(?:ctrl|alt|altgr|super|shift)){0,2}\+(?:[Ff][0-9]{1,2}|[Ee][Ss][Cc]|.|[Cc][Rr]>)>|[Sp][Pp][As][Cc][Ee]>|[Ee][Ss][Cc]>|[Cc][Rr]>|[Ff][0-9]{1,2}>)')

def parse_sequence(s):
    """
    Yields simple keys like 'a', 'A', etc. or long key names like <Esc>,
    <ctrl+p>, etc.
    """
    def look_ahead(source, pat):
        return pat.match(source) is not None

    idx = 0
    long_name = ''
    while idx < len(s):
        if ((s[idx] == '<') and look_ahead(s[idx:], _control_key_rx) and
            not long_name):
                long_name = '<'
        elif long_name and (s[idx] == '>'):
            # Special case for <ctrl+>>
            if (len(s) - 1 > idx) and (s[idx + 1] == '>'):
                idx += 1
                long_name += '>'
            yield long_name + '>'
            long_name = ''
        elif long_name:
            long_name += s[idx]
        else:
            yield s[idx]
        idx += 1
