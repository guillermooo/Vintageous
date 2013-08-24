"""Motion parsers.

   Motion commands go in Vintageous/motions.py; not here.
"""

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.constants import MODE_VISUAL_BLOCK


# $
def vi_dollar(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    vi_cmd_data['motion']['command'] = '_vi_dollar'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_g(vi_cmd_data):
    if (vi_cmd_data['count'] > 5) or vi_cmd_data['count'] == 1:
        vi_cmd_data['is_jump'] = True

    if vi_cmd_data['_user_provided_count']:
        target = vi_cmd_data['count']
        vi_cmd_data['count'] = 1
        vi_cmd_data['motion']['command'] = 'vi_go_to_line'
        vi_cmd_data['motion']['args'] = {'line': target, 'mode': vi_cmd_data['mode']}
    else:
        vi_cmd_data['motion']['command'] = '_vi_big_g'
        vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_gg(vi_cmd_data):
    if (vi_cmd_data['count'] > 5) or vi_cmd_data['count'] == 1:
        vi_cmd_data['is_jump'] = True

    # FIXME: Cannot go to line 1. We need to signal when the count is user-provided and when it's
    # a default value.
    if vi_cmd_data['count'] > 1:
        target = vi_cmd_data['count']
        vi_cmd_data['count'] = 1
        vi_cmd_data['motion']['command'] = 'vi_go_to_line'
        vi_cmd_data['motion']['args'] = {'line': target, 'mode': vi_cmd_data['mode']}
    else:
        if vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
            vi_cmd_data['motion']['command'] = 'no_op'
            vi_cmd_data['motion']['args'] = {}
        else:
            vi_cmd_data['motion']['command'] = 'move_to'
            vi_cmd_data['motion']['args'] = {'to': 'bof'}
            vi_cmd_data['post_motion'] = [['clip_end_to_line',],]

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
    elif vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['args']['extend'] = True
    elif vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['motion']['args']['extend'] = True

    return vi_cmd_data


def vi_zero(vi_cmd_data):
    if vi_cmd_data['count'] == 1:
        vi_cmd_data['motion']['command'] = 'vi_move_to_hard_bol'
        vi_cmd_data['motion']['args'] = {}

        if vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['pre_motion'] = ['_vi_orient_selections_toward_begin',]
            vi_cmd_data['motion']['args']['extend'] = True
        elif vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
            vi_cmd_data['motion']['args']['extend'] = True

    else:
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True}
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1

        if vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['pre_motion'] = ['_vi_orient_selections_toward_begin',]
            vi_cmd_data['motion']['args']['extend'] = True
        elif vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
            vi_cmd_data['motion']['args']['extend'] = True
        elif vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
            vi_cmd_data['motion']['command'] = 'no_op'
            vi_cmd_data['motion']['args'] = {}

        # TODO: Unify handling of the 'extend' argument. All VISUAL modes need it, so either include
        # it by default at some point, or let each command decide, as we do here.
        vi_cmd_data['post_motion'] = [['move_to_first_non_white_space_char', {'extend': True}],]

    return vi_cmd_data


