from Vintageous.vi.constants import (MODE_NORMAL, MODE_VISUAL, MODE_VISUAL_LINE,
                          _MODE_INTERNAL_VISUAL)


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
        if vi_cmd_data['_internal_mode'] == _MODE_INTERNAL_VISUAL:
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

        if vi_cmd_data['_internal_mode'] == _MODE_INTERNAL_VISUAL:
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
    elif vi_cmd_data['_internal_mode'] == _MODE_INTERNAL_VISUAL:
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
    elif vi_cmd_data['_internal_mode'] == _MODE_INTERNAL_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
    elif vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['motion']['args']['extend'] = True

    return vi_cmd_data


def vi_zero(vi_cmd_data):
    if vi_cmd_data['count'] == 1:
        vi_cmd_data['motion']['command'] = 'vi_move_to_hard_bol'
        vi_cmd_data['motion']['args'] = {}

        if vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['motion']['args']['extend'] = True

    else:
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True}
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1

        if vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['motion']['args']['extend'] = True

        vi_cmd_data['post_motion'] = [['move_to_first_non_white_space_char', {'extend': True}],]

    return vi_cmd_data


def vi_underscore(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    if vi_cmd_data['count'] == 1:
        vi_cmd_data['motion']['command'] = 'move_to'
        vi_cmd_data['motion']['args'] = {'to': 'bol'}

        if vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['motion']['args']['extend'] = True

    else:
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True}
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1

        if vi_cmd_data['mode'] == MODE_NORMAL:
            vi_cmd_data['pre_motion'] = ['_vi_underscore_pre_motion', {'mode': vi_cmd_data['mode']}]
            vi_cmd_data['post_motion'] = [['_vi_underscore_post_motion', {'mode': vi_cmd_data['mode']}],]
        elif vi_cmd_data['mode'] == MODE_VISUAL:
            vi_cmd_data['motion']['args']['extend'] = True
            vi_cmd_data['post_motion'] = [['_vi_underscore_post_motion', {'mode': vi_cmd_data['mode'], 'extend': True}],]

    return vi_cmd_data


def vi_l(vi_cmd_data):
    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'characters', 'forward': True}

    # EXCLUSIVE
    # v2l
    # Can move onto the new line character.
    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_every_motion'] = ['visual_dont_overshoot_line_right',]
    # Cannot move onto the new line character.
    else:
        vi_cmd_data['post_every_motion'] = ['dont_overshoot_line_right',]

    return vi_cmd_data


def vi_h(vi_cmd_data):
    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'characters', 'forward': False}

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_every_motion'] = ['visual_dont_overshoot_line_left',]
    else:
        vi_cmd_data['post_every_motion'] = ['dont_overshoot_line_left',]

    return vi_cmd_data


def vi_j(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True}

    if vi_cmd_data['_internal_mode'] == _MODE_INTERNAL_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_motion'] = ['_vi_j_pre_motion',]
        vi_cmd_data['post_motion'] = [['_vi_j_post_motion',],]
    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_motion'] = [['visual_clip_end_to_eol',],]
        # This takes care of ST extending the end by one character.
        vi_cmd_data['reposition_caret'] = ['visual_shrink_end_one_char',]
    elif vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_motion'] = [['visual_extend_end_to_hard_end', {'mode': MODE_VISUAL_LINE}],]
    else:
        vi_cmd_data['post_motion'] = [['clip_end_to_line',],]

    return vi_cmd_data


def vi_k(vi_cmd_data):
    if vi_cmd_data['count'] > 5:
        vi_cmd_data['is_jump'] = True

    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': False}

    if vi_cmd_data['_internal_mode'] == _MODE_INTERNAL_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_motion'] = [['visual_extend_to_full_line', {'_internal_mode': vi_cmd_data['_internal_mode']}],]
    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        # This takes care of ST extending the end by one character.
        vi_cmd_data['reposition_caret'] = ['visual_shrink_end_one_char',]
        vi_cmd_data['post_motion'] = [['visual_clip_end_to_eol',],]
    elif vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['motion']['args']['extend'] = True
        if vi_cmd_data['motion']['args'].get('forward'):
            pass
        else:
            vi_cmd_data['post_motion'] = [['visual_extend_end_to_hard_end', {'mode': MODE_VISUAL_LINE}],]
    else:
        vi_cmd_data['post_motion'] = [['clip_end_to_line',],]

    return vi_cmd_data


