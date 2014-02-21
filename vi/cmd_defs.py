from Vintageous.vi.utils import modes


class cmd_types:
    """
    Types of command.
    """
    MOTION = 1
    ACTION = 2
    ANY =    3
    OTHER =  4
    USER =   5


class cmds:
    """
    Vim commands' names. They help locate a function that returns
    configuration data for the command based on mode, etc. These functions
    can be found in `vi/motions.py` and `vi/actions.py`.
    """

    A =                            'vi_a'
    A_TEXT_OBJECT =                'vi_a_text_object'
    AMPERSAND =                    'vi_ampersand'
    AT =                           'vi_at'
    B =                            'vi_b'
    BACKTICK =                     'vi_backtick'
    C =                            'vi_c'
    CC =                           'vi_cc'
    COLON =                        'vi_colon'
    COMMA =                        'vi_comma'
    D =                            'vi_d'
    DD =                           'vi_dd'
    DOLLAR =                       'vi_dollar'
    DOT =                          'vi_dot'
    DOUBLE_QUOTE =                 'vi_double_quote'
    E =                            'vi_e'
    EN_DASH =                      'vi_en_dash'
    ENTER =                        'vi_enter'
    EQUAL =                        'vi_equal'
    EQUAL_EQUAL =                  'vi_equal_equal'
    ESC =                          'vi_esc'
    EXCLAMATION =                  'vi_exclamation'
    F =                            'vi_f'
    G =                            'vi_g'
    G_BIG_D =                      'vi_g_big_d'
    G_BIG_J =                      'vi_g_big_j'
    G_BIG_T =                      'vi_g_big_t'
    G_BIG_U =                      'vi_gU'
    G_BIG_U_BIG_U =                'vi_g_big_u_big_u'
    G_BIG_U_G_BIG_U =              'vi_g_big_u_g_big_u'
    G_TILDE =                      'vi_g_tilde'
    G_TILDE_G_TILDE =              'vi_g_tilde_g_tilde'
    G_TILDE_TILDE =                'vi_g_tilde_tilde'
    G_UNDERSCORE =                 'vi_g__'
    GD =                           'vi_gd'
    GE =                           'vi_ge'
    GG =                           'vi_gg'
    GH =                           'vi_gh'
    GJ =                           'vi_g_j'
    GK =                           'vi_g_k'
    GQ =                           'vi_gq'
    GREATER_THAN =                 'vi_greater_than'
    GREATER_THAN =                 'vi_greater_than'
    GREATER_THAN_GREATER_THAN =    'vi_greater_than_greater_than'
    GT =                           'vi_gt'
    GU =                           'vi_gu'
    GUGU =                         'vi_gugu'
    GUU =                          'vi_guu'
    GV =                           'vi_gv'
    H =                            'vi_h'
    HAT =                          'vi_hat'
    I =                            'vi_i'
    I_TEXT_OBJECT =                'vi_i_text_object'
    J =                            'vi_j'
    K =                            'vi_k'
    K_SELECT =                     'vi_k_select'
    L =                            'vi_l'
    LEFT_BRACE =                   'vi_left_brace'
    LEFT_SQUARE_BRACKET =          'vi_left_square_bracket'
    LEFT_CURLY_BRACE =             'vi_left_curly_brace'
    LEFT_PAREN =                   'vi_left_paren'
    LESS_THAN =                    'vi_less_than'
    LESS_THAN_LESS_THAN =          'vi_less_than_less_than'
    M =                            'vi_m'
    N =                            'vi_n'
    O =                            'vi_o'
    OCTOTHORP =                    'vi_octothorp'
    P =                            'vi_p'
    PERCENT =                      'vi_percent'
    PIPE =                         'vi_pipe'
    PLUS =                         'vi_plus'
    Q =                            'vi_q'
    QUESTION_MARK =                'vi_question_mark'
    QUESTION_MARK_IMPL =           'vi_question_mark_impl'
    QUOTE =                        'vi_quote'
    QUOTE_QUOTE =                  'vi_quote_quote'
    R =                            'vi_r'
    RIGHT_BRACE =                  'vi_right_brace'
    RIGHT_SQUARE_BRACKET =         'vi_right_square_bracket'
    RIGHT_PAREN =                  'vi_right_paren'
    RIGHT_PAREN =                  'vi_right_paren'
    S =                            'vi_s'
    SEMICOLON =                    'vi_semicolon'
    SLASH =                        'vi_slash'
    SLASH_IMPL =                   'vi_slash_impl'
    SPACE =                        'vi_space'
    STAR =                         'vi_star'
    T =                            'vi_t'
    TILDE =                        'vi_tilde'
    U =                            'vi_u'
    UNDERSCORE =                   'vi_underscore'
    V =                            'vi_v'
    W =                            'vi_w'
    X =                            'vi_x'
    Y =                            'vi_y'
    YY =                           'vi_yy'
    Z =                            'open_name_space'
    Z_ENTER =                      'vi_z_enter'
    Z_MINUS =                      'vi_z_minus'
    ZB =                           'vi_zb'
    ZERO =                         'vi_0'
    ZT =                           'vi_zt'
    ZZ =                           'vi_zz'

    # Upper case

    BIG_A =                        'vi_big_a'
    BIG_B =                        'vi_big_b'
    BIG_C =                        'vi_big_c'
    BIG_D =                        'vi_big_d'
    BIG_E =                        'vi_big_e'
    BIG_F =                        'vi_big_f'
    BIG_G =                        'vi_big_g'
    BIG_H =                        'vi_H'
    BIG_I =                        'vi_big_i'
    BIG_J =                        'vi_big_j'
    BIG_J =                        'vi_big_j'
    BIG_K =                        'vi_big_k'
    BIG_L =                        'vi_L'
    BIG_M =                        'vi_M'
    BIG_N =                        'vi_big_n'
    BIG_O =                        'vi_big_o'
    BIG_P =                        'vi_big_p'
    BIG_Q =                        'vi_big_q'
    BIG_R =                        'vi_big_r'
    BIG_S =                        'vi_big_s'
    BIG_T =                        'vi_big_t'
    BIG_U =                        'vi_big_u'
    BIG_V =                        'vi_big_v'
    BIG_W =                        'vi_W'
    BIG_X =                        'vi_big_x'
    BIG_Y =                        'vi_big_y'
    BIG_Z =                        'vi_Z'
    BIG_Z_BIG_Q =                  'vi_big_z_big_q'
    BIG_Z_BIG_Z =                  'vi_big_z_big_z'

    # Shift- commands

    SHIFT_ENTER =                  'vi_shift_enter'
    SHIFT_ENTER =                  'vi_shift_enter'
    SHIFT_F3 =                     'vi_shift_f3'
    SHIFT_F4 =                     'vi_shift_f4'

    # Ctrl+Shift- commands

    SHIFT_CTRL_F12 =               'vi_shift_ctrl_f12'

    # Ctrl- commands

    CTRL_A =                       'vi_ctrl_a'
    CTRL_B =                       'vi_ctrl_b'
    CTRL_BIG_F =                   'vi_ctrl_big_f'
    CTRL_BIG_P =                   'vi_ctrl_big_p'
    CTRL_D =                       'vi_ctrl_d'
    CTRL_E =                       'vi_ctrl_e'
    CTRL_F =                       'vi_ctrl_f'
    CTRL_G =                       'vi_ctrl_g'
    CTRL_F11 =                     'vi_ctrl_f11'
    CTRL_F12 =                     'vi_ctrl_f12'
    CTRL_K =                       'vi_ctrl_k'
    CTRL_K_CTRL_B =                'vi_ctrl_k_ctrl_b'
    CTRL_L =                       'vi_ctrl_l'
    CTRL_P =                       'vi_ctrl_p'
    CTRL_R =                       'vi_ctrl_r'
    CTRL_R_EQUAL =                 'vi_ctrl_r_equal'
    CTRL_U =                       'vi_ctrl_u'
    CTRL_V =                       'vi_ctrl_v'
    CTRL_W =                       'open_name_space'
    CTRL_W_BIG_H =                 'vi_ctrl_w_big_h'
    CTRL_W_BIG_L =                 'vi_ctrl_w_big_l'
    CTRL_W_H =                     'vi_ctrl_w_h'
    CTRL_W_L =                     'vi_ctrl_w_l'
    CTRL_W_Q =                     'vi_ctrl_w_q'
    CTRL_W_V =                     'vi_ctrl_w_v'
    CTRL_X =                       'vi_ctrl_x'
    CTRL_Y =                       'vi_ctrl_y'

    # Alt-Ctrl- commands

    ALT_CTRL_P = 'vi_ctrl_alt_p'

    # Function keys

    F1 =                           'vi_f1'
    F2 =                           'vi_f2'
    F3 =                           'vi_f3'
    F4 =                           'vi_f4'
    F5 =                           'vi_f5'
    F6 =                           'vi_f6'
    F7 =                           'vi_f7'
    F8 =                           'vi_f8'
    F9 =                           'vi_f9'
    F10 =                          'vi_f10'
    F11 =                          'vi_f11'
    F12 =                          'vi_f12'
    F12 =                          'vi_f12'
    F13 =                          'vi_f13'
    F14 =                          'vi_f14'
    F15 =                          'vi_f15'

    # Special commands

    MISSING =                      '_missing'
    OPEN_NAME_SPACE =              'open_name_space'
    OPEN_REGISTERS =               'open_registers'