def vi_underscore(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    if vi_cmd_data['count'] == 1:
        if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
            # TODO: This is sloppy. Make 'motion' a real motion and do away with 'pre_motion'. The
            # problem is that VintageState or VintageRun automatically add 'extend': True
            # to motions, so we cannot simply say 'move_to' 'hardbol' in the motion.
            # Perhaps 'extend' should always be added manually or left unmodified if the current
            # mode was _MODE_INTERNAL_NORMAL. Being explicit with 'extend' looks like the better idea.
            vi_cmd_data['motion']['command'] = 'vi_no_op'
            vi_cmd_data['motion']['args'] = {}
            vi_cmd_data['pre_motion'] = ['move_to', {'to': 'hardbol', 'extend': True}]
            vi_cmd_data['post_motion'] = [['_vi_underscore_post_motion',],]
        elif vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
            vi_cmd_data['motion']['command'] = 'vi_no_op'
            vi_cmd_data['motion']['args'] = {}
        else:
            vi_cmd_data['motion']['command'] = 'move_to'
            vi_cmd_data['pre_motion'] = ['_vi_underscore_pre_motion', {'mode': vi_cmd_data['mode']}]
            vi_cmd_data['motion']['args'] = {'to': 'bol'}
            vi_cmd_data['post_motion'] = [['_vi_underscore_post_motion', {'mode': vi_cmd_data['mode']}],]

        if vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['motion']['args']['extend'] = True

    else:
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True}
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1

        if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
            vi_cmd_data['motion']['command'] = 'move'
            vi_cmd_data['motion']['args'] = {'by': 'lines', 'extend': True, 'forward': True}
            vi_cmd_data['pre_motion'] = ['_vi_underscore_pre_motion', {'mode': vi_cmd_data['mode']}]
            vi_cmd_data['post_motion'] = [['_vi_underscore_post_motion', {'mode': vi_cmd_data['mode']}],]
        elif vi_cmd_data['mode'] == MODE_NORMAL:
            vi_cmd_data['pre_motion'] = ['_vi_underscore_pre_motion', {'mode': vi_cmd_data['mode']}]
            vi_cmd_data['post_motion'] = [['_vi_underscore_post_motion', {'mode': vi_cmd_data['mode']}],]
        elif vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['motion']['args']['extend'] = True
            vi_cmd_data['post_motion'] = [['_vi_underscore_post_motion', {'mode': vi_cmd_data['mode'], 'extend': True}],]
        elif vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
            vi_cmd_data['motion']['command'] = 'vi_no_op'
            vi_cmd_data['motion']['args'] = {}

    return vi_cmd_data