def vi_w(vi_cmd_data):
    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'words', 'forward': True}
    vi_cmd_data['post_every_motion'] = ['_vi_w_post_every_motion',]

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['pre_motion'] = ['_vi_w_pre_motion',]
        vi_cmd_data['pre_every_motion'] = ['_vi_w_pre_every_motion',]
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_every_motion'] = ['_vi_w_post_every_motion',]

    return vi_cmd_data

def vi_b(vi_cmd_data):
    vi_cmd_data['__reorient_caret'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'words', 'forward': False}

    if vi_cmd_data['mode'] in (MODE_NORMAL, _MODE_INTERNAL_VISUAL):
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode'], '_internal_mode': vi_cmd_data['_internal_mode']}]
        vi_cmd_data['post_every_motion'] = ['dont_stay_on_eol_backward',]
    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['pre_every_motion'] = ['_vi_b_pre_motion', {'mode': vi_cmd_data['mode'], '_internal_mode': vi_cmd_data['_internal_mode']}]
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['post_every_motion'] = ['_vi_b_post_every_motion', {'mode': vi_cmd_data['mode'], '_internal_mode': vi_cmd_data['_internal_mode']}]
        # vi_cmd_data['post_every_motion'] = ['dont_stay_on_eol_backward',]
        # vi_cmd_data['post_motion'] = [['extend_to_minimal_width',],]

    return vi_cmd_data


def vi_e(vi_cmd_data):
    # NORMAL mode movement:
    #   ST does what Vim does (TODO: always?).
    #
    # _MODE_INTERNAL_VISUAL
    #
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'word_ends', 'forward': True}
    vi_cmd_data['__reorient_caret'] = True

    # TODO: Seems like we're mixing modes here.
    if (vi_cmd_data['_internal_mode'] == _MODE_INTERNAL_VISUAL or
        vi_cmd_data['mode'] == MODE_NORMAL):
            vi_cmd_data['pre_motion'] = ['_vi_e_pre_motion', {'mode': vi_cmd_data['mode'], '_internal_mode': vi_cmd_data['_internal_mode']}]
            vi_cmd_data['post_every_motion'] = ['_vi_e_post_every_motion', {'mode': vi_cmd_data['mode'], '_internal_mode': vi_cmd_data['_internal_mode']}]

    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['args']['extend'] = True
        vi_cmd_data['pre_motion'] = ['_vi_e_pre_motion', {'mode': vi_cmd_data['mode'], '_internal_mode': vi_cmd_data['_internal_mode']}]
        vi_cmd_data['post_every_motion'] = ['_vi_e_post_every_motion', {'mode': vi_cmd_data['mode'], '_internal_mode': vi_cmd_data['_internal_mode']}]

    return vi_cmd_data


def vi_f(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_input'], '_internal_mode': vi_cmd_data['_internal_mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_t(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_find_in_line_exclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_input'], '_internal_mode': vi_cmd_data['_internal_mode']}

    return vi_cmd_data


def vi_big_t(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_reverse_find_in_line_exclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_input'], '_internal_mode': vi_cmd_data['_internal_mode']}

    return vi_cmd_data


def vi_big_f(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_reverse_find_in_line_inclusive'
    vi_cmd_data['motion']['args'] = {'extend': False, 'character': vi_cmd_data['user_input'], '_internal_mode': vi_cmd_data['_internal_mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_percent(vi_cmd_data):
    vi_cmd_data['is_jump'] = True

    vi_cmd_data['motion']['command'] = 'vi_percent'
    vi_cmd_data['motion']['args'] = {'percent': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_double_single_quote(vi_cmd_data):
    vi_cmd_data['motion']['command'] = 'vi_latest_jump'
    vi_cmd_data['motion']['args'] = {}
    vi_cmd_data['count'] = 1

    return vi_cmd_data
