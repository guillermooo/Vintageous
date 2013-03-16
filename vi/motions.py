from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE


# $
def vi_dollar(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    # No count given.
    if vi_cmd_data['count'] == 1:
        vi_cmd_data['motion']['command'] = 'move_to'
        vi_cmd_data['motion']['args'] = {'to': 'eol'}

        # CHARACTERWISE + INCLUSIVE
        # d$
        # TODO: If on hard eol, cancel movement; don't go to the next eol.
        if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
            vi_cmd_data['motion']['args']['extend'] = True
            vi_cmd_data['post_motion'] = [['visual_clip_end_to_eol',],]

        # CHARACTERWISE + INCLUSIVE (includes EOL)
        # vd$
        elif vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['motion']['args']['extend'] = True
            # Prevent $ from jumping to next line's eol.
            # XXX: This is a suboptimal. It will fail if $'ing on an empty line.
            #      Perhaps we need a _visual_dollar_forward command to cover all cases.
            vi_cmd_data['pre_motion'] = ['_back_one_if_on_hard_eol',]
            vi_cmd_data['post_motion'] = [['_extend_b_to_hard_eol',],]

        # LINEWISE + INCLUSIVE
        # Vd$
        elif vi_cmd_data['mode'] == MODE_VISUAL_LINE:
            vi_cmd_data['motion']['args']['extend'] = True
            vi_cmd_data['post_motion'] = [['visual_extend_to_full_line',],]

        # CHARACTERWISE + INCLUSIVE
        # $
        else:
            vi_cmd_data['post_motion'] = [['clip_end_to_line',],]

    # Count given. Move lines downward.
    else:
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True}
        # <count>$ must include the current line, so we subtract one.
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1

        if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
            vi_cmd_data['motion']['args']['extend'] = True
            # LINEWISE
            # 2d$
            #
            # $ behaves differently depending on whether the caret is at BOL (LINEWISE + INCLUSIVE)
            # or not (LINEWISE + EXCLUSIVE). We cannot handle this here, so let an additional
            # command take care of the final deicisions.
            #
            # FIXME: Behavior also depends on whitespace before the caret. Motion becomes
            # linewise in that case.
            #
            # vi_cmd_data['count'] = vi_cmd_data['count'] + 1
            vi_cmd_data['pre_every_motion'] = ['_pre_every_dollar',]
            # vi_cmd_data['post_motion'] = [['_extend_b_to_hard_eol',],]
            # Motion becomes linewise if caret is preceded only by white space.
            # vi_cmd_data['post_motion'].append(['_extend_a_to_bol_if_leading_white_space',])

        # CHARACTERWISE + INCLUSIVE (includes last EOL)
        elif vi_cmd_data['mode'] == MODE_VISUAL:
            # CHARACTERWISE + INCLUSIVE
            # v2$
            #
            vi_cmd_data['motion']['args']['extend'] = True
            vi_cmd_data['post_motion'].append(['_extend_b_to_hard_eol',])
            # Motion becomes linewise if caret is preceded only by white space.
            vi_cmd_data['post_motion'].append(['_extend_a_to_bol_if_leading_white_space',])
        else:
            # LINEWISE + EXCLUSIVE
            # 2$
            vi_cmd_data['post_motion'].append(['move_to', {'to': 'eol'}])
            vi_cmd_data['post_motion'].append(['clip_end_to_line',])

    return vi_cmd_data


def vi_big_g(vi_cmd_data):
    if (vi_cmd_data['count'] > 5) or vi_cmd_data['count'] == 1:
        vi_cmd_data['is_jump'] = True

    # FIXME: Cannot go to line 1. We need to signal when the count is user-provided and when it's
    # a default value.
    if vi_cmd_data['count'] > 1:
        target = vi_cmd_data['count']
        vi_cmd_data['count'] = 1
        vi_cmd_data['motion']['command'] = 'vi_go_to_line'
        vi_cmd_data['motion']['args'] = {'line': target}
    else:
        vi_cmd_data['motion']['command'] = 'move_to'
        vi_cmd_data['motion']['args'] = {'to': 'eof'}

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
    elif vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['args']['extend'] = True
    elif vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['motion']['args']['extend'] = True

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
        vi_cmd_data['motion']['args'] = {'line': target}
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

    else:
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True}
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1

        if vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['pre_motion'] = ['_vi_orient_selections_toward_begin',]
            vi_cmd_data['motion']['args']['extend'] = True

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

    return vi_cmd_data


