from Vintageous.vi import inputs
from Vintageous.vi.keys import cmds
from Vintageous.vi.keys import cmd_defs
from Vintageous.vi.utils import modes


def vi_j(state, **kwargs):
    cmd = {}

    if state.mode == modes.SELECT:
        cmd['motion'] = '_vi_select_j'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
        return cmd

    cmd['motion'] = '_vi_j'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'xpos': state.xpos}
    return cmd


def vi_k(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_k'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'xpos': state.xpos}
    return cmd


def vi_h(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_h'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_l(state, **kwargs):
    cmd = {}

    if state.mode == modes.SELECT:
        cmd['motion'] = 'find_under_expand_skip'
        cmd['motion_args'] = {}
        return cmd

    cmd['motion'] = '_vi_l'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_t(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_find_in_line'
    cmd['motion_args'] = {'char': state.user_input, 'mode': state.mode,
                          'count': state.count, 'inclusive': False}
    return cmd


def vi_f(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_find_in_line'
    cmd['motion_args'] = {'char': state.user_input, 'mode': state.mode,
                          'count': state.count, 'inclusive': True}
    return cmd


def vi_quote(state, **kwargs):
    if state.user_input == "'":
        return vi_quote_quote(state, **kwargs)

    cmd = {}
    cmd['is_jump'] = True

    cmd['motion'] = '_vi_quote'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'character': state.user_input}
    return cmd


def vi_quote_quote(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_quote_quote'
    cmd['motion_args'] = {} # {'mode': state.mode, 'count': state.count}
    return cmd


def vi_backtick(state, **kwargs):
    cmd = {}
    cmd['is_jump'] = True
    cmd['motion'] = '_vi_backtick'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'character': state.user_input}
    return cmd


def vi_big_t(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_reverse_find_in_line'
    cmd['motion_args'] = {'char': state.user_input, 'mode': state.mode,
                          'count': state.count, 'inclusive': False}
    return cmd


def vi_big_f(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_reverse_find_in_line'
    cmd['motion_args'] = {'char': state.user_input, 'mode': state.mode,
                          'count': state.count, 'inclusive': True}
    return cmd


def vi_semicolon(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_find_in_line' if state.last_character_search_forward else '_vi_reverse_find_in_line'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count,
                          'char': state.last_character_search,
                          'change_direction': False}

    return cmd


def vi_comma(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_find_in_line' if not state.last_character_search_forward else '_vi_reverse_find_in_line'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count,
                          'char': state.last_character_search,
                          'change_direction': False}

    return cmd


def vi_dollar(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_dollar'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_w(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_w'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_W(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_big_w'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_e(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_e'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_0(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_zero'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_slash(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_slash'
    cmd['motion_args'] = {}

    return cmd


def vi_slash_impl(state, **kwargs):
    cmd = {}
    cmd['is_jump'] = True
    cmd['motion'] = '_vi_slash_impl'
    cmd['motion_args'] = {'search_string': state.user_input,
                          'mode': state.mode,
                          'count': state.count}

    return cmd


def vi_question_mark(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_question_mark'
    cmd['motion_args'] = {}
    return cmd


def vi_question_mark_impl(state, **kwargs):
    cmd = {}
    cmd['is_jump'] = True
    cmd['motion'] = '_vi_question_mark_impl'
    cmd['motion_args'] = {'search_string': state.user_input,
                          'mode': state.mode,
                          'count': state.count}
    return cmd


def vi_left_brace(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_left_brace'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_left_square_bracket(state, **kwargs):
    # TODO: Implement this.
    cmd = {}
    cmd['motion'] = '_vi_left_square_bracket'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_right_brace(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_right_brace'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_right_square_bracket(state, **kwargs):
    # TODO: Implement this.
    cmd = {}
    cmd['motion'] = '_vi_right_square_bracket'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_gg(state, **kwargs):
    cmd = {}
    cmd['is_jump'] = True

    if state.action_count or state.motion_count:
        cmd['motion'] = '_vi_go_to_line'
        cmd['motion_args'] = {'line': state.count, 'mode': state.mode}
        return cmd

    cmd['motion'] = '_vi_gg'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_big_g(state, **kwargs):
    cmd = {}
    cmd['is_jump'] = True

    if state.action_count or state.motion_count:
        cmd['motion'] = '_vi_go_to_line'
        cmd['motion_args'] = {'line': state.count, 'mode': state.mode}
    else:
        cmd['motion'] = '_vi_big_g'
        cmd['motion_args'] = {'mode': state.mode}

    return cmd


def vi_percent(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_percent'

    percent = None
    if state.motion_count or state.action_count:
        percent = state.count

    cmd['motion_args'] = {'mode': state.mode, 'percent': percent}

    return cmd


def vi_H(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_big_h'
    cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

    return cmd


def vi_L(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_big_l'
    cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

    return cmd


def vi_M(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_big_m'
    cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

    return cmd


def vi_star(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_star'
    cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

    return cmd


def vi_underscore(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_underscore'
    cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

    return cmd


def vi_hat(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_hat'
    cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

    return cmd


def vi_octothorp(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_octothorp'
    cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

    return cmd


def vi_big_b(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_big_b'
    cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

    return cmd


def vi_g_j(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_g_j'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_g_k(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_g_k'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_g__(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_g__'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_ctrl_u(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_ctrl_u'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_ctrl_d(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_ctrl_d'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_pipe(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_pipe'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_left_paren(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_left_paren'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_right_paren(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_right_paren'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_b(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_b'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_ge(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_ge'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_n(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_n'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'search_string': state.last_buffer_search}

    return cmd


def vi_big_n(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_big_n'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'search_string': state.last_buffer_search}

    return cmd


def vi_big_e(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_big_e'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_ctrl_f(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_ctrl_f'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_ctrl_b(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_ctrl_b'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_enter(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_enter'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_shift_enter(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_shift_enter'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_a_text_object(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_select_text_object'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'text_object': state.user_input, 'inclusive': True}

    return cmd


def vi_i_text_object(state, **kwargs):
    cmd = {}
    cmd['motion'] = '_vi_select_text_object'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'text_object': state.user_input, 'inclusive': False}

    return cmd


# TODO: Make this an action, not a motion.
def vi_k_select(state):
    """
    Non-standard.
    """
    if state.mode != modes.SELECT:
        raise ValueError('bad mode, expected mode_select, got {0}'.format(state.mode))

    cmd = {}
    cmd['motion'] = 'soft_undo'
    cmd['motion_args'] = {} # {'mode': state.mode, 'count': state.count}
    return cmd


def vi_gd(state):
    cmd = {}
    cmd['is_jump'] = True
    cmd['motion'] = '_vi_go_to_symbol'
    cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'globally': False}
    return cmd

