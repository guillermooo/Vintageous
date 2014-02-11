from Vintageous.vi.utils import input_types
from Vintageous.vi import utils


def get(state, name):
    parser_func = globals().get(name, None)
    if parser_func is None:
        raise ValueError('parser name unknown')
    return parser_func(state)


def default(in_):
    """
    Any input (character) satisfies this parser.
    """
    in_ = utils.translate_char(in_)
    return len(in_) == 1


def vi_f(state):
    return (default, input_types.INMEDIATE, None)


def vi_big_f(state):
    return (default, input_types.INMEDIATE, None)


def vi_big_t(state):
    return (default, input_types.INMEDIATE, None)


def vi_t(state):
    return (default, input_types.INMEDIATE, None)


# TODO: rename to "vi_a_text_object".
def vi_inclusive_text_object(state):
    return (default, input_types.INMEDIATE, None)


def vi_exclusive_text_object(state):
    return (default, input_types.INMEDIATE, None)


def vi_m(state):
    return (default, input_types.INMEDIATE, None)


def vi_r(state):
    return (default, input_types.INMEDIATE, None)


def vi_q(state):
    return (default, input_types.INMEDIATE, None)


def vi_at(state):
    return (default, input_types.INMEDIATE, None)


def vi_a_text_object(state):
    return (default, input_types.INMEDIATE, None)


def vi_i_text_object(state):
    return (default, input_types.INMEDIATE, None)


def vi_quote(state):
    return (default, input_types.INMEDIATE, None)


def vi_r(state):
    return (default, input_types.INMEDIATE, '_vi_r_on_parser_done')


def vi_backtick(state):
    return (default, input_types.INMEDIATE, None)


def vi_slash(state):
    """
    This parse should always be used non-interactively. / usually collects
    its input from an input panel.
    """
    # Any input is valid; we're never satisfied.
    if state.non_interactive:
        return (lambda x: False, input_types.INMEDIATE, '_vi_slash_on_parser_done')
    else:
        return ('_vi_slash', input_types.VIA_PANEL, None)


def vi_question_mark(state):
    """
    This parser should always be used non-interactively. ? usually collects
    its input from an input panel.
    """
    # Any input is valid; we're never satisfied.

    if state.non_interactive:
        return (lambda x: False, input_types.INMEDIATE, '_vi_question_mark_on_parser_done')
    else:
        return ('_vi_question_mark', input_types.VIA_PANEL, None)
