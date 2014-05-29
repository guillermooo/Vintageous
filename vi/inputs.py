from collections import namedtuple

from Vintageous.vi.utils import input_types
from Vintageous.vi import utils


parser_def = namedtuple('parsed_def', 'command interactive_command input_param on_done type')


def get(state, name):
    parser_func = globals().get(name, None)
    if parser_func is None:
        raise ValueError('parser name unknown')
    return parser_func(state)


def one_char(in_):
    """
    Any input (character) satisfies this parser.
    """
    in_ = utils.translate_char(in_)
    return len(in_) == 1


def vi_f(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_big_f(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_big_t(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_t(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


# TODO: rename to "vi_a_text_object".
def vi_inclusive_text_object(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_exclusive_text_object(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_m(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_q(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_at(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_a_text_object(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_i_text_object(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_quote(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_r(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done='_vi_r_on_parser_done',
                   type=input_types.INMEDIATE)
    return p


def vi_backtick(state):
    p = parser_def(command=one_char,
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_left_square_bracket(state):
    p = parser_def(command=lambda x: x in '(){}',
                   interactive_command=None,
                   input_param=None,
                   on_done=None,
                   type=input_types.INMEDIATE)
    return p


def vi_slash(state):
    """
    This parse should always be used non-interactively. / usually collects
    its input from an input panel.
    """
    # Any input is valid; we're never satisfied.
    if state.non_interactive:
        return parser_def(command=lambda x: False,
                          interactive_command='_vi_slash',
                          type=input_types.INMEDIATE,
                          on_done='_vi_slash_on_parser_done',
                          input_param='key')
    else:
        return parser_def(command='_vi_slash',
                          interactive_command='_vi_slash',
                          type=input_types.VIA_PANEL,
                          on_done=None,
                          input_param='default')


def vi_question_mark(state):
    """
    This parser should always be used non-interactively. ? usually collects
    its input from an input panel.
    """
    # Any input is valid; we're never satisfied.
    if state.non_interactive:
        return parser_def(command=lambda x: False,
                          interactive_command='_vi_question_mark',
                          type=input_types.INMEDIATE,
                          on_done='_vi_question_mark_on_parser_done',
                          input_param='key')
    else:
        return parser_def(command='_vi_question_mark',
                          interactive_command='_vi_question_mark',
                          type=input_types.VIA_PANEL,
                          on_done=None,
                          input_param='default')