# Mappings 'command name' ==> 'command definition'
#
# 'command name' is one of `cmds`. 'command definition' is the minimum data
# needed by `State` to know what to do with the command.
#
# During the lifecycle of a command, configuration data may be gathered from
# other parts.
#
# Any requested command that can't be found here should report back as a
# 'missing command'.
cmd_defs = {
    modes.NORMAL: {
        cmds.B:                         dict(name=cmds.B,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BACKTICK:                  dict(name=cmds.BACKTICK,                    input='vi_backtick',        type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_B:                     dict(name=cmds.BIG_B,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_E:                     dict(name=cmds.BIG_E,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_F:                     dict(name=cmds.BIG_F,                       input='vi_big_f',           type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_G:                     dict(name=cmds.BIG_G,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_H:                     dict(name=cmds.BIG_H,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.BIG_L:                     dict(name=cmds.BIG_L,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.BIG_M:                     dict(name=cmds.BIG_M,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.BIG_N:                     dict(name=cmds.BIG_N,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_T:                     dict(name=cmds.BIG_T,                       input='vi_big_t',           type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.BIG_W:                     dict(name=cmds.BIG_W,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.COMMA:                     dict(name=cmds.COMMA,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.CTRL_B:                    dict(name=cmds.CTRL_B,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.CTRL_D:                    dict(name=cmds.CTRL_D,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.CTRL_F:                    dict(name=cmds.CTRL_F,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.CTRL_U:                    dict(name=cmds.CTRL_U,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.DOLLAR:                    dict(name=cmds.DOLLAR,                      input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.E:                         dict(name=cmds.E,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.ENTER:                     dict(name=cmds.ENTER,                       input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.F:                         dict(name=cmds.F,                           input='vi_f',               type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.G_UNDERSCORE:              dict(name=cmds.G_UNDERSCORE,                input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.GD:                        dict(name=cmds.GD,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.GE:                        dict(name=cmds.GE,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.GG:                        dict(name=cmds.GG,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.GJ:                        dict(name=cmds.GJ,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.GK:                        dict(name=cmds.GK,                          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.H:                         dict(name=cmds.H,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.HAT:                       dict(name=cmds.HAT,                         input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.J:                         dict(name=cmds.J,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.K:                         dict(name=cmds.K,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.L:                         dict(name=cmds.L,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.LEFT_BRACE:                dict(name=cmds.LEFT_BRACE,                  input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.LEFT_PAREN:                dict(name=cmds.LEFT_PAREN,                  input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.LEFT_SQUARE_BRACKET:       dict(name=cmds.LEFT_SQUARE_BRACKET,         input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.N:                         dict(name=cmds.N,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.OCTOTHORP:                 dict(name=cmds.OCTOTHORP,                   input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.PERCENT:                   dict(name=cmds.PERCENT,                     input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.PIPE:                      dict(name=cmds.PIPE,                        input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.QUESTION_MARK:             dict(name=cmds.QUESTION_MARK,               input='vi_question_mark',   type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.QUOTE:                     dict(name=cmds.QUOTE,                       input='vi_quote',           type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.RIGHT_BRACE:               dict(name=cmds.RIGHT_BRACE,                 input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.RIGHT_PAREN:               dict(name=cmds.RIGHT_PAREN,                 input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.RIGHT_SQUARE_BRACKET:      dict(name=cmds.RIGHT_SQUARE_BRACKET,        input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.SEMICOLON:                 dict(name=cmds.SEMICOLON,                   input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.SHIFT_ENTER:               dict(name=cmds.SHIFT_ENTER,                 input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=False, scroll_into_view=True),
        cmds.SPACE:                     dict(name=cmds.L,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.STAR:                      dict(name=cmds.STAR,                        input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.T:                         dict(name=cmds.T,                           input='vi_t',               type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.UNDERSCORE:                dict(name=cmds.UNDERSCORE,                  input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.W:                         dict(name=cmds.W,                           input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.ZERO:                      dict(name=cmds.ZERO,                        input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),

        cmds.QUESTION_MARK:             dict(name=cmds.QUESTION_MARK,               input='vi_question_mark',   type=cmd_types.MOTION, multi_step=True, updates_xpos=True, scroll_into_view=True),
        cmds.QUESTION_MARK_IMPL:        dict(name=cmds.QUESTION_MARK_IMPL,          input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),
        cmds.SLASH:                     dict(name=cmds.SLASH,                       input='vi_slash',           type=cmd_types.MOTION, multi_step=True, updates_xpos=True, scroll_into_view=True),
        cmds.SLASH_IMPL:                dict(name=cmds.SLASH_IMPL,                  input=None,                 type=cmd_types.MOTION, multi_step=False, updates_xpos=True, scroll_into_view=True),

        cmds.BIG_J:                     dict(name=cmds.BIG_J,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.G_BIG_J:                   dict(name=cmds.G_BIG_J,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.GV:                        dict(name=cmds.GV,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.BIG_C:                     dict(name=cmds.BIG_C,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.BIG_D:                     dict(name=cmds.BIG_D,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.C:                         dict(name=cmds.C,                           input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.CTRL_G:                    dict(name=cmds.CTRL_G,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=True, repeatable=False),
        cmds.CTRL_V:                    dict(name=cmds.CTRL_V,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=True, repeatable=False),
        cmds.D:                         dict(name=cmds.D,                           input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.EQUAL:                     dict(name=cmds.EQUAL,                       input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=True, repeatable=True),
        cmds.G_BIG_U:                   dict(name=cmds.G_BIG_U,                     input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.G_BIG_U_BIG_U:             dict(name=cmds.G_BIG_U_BIG_U,               input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.G_BIG_U_G_BIG_U:           dict(name=cmds.G_BIG_U_G_BIG_U,             input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.G_TILDE:                   dict(name=cmds.G_TILDE,                     input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.GREATER_THAN:              dict(name=cmds.GREATER_THAN,                input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=True, repeatable=True),
        cmds.GU:                        dict(name=cmds.GU,                          input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.GUGU:                       dict(name=cmds.GUU,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.GUU:                       dict(name=cmds.GUU,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.LESS_THAN:                 dict(name=cmds.LESS_THAN,                   input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=True, repeatable=True),
        cmds.M:                         dict(name=cmds.M,                           input='vi_m',               type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.R:                         dict(name=cmds.R,                           input='vi_r',               type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.S:                         dict(name=cmds.S,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.TILDE:                     dict(name=cmds.TILDE,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.Y:                         dict(name=cmds.Y,                           input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=False),

        cmds.BIG_Y:                     dict(name=cmds.BIG_Y,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_Z_BIG_Q:               dict(name=cmds.BIG_Z_BIG_Q,                 input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_Z_BIG_Z:               dict(name=cmds.BIG_Z_BIG_Z,                 input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_R:                    dict(name=cmds.CTRL_R,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.DD:                        dict(name=cmds.DD,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),

        cmds.AT:                         dict(name=cmds.AT,                         input='vi_at',              type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_O:                     dict(name=cmds.BIG_O,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.BIG_P:                     dict(name=cmds.BIG_P,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.BIG_X:                     dict(name=cmds.BIG_X,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.GH:                        dict(name=cmds.GH,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.O:                         dict(name=cmds.O,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.P:                         dict(name=cmds.P,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.Q:                         dict(name=cmds.Q,                           input='vi_q',               type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.BIG_S:                     dict(name=cmds.BIG_S,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.CC:                        dict(name=cmds.CC,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.EQUAL_EQUAL:               dict(name=cmds.EQUAL_EQUAL,                 input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.G_TILDE_G_TILDE:           dict(name=cmds.G_TILDE_G_TILDE,             input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.G_TILDE_TILDE:             dict(name=cmds.G_TILDE_G_TILDE,             input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.GREATER_THAN_GREATER_THAN: dict(name=cmds.GREATER_THAN_GREATER_THAN,   input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),

        cmds.G_BIG_T:                   dict(name=cmds.G_BIG_T,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.GQ:                        dict(name=cmds.GQ,                          input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),
        cmds.GT:                        dict(name=cmds.GT,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.GU:                        dict(name=cmds.GU,                          input=None,                 type=cmd_types.ACTION, motion_required=True, multi_step=False, repeatable=True),

        cmds.CTRL_W_BIG_H:              dict(name=cmds.CTRL_W_BIG_H,                input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_BIG_L:              dict(name=cmds.CTRL_W_BIG_L,                input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_H:                  dict(name=cmds.CTRL_W_H,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_L:                  dict(name=cmds.CTRL_W_L,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_Q:                  dict(name=cmds.CTRL_W_Q,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W_V:                  dict(name=cmds.CTRL_W_V,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.Z_ENTER:                   dict(name=cmds.Z_ENTER,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.Z_MINUS:                   dict(name=cmds.Z_MINUS,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.ZB:                        dict(name=cmds.ZB,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.ZT:                        dict(name=cmds.ZT,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.ZZ:                        dict(name=cmds.ZZ,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.CTRL_A:                    dict(name=cmds.CTRL_A,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.CTRL_R_EQUAL:              dict(name=cmds.CTRL_R_EQUAL,                input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_X:                    dict(name=cmds.CTRL_X,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),

        cmds.A:                         dict(name=cmds.A,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_A:                     dict(name=cmds.BIG_A,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_I:                     dict(name=cmds.BIG_I,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_R:                     dict(name=cmds.BIG_R,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_U:                     dict(name=cmds.BIG_U,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.BIG_V:                     dict(name=cmds.BIG_V,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_E:                    dict(name=cmds.CTRL_E,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_Y:                    dict(name=cmds.CTRL_Y,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.DOT:                       dict(name=cmds.DOT,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.G_BIG_D:                   dict(name=cmds.G_BIG_D,                     input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.I:                         dict(name=cmds.I,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.LESS_THAN_LESS_THAN:       dict(name=cmds.LESS_THAN_LESS_THAN,         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.QUOTE_QUOTE:               dict(name=cmds.QUOTE_QUOTE,                 input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.S:                         dict(name=cmds.S,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.U:                         dict(name=cmds.U,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.V:                         dict(name=cmds.V,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.X:                         dict(name=cmds.X,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.X:                         dict(name=cmds.X,                           input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=True),
        cmds.YY:                        dict(name=cmds.YY,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        cmds.COLON:                     dict(name=cmds.COLON,                       input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.ESC:                       dict(name=cmds.ESC,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),

        # Enable some Sublime Text key bindings.
        cmds.ALT_CTRL_P:                dict(name=cmds.ALT_CTRL_P,                  input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.BIG_Z:                     dict(name=cmds.OPEN_NAME_SPACE,             input=None,                 type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_BIG_F:                dict(name=cmds.CTRL_BIG_F,                  input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_BIG_P:                dict(name=cmds.CTRL_BIG_P,                  input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_F12:                  dict(name=cmds.CTRL_F12,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_K:                     dict(name=cmds.OPEN_NAME_SPACE,             input=None,                 type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_K_CTRL_B:             dict(name=cmds.CTRL_K_CTRL_B,               input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_P:                    dict(name=cmds.CTRL_P,                      input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.CTRL_W:                    dict(name=cmds.OPEN_NAME_SPACE,             input=None,                 type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.DOUBLE_QUOTE:              dict(name=cmds.OPEN_REGISTERS,              input=None,                 type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.F11:                       dict(name=cmds.F11,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.F12:                       dict(name=cmds.F12,                         input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.F3:                        dict(name=cmds.F3,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.F4:                        dict(name=cmds.F4,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.F7:                        dict(name=cmds.F7,                          input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.G:                         dict(name=cmds.OPEN_NAME_SPACE,             input=None,                 type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),
        cmds.SHIFT_CTRL_F12:            dict(name=cmds.SHIFT_CTRL_F12,              input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.SHIFT_F3:                  dict(name=cmds.SHIFT_F3,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.SHIFT_F4:                  dict(name=cmds.SHIFT_F4,                    input=None,                 type=cmd_types.ACTION, motion_required=False, multi_step=False, repeatable=False),
        cmds.Z:                         dict(name=cmds.OPEN_NAME_SPACE,             input=None,                 type=cmd_types.OTHER, motion_required=False, multi_step=False, repeatable=False),

        cmds.MISSING:                   dict(name=cmds.MISSING,                     input=None,                 type=cmd_types.ANY, motion_required=False, multi_step=False)
    }
}

cmd_defs[modes.OPERATOR_PENDING] = cmd_defs[modes.NORMAL].copy()
cmd_defs[modes.OPERATOR_PENDING][cmds.A] =    dict(name=cmds.A_TEXT_OBJECT,         input='vi_i_text_object',   type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.OPERATOR_PENDING][cmds.I] =    dict(name=cmds.I_TEXT_OBJECT,         input='vi_a_text_object',   type=cmd_types.MOTION, multi_step=False)

cmd_defs[modes.VISUAL] = cmd_defs[modes.NORMAL].copy()
cmd_defs[modes.VISUAL][cmds.A] =              dict(name=cmds.A_TEXT_OBJECT,         input='vi_a_text_object',   type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.VISUAL][cmds.BIG_O] =          dict(name=cmds.O,                     input=None,                 type=cmd_types.ACTION, multi_step=False, motion_required=False, repeatable=False)
cmd_defs[modes.VISUAL][cmds.I] =              dict(name=cmds.I_TEXT_OBJECT,         input='vi_a_text_object',   type=cmd_types.MOTION, multi_step=False)

cmd_defs[modes.VISUAL_LINE] = cmd_defs[modes.NORMAL].copy()
cmd_defs[modes.VISUAL_LINE][cmds.BIG_O] =     dict(name=cmds.O,                     input=None,                 type=cmd_types.ACTION, multi_step=False, motion_required=False, repeatable=False)

cmd_defs[modes.VISUAL_BLOCK] = cmd_defs[modes.NORMAL].copy()

cmd_defs[modes.SELECT] = {}
cmd_defs[modes.SELECT][cmds.BIG_A] =    dict(name=cmds.BIG_A,       input=None, type=cmd_types.ACTION, multi_step=False, motion_required=False, repeatable=False)
cmd_defs[modes.SELECT][cmds.BIG_J] =    dict(name=cmds.BIG_J,       input=None, type=cmd_types.ACTION, multi_step=False, motion_required=False, repeatable=False)
cmd_defs[modes.SELECT][cmds.I] =        dict(name=cmds.I,           input=None, type=cmd_types.ACTION, multi_step=False, motion_required=False, repeatable=False)
cmd_defs[modes.SELECT][cmds.J] =        dict(name=cmds.J,           input=None, type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.SELECT][cmds.K] =        dict(name=cmds.K_SELECT,    input=None, type=cmd_types.MOTION, multi_step=False)
cmd_defs[modes.SELECT][cmds.L] =        dict(name=cmds.L,           input=None, type=cmd_types.MOTION, multi_step=False)