def vi_l(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_l_motion'
    vi_cmd_data['motion']['args'] = {'count': vi_cmd_data['count'], 'mode': vi_cmd_data['mode']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_h(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_h_motion'
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


def vi_j(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    vi_cmd_data['must_update_xpos'] = False

    vi_cmd_data['motion']['command'] = '_vi_j_motion'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'xpos': vi_cmd_data['xpos']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_k(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    vi_cmd_data['must_update_xpos'] = False

    vi_cmd_data['motion']['command'] = '_vi_k_motion'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'xpos': vi_cmd_data['xpos']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_w(vi_cmd_data):
    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    # XXX There's also a 'clip_to_line' parameter.
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_begin': True, 'punct_begin': True, 'empty_line': True, 'forward': True, 'clip_to_line': True}
    # vi_cmd_data['post_every_motion'] = ['_vi_w_post_every_motion',]

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['pre_every_motion'] = ['_vi_w_pre_every_motion',]
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_every_motion'] = ['_vi_w_post_every_motion',]

    elif vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['last_motion'] = ['_vi_w_last_motion', {'mode': vi_cmd_data['mode']}]
    # In _MODE_INTERNAL_NORMAL, things seem to work as in Vim except for a few corner cases.
    # The two modes are similar enough, but the fact everyhing's working more or less as expected
    # is quite by coincidence.
    # XXX: Add specific code for _MODE_INTERNAL_NORMAL.

    return vi_cmd_data

def vi_b(vi_cmd_data):
    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_begin': True, 'punct_begin': True, 'empty_line': True, 'forward': False}

    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode'],}]
        vi_cmd_data['post_every_motion'] = ['dont_stay_on_eol_backward',]
    elif vi_cmd_data['mode'] == MODE_VISUAL:
        # TODO: Rename to factor in *every*.
        vi_cmd_data['pre_motion'] = ['_vi_visual_orient_selections_toward_begin',]
        vi_cmd_data['motion']['args']['extend'] = True

    return vi_cmd_data


def vi_e(vi_cmd_data):
    # NORMAL mode movement:
    #   ST does what Vim does (TODO: always?).
    #
    # _MODE_INTERNAL_NORMAL
    #
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_end': True, 'punct_end': True, 'empty_line': False, 'forward': True}
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

    return vi_cmd_data


def vi_octothorp(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_octothorp'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_star(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_star'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    return vi_cmd_data


def vi_f(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_t(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_find_in_line_exclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_t(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_reverse_find_in_line_exclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_f(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_reverse_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


# TODO: Unify handling of text objects in one function. Perhaps add state.args to merge with vi_cmd_data['motion']['args']
def vi_inclusive_text_object(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_select_text_object'
    vi_cmd_data['motion']['args'] = {'text_object': vi_cmd_data['user_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'inclusive': True}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


# TODO: Unify handling of text objects in one function. Perhaps add state.args to merge with vi_cmd_data['motion']['args']
def vi_exclusive_text_object(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_select_text_object'
    vi_cmd_data['motion']['args'] = {'text_object': vi_cmd_data['user_input'], 'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'inclusive': False}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_percent(vi_cmd_data):
    vi_cmd_data['is_jump'] = True

    vi_cmd_data['motion']['command'] = 'vi_percent'
    # Make sure we know exactly what the user entered (1% != %) so we can disambiguate in the
    # command.
    vi_cmd_data['motion']['args'] = {'percent': vi_cmd_data['_user_provided_count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_double_single_quote(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_latest_jump'
    vi_cmd_data['motion']['args'] = {}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_forward_slash(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_forward_slash'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'search_string': vi_cmd_data['user_input']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_question_mark(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_question_mark'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'search_string': vi_cmd_data['user_input']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_n(vi_cmd_data):
    vi_cmd_data['motion']['command'] = '_vi_forward_slash'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'search_string': vi_cmd_data['last_buffer_search']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_semicolon(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'character': vi_cmd_data['last_character_search']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_comma(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_reverse_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count'], 'character': vi_cmd_data['last_character_search']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_big_w(vi_cmd_data):
    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_begin': True, 'empty_line': True, 'separators': '', 'forward': True}
    vi_cmd_data['post_every_motion'] = ['_vi_w_post_every_motion',]

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['pre_every_motion'] = ['_vi_w_pre_every_motion',]
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_every_motion'] = ['_vi_w_post_every_motion',]

    # In _MODE_INTERNAL_NORMAL, things seem to work as in Vim except for a few corner cases.
    # The two modes are similar enough, but the fact everyhing's working more or less as expected
    # is quite by coincidence.
    # XXX: Add specific code for _MODE_INTERNAL_NORMAL.

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

    return vi_cmd_data


def vi_big_b(vi_cmd_data):
    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'stops', 'word_begin': True, 'empty_line': True, 'separators': '', 'forward': False}

    if vi_cmd_data['mode'] == MODE_NORMAL:
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode'],}]
        vi_cmd_data['post_every_motion'] = ['dont_stay_on_eol_backward',]
    elif vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode'],}]
        vi_cmd_data['post_every_motion'] = ['dont_stay_on_eol_backward',]
    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['pre_motion'] = ['_vi_visual_orient_selections_toward_begin',]
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode']}]
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_every_motion'] = ['_vi_b_post_every_motion', {'mode': vi_cmd_data['mode']}]

    return vi_cmd_data