def vi_l(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_l'
    vi_cmd_data['motion']['args'] = {'count': vi_cmd_data['count'], 'mode': vi_cmd_data['mode']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_h(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_h'
    vi_cmd_data['motion']['args'] = {'count': vi_cmd_data['count'], 'mode': vi_cmd_data['mode']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_h(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_big_h'
    # XXX: We subtract one, but vi_cmd_data should know when it's been set to a default value
    # or to an user-supplied one.
    vi_cmd_data['motion']['args'] = {'count': vi_cmd_data['count'] - 1, 'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_big_l(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_big_l'
    # XXX: We subtract one, but vi_cmd_data should know when it's been set to a default value
    # or to an user-supplied one.
    vi_cmd_data['motion']['args'] = {'count': vi_cmd_data['count'] - 1, 'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_big_m(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_big_m'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_g__(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_g__'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_j(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    vi_cmd_data['must_update_xpos'] = False

    vi_cmd_data['motion']['command'] = '_vi_j'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'xpos': vi_cmd_data['xpos']}
    vi_cmd_data['count'] = 1
    # We handle this on our own?
    vi_cmd_data['scroll_into_view'] = True
    vi_cmd_data['scroll_command'] = ['_vi_minimal_scroll',]

    return vi_cmd_data


def vi_k(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    vi_cmd_data['must_update_xpos'] = False

    vi_cmd_data['motion']['command'] = '_vi_k'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'xpos': vi_cmd_data['xpos']}
    vi_cmd_data['count'] = 1
    vi_cmd_data['scroll_into_view'] = True
    # TODO: This could be further simplified; I don't think we need a hook here.
    vi_cmd_data['scroll_command'] = ['_vi_minimal_scroll',]

    return vi_cmd_data


def vi_w(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_w'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_b(vi_cmd_data):
    # FIXME: b is a huge mess. Fix it.
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_begin': True, 'punct_begin': True, 'empty_line': True, 'forward': False}

    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['args']['extend'] = True
    elif vi_cmd_data['mode'] == MODE_VISUAL:
        # TODO: Rename to factor in *every*.
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode'],}]
        vi_cmd_data['post_every_motion'] = ['_vi_b_post_every_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['motion']['args']['extend'] = True
    elif vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
        vi_cmd_data['motion']['command'] = 'vi_no_op'
        vi_cmd_data['motion']['args'] = {}

    return vi_cmd_data


def vi_e(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_e'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_g_e(vi_cmd_data):
    # TODO: Improve this by implementing the whole command in a TextCommand (don't use 'move').
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_end': True, 'punct_end': True, 'empty_line': False, 'forward': False}
    vi_cmd_data['__reorient_caret'] = True

    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_motion'] = ['_vi_e_pre_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['post_every_motion'] = ['_vi_e_post_every_motion', {'mode': vi_cmd_data['mode']}]

    elif vi_cmd_data['mode'] == MODE_NORMAL:
        vi_cmd_data['pre_motion'] = ['_vi_e_pre_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['post_every_motion'] = ['_vi_e_post_every_motion', {'mode': vi_cmd_data['mode']}]

    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_motion'] = ['_vi_g_e_pre_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['post_motion'] = [['_vi_g_e_post_motion', {'mode': vi_cmd_data['mode']}]]

    elif vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
        vi_cmd_data['motion']['command'] = 'vi_no_op'
        vi_cmd_data['motion']['args'] = {}

    return vi_cmd_data


def vi_octothorp(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_octothorp'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_star(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_star'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'exact_word': True}

    return vi_cmd_data


def vi_f(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_motion_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_t(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_find_in_line_exclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_motion_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_t(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_reverse_find_in_line_exclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_motion_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_f(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_reverse_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_motion_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


# TODO: Unify handling of text objects in one function. Perhaps add state.args to merge with vi_cmd_data['motion']['args']
def vi_inclusive_text_object(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_select_text_object'
    vi_cmd_data['motion']['args'] = {'text_object': vi_cmd_data['user_motion_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'inclusive': True}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


# TODO: Unify handling of text objects in one function. Perhaps add state.args to merge with vi_cmd_data['motion']['args']
def vi_exclusive_text_object(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_select_text_object'
    vi_cmd_data['motion']['args'] = {'text_object': vi_cmd_data['user_motion_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'inclusive': False}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_percent(vi_cmd_data):
    vi_cmd_data['is_jump'] = True

    vi_cmd_data['motion']['command'] = 'vi_percent'
    # Make sure we know exactly what the user entered (1% != %) so we can disambiguate in the
    # command.
    vi_cmd_data['motion']['args'] = {'percent': vi_cmd_data['_user_provided_count'], 'mode': vi_cmd_data['mode']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_double_single_quote(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_double_single_quote'
    vi_cmd_data['motion']['args'] = {}
    vi_cmd_data['count'] = 1
    vi_cmd_data['creates_jump_at_current_position'] = True

    return vi_cmd_data


def vi_forward_slash(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_forward_slash'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'search_string': vi_cmd_data['user_motion_input']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_question_mark(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_question_mark'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'search_string': vi_cmd_data['user_motion_input']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_n(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_forward_slash'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'search_string': vi_cmd_data['last_buffer_search']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data

def vi_big_n(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_question_mark'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'search_string': vi_cmd_data['last_buffer_search']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_semicolon(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_find_in_line_inclusive' if vi_cmd_data['last_character_search_forward'] else 'vi_reverse_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'character': vi_cmd_data['last_character_search'], 'change_direction': False}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_comma(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_reverse_find_in_line_inclusive' if vi_cmd_data['last_character_search_forward'] else 'vi_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'character': vi_cmd_data['last_character_search'], 'change_direction': False}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_w(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_big_w'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_e(vi_cmd_data):
    # NORMAL mode movement:
    #   ST does what Vim does (TODO: always?).
    #
    # _MODE_INTERNAL_NORMAL
    #
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_end': True, 'empty_line': True, 'separators': '', 'forward': True}
    vi_cmd_data['__reorient_caret'] = True

    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_motion'] = ['_vi_e_pre_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['post_every_motion'] = ['_vi_e_post_every_motion', {'mode': vi_cmd_data['mode']}]

    elif vi_cmd_data['mode'] == MODE_NORMAL:
        vi_cmd_data['pre_motion'] = ['_vi_e_pre_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['post_every_motion'] = ['_vi_e_post_every_motion', {'mode': vi_cmd_data['mode']}]

    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_motion'] = ['_vi_e_pre_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['post_every_motion'] = ['_vi_e_post_every_motion', {'mode': vi_cmd_data['mode']}]

    elif vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
        vi_cmd_data['motion']['command'] = 'vi_no_op'
        vi_cmd_data['motion']['args'] = {}

    return vi_cmd_data


def vi_big_b(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_begin': True, 'empty_line': True, 'separators': '', 'forward': False}

    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode'],}]
        vi_cmd_data['post_every_motion'] = ['dont_stay_on_eol_backward',]
    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['pre_motion'] = ['_vi_b_pre_motion',]
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_every_motion'] = ['_vi_b_post_every_motion', {'mode': vi_cmd_data['mode']}]

    elif vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
        vi_cmd_data['motion']['command'] = 'vi_no_op'
        vi_cmd_data['motion']['args'] = {}

    return vi_cmd_data


def vi_right_brace(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_right_brace'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_left_brace(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_left_brace'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_right_parenthesis(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_right_parenthesis'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_left_parenthesis(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_left_parenthesis'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_g_d(vi_cmd_data):
    vi_cmd_data['is_jump'] = True
    vi_cmd_data['motion']['command'] = '_vi_go_to_symbol'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_g_big_d(vi_cmd_data):
    vi_cmd_data['is_jump'] = True
    vi_cmd_data['motion']['command'] = '_vi_go_to_symbol'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'globally': True}

    return vi_cmd_data


def vi_quote(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_quote'
    vi_cmd_data['motion']['args'] = {'character': vi_cmd_data['user_motion_input'], 'mode': vi_cmd_data['mode']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_ctrl_f(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'pages', 'forward': True}

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
    elif vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_motion'] = [['visual_extend_to_full_line',]]
    elif vi_cmd_data['mode'] != MODE_NORMAL:
        # TODO: Sublime Text seems to ignore the 'extend' param to Ctrl+f, so disable it.
        # vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['motion']['command'] = 'vi_no_op'
        vi_cmd_data['motion']['args'] = {}
    elif vi_cmd_data['mode'] == MODE_VISUAL_BLOCK:
        vi_cmd_data['motion']['command'] = 'vi_no_op'
        vi_cmd_data['motion']['args'] = {}

    return vi_cmd_data

def vi_ctrl_b(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'pages', 'forward': False}

    if vi_cmd_data['mode'] != MODE_NORMAL:
        # TODO: Sublime Text seems to ignore the 'extend' param to Ctrl+b, so disable it.
        # vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['motion']['command'] = 'vi_no_op'
        vi_cmd_data['motion']['args'] = {}

    return vi_cmd_data


def vi_g_star(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_star'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'exact_word': False}

    return vi_cmd_data


def vi_g_octothorp(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_octothorp'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'exact_word': False}

    return vi_cmd_data

def vi_enter(vi_cmd_data):
    # TODO: Improve post_motion: should leave caret at first non-white space char.
    vi_cmd_data['motion']['command'] = '_vi_j'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': 1, 'xpos': 0}
    vi_cmd_data['post_action'] = ['_vi_move_caret_to_first_non_white_space_character', {'mode': vi_cmd_data['mode']}]

    if vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': 1, 'xpos': vi_cmd_data['xpos']}

    return vi_cmd_data


def vi_shift_enter(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_k'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': 1, 'xpos': 0}
    vi_cmd_data['post_motion'] = [['_vi_shift_enter_post_motion', {'mode': vi_cmd_data['mode']}]]

    if vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': 1, 'xpos': vi_cmd_data['xpos']}
        vi_cmd_data['post_motion'] = None

    return vi_cmd_data


def vi_pipe(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_pipe'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_ctrl_d(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_ctrl_d'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_ctrl_u(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_ctrl_u'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


# We have this one duplicated in actions.py because vi_g_action (like in gg or gU) can sometimes
# be an action, and other times a motion.
def vi_g_action(vi_cmd_data):
    """This doesn't do anything by itself, but tells global state to wait for a second action that
       completes this one.
    """
    vi_cmd_data['motion_required'] = True
    # Let global state know we still need a second action to complete this one.
    vi_cmd_data['is_digraph_start'] = True
    vi_cmd_data['action']['command'] = 'no_op'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data
