# All data types stores in the ``vi_cmd_data`` dictionary must be valid for JSON.
# The dictionary ends up being an argumento to an ST command.


from Vintageous.vi import motions
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import ACTIONS_EXITING_TO_INSERT_MODE
from Vintageous.vi.constants import MODE_INSERT
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_NORMAL_INSERT
from Vintageous.vi.constants import MODE_REPLACE
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE


def vi_enter_visual_mode(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_enter_visual_mode'
    vi_cmd_data['action']['args'] = {}
    return vi_cmd_data


def vi_enter_normal_mode(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_enter_normal_mode'
    vi_cmd_data['action']['args'] = {}
    return vi_cmd_data


def vi_enter_visual_line_mode(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    # TODO: This seems to be duplicated during this command's full run.
    vi_cmd_data['action']['command'] = 'vi_enter_visual_line_mode'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['visual_extend_to_full_line',]
    return vi_cmd_data


def vi_enter_insert_mode(vi_cmd_data):
    # It's not too important to set this attribute, since vi_enter_normal_mode and co. will always
    # update xpos on their own, but it's confusing to let vi_enter_insert_mode set xpos to 0.
    vi_cmd_data['must_update_xpos'] = False
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_enter_insert_mode'
    vi_cmd_data['action']['args'] = {}
    return vi_cmd_data


def vi_enter_normal_insert_mode(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_enter_normal_insert_mode'
    vi_cmd_data['action']['args'] = {}
    return vi_cmd_data


def vi_enter_replace_mode(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_enter_replace_mode'
    vi_cmd_data['action']['args'] = {}
    return vi_cmd_data


def vi_d(vi_cmd_data):
    vi_cmd_data['cancel_action_if_motion_fails'] = True
    vi_cmd_data['can_yank'] = True
    vi_cmd_data['populates_small_delete_register'] = True
    vi_cmd_data['motion_required'] = True
    forward = vi_cmd_data['motion'].get('args') and vi_cmd_data['motion']['args'].get('forward')
    # FIXME: Should not delete new line characters.
    vi_cmd_data['action']['command'] = 'right_delete' if forward else 'left_delete'
    vi_cmd_data['action']['args'] = {}
    # FIXME: dj must leave the caret at the first non-whitespace character. Either let commands
    # specify multiple post_action hooks or implement a custom one for vi_d to factor this in.
    vi_cmd_data['post_action'] = ['_vi_d_post_action',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    # If we're deleting by words, make sure we don't delete the entire line
    # when deleting the last character from the last word on the line.
    # Under these circumstances, visual mode will select the last character and
    # the newline, so clip the newline from the resulting motion.
    #
    # TODO: Maybe there should be a 'post_motion_required_by_action' step in
    # the action execution. That would help avoid conflicting requirements by
    # motions/actions?
    if vi_cmd_data['motion'].get('args') and \
       vi_cmd_data['motion']['args'].get('by') == 'words':
            vi_cmd_data['post_every_motion'] = ['_d_w_post_every_motion']

    return vi_cmd_data


def vi_visual_o(vi_cmd_data):
    vi_cmd_data['motion_required'] = True
    vi_cmd_data['action']['command'] = 'vi_reverse_caret'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data

def vi_o(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'run_macro_file'
    vi_cmd_data['action']['args'] = {'file': 'res://Packages/Default/Add Line.sublime-macro'}
    vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
    vi_cmd_data['next_mode'] = MODE_INSERT

    return vi_cmd_data


def vi_big_o(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'run_macro_file'
    vi_cmd_data['action']['args'] = {'file': 'res://Packages/Default/Add Line Before.sublime-macro'}
    vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
    vi_cmd_data['next_mode'] = MODE_INSERT

    return vi_cmd_data


def vi_big_a(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_edit_at_eol'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_big_i(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_big_i'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_a(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_edit_after_caret'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_s(vi_cmd_data):
    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'characters', 'extend': True, 'forward': True}

    vi_cmd_data['can_yank'] = True
    vi_cmd_data['populates_small_delete_register'] = True

    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'right_delete'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
    vi_cmd_data['next_mode'] = MODE_INSERT

    return vi_cmd_data

def vi_c(vi_cmd_data):
    vi_cmd_data['can_yank'] = True
    vi_cmd_data['populates_small_delete_register'] = True
    vi_cmd_data['cancel_action_if_motion_fails'] = True

    vi_cmd_data['motion_required'] = True
    vi_cmd_data['action']['command'] = 'left_delete'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
    vi_cmd_data['next_mode'] = MODE_INSERT

    # If we're deleting by words, make sure we don't delete the entire line
    # when deleting the last character from the last word on the line.
    # Under these circumstances, visual mode will select the last character and
    # the newline, so clip the newline from the resulting motion.
    #
    # TODO: Maybe there should be a 'post_motion_required_by_action' step in
    # the action execution. That would help avoid conflicting requirements by
    # motions/actions?
    if vi_cmd_data['motion'].get('args') and \
       vi_cmd_data['motion']['args'].get('by') == 'words':
            vi_cmd_data['post_every_motion'] = ['visual_dont_stay_on_eol_forward_maybe']

    return vi_cmd_data


def vi_big_c(vi_cmd_data):
    # C
    # Motion + Action
    # No count: CHARACTERWISE + EXCLUSIVE
    # Count: LINEWISE + EXCLUSIVE

    vi_cmd_data['can_yank'] = True
    vi_cmd_data['populates_small_delete_register'] = True

    if vi_cmd_data['count'] == 1:
        vi_cmd_data['motion']['command'] = 'move_to'
        vi_cmd_data['motion']['args'] = {'to': 'eol', 'extend': True}

        vi_cmd_data['motion_required'] = False
        vi_cmd_data['action']['command'] = 'right_delete'
        vi_cmd_data['action']['args'] = {}
        vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
        vi_cmd_data['next_mode'] = MODE_INSERT

    else:
        # Avoid C'ing one line too many.
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True, 'extend': True}
        vi_cmd_data['post_motion'] = [['extend_to_minimal_width',], ['visual_extend_to_line',]]

        vi_cmd_data['motion_required'] = False
        vi_cmd_data['action']['command'] = 'right_delete'
        vi_cmd_data['action']['args'] = {}
        vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
        vi_cmd_data['next_mode'] = MODE_INSERT

    return vi_cmd_data


def vi_big_d(vi_cmd_data):
    vi_cmd_data['can_yank'] = True
    vi_cmd_data['populates_small_delete_register'] = True

    # TODO: Use separate if branches for each mode.

    if vi_cmd_data['count'] == 1:
        vi_cmd_data['motion']['command'] = 'move_to'
        vi_cmd_data['motion']['args'] = {'to': 'eol', 'extend': True}

        vi_cmd_data['motion_required'] = False
        vi_cmd_data['action']['command'] = 'right_delete'
        vi_cmd_data['action']['args'] = {}

    else:
        # Avoid C'ing one line too many.
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True, 'extend': True}
        vi_cmd_data['post_motion'] = [['_vi_big_b_post_motion', {'mode': vi_cmd_data['mode']}],]

        vi_cmd_data['motion_required'] = False
        vi_cmd_data['action']['command'] = 'right_delete'
        vi_cmd_data['action']['args'] = {}

    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'
    vi_cmd_data['next_mode'] = MODE_NORMAL

    return vi_cmd_data


def vi_big_s(vi_cmd_data):
    # S
    # Motion + Action
    # No count: CHARACTERWISE + EXCLUSIVE
    # Count: LINEWISE + EXCLUSIVE

    vi_cmd_data['can_yank'] = True
    vi_cmd_data['yanks_linewise'] = True

    if vi_cmd_data['count'] == 1:
        # Force execution of motion steps.
        vi_cmd_data['motion']['command'] = 'no_op'
        vi_cmd_data['motion']['args'] = {'forward': True}
        vi_cmd_data['post_motion'] = [['extend_to_minimal_width',], ['visual_extend_to_line',],]

        vi_cmd_data['motion_required'] = False
        vi_cmd_data['action']['command'] = 'right_delete'
        vi_cmd_data['action']['args'] = {}
        vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
        vi_cmd_data['next_mode'] = MODE_INSERT
    else:
        # Avoid S'ing one line too many.
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'forward': True, 'extend': True}
        vi_cmd_data['post_motion'] = [['_vi_big_s_post_motion' ,{'mode': vi_cmd_data['mode']}],]

        vi_cmd_data['motion_required'] = False
        vi_cmd_data['action']['command'] = 'right_delete'
        vi_cmd_data['action']['args'] = {}
        vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
        vi_cmd_data['next_mode'] = MODE_INSERT

    return vi_cmd_data


def vi_x(vi_cmd_data):
    vi_cmd_data['can_yank'] = True
    vi_cmd_data['populates_small_delete_register'] = True
    vi_cmd_data['motion_required'] = False

    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['cancel_action_if_motion_fails'] = True
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'characters', 'forward': True, 'extend':True}
        vi_cmd_data['post_every_motion'] = ['_vi_x_post_every_motion', {'mode': vi_cmd_data['mode']}]

    vi_cmd_data['action']['command'] = 'right_delete'
    vi_cmd_data['action']['args'] = {}

    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_big_x(vi_cmd_data):
    # TODO: Commands that specify a motion as well as an action should have a way of inspecting
    # the current operation mode. Perhaps a dummy_motion command could be introduced to enable
    # this.
    vi_cmd_data['can_yank'] = True
    vi_cmd_data['motion_required'] = False

    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['populates_small_delete_register'] = True
        vi_cmd_data['cancel_action_if_motion_fails'] = True
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'characters', 'forward': False, 'extend':True}
        vi_cmd_data['post_every_motion'] = ['_vi_big_x_post_every_motion', {'mode': vi_cmd_data['mode']}]

    elif vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['motion']['command'] = '_vi_big_x_motion'
        vi_cmd_data['motion']['args'] = {'mode': vi_cmd_data['mode']}

    # TODO: This is wrong for VISUALMODE. In VISUALMODE, X in Vim deletes linewise.
    vi_cmd_data['action']['command'] = 'left_delete'
    vi_cmd_data['action']['args'] = {}

    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_p(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_paste'
    vi_cmd_data['action']['args'] = {'count': vi_cmd_data['count'], 'register': vi_cmd_data['register']}
    vi_cmd_data['post_action'] = ['dont_stay_on_eol_backward',]

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['post_action'] = ['collapse_to_a',]
        vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'
    elif vi_cmd_data['mode'] == MODE_VISUAL_LINE:
        vi_cmd_data['post_action'] = ['collapse_to_a',]
        vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_big_p(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'vi_paste_before'
    vi_cmd_data['action']['args'] = {'count': vi_cmd_data['count'], 'register': vi_cmd_data['register']}

    if vi_cmd_data['mode'] == MODE_VISUAL:
        vi_cmd_data['post_action'] = ['collapse_to_a',]
        vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_dd(vi_cmd_data):
    # Assume _MODE_INTERNAL_NORMAL. Can't be issued in any other mode.
    vi_cmd_data['can_yank'] = True
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'lines', 'extend': True, 'forward': True}
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['pre_motion'] = ['_vi_dd_pre_motion', {'mode': vi_cmd_data['mode']}]
    vi_cmd_data['post_motion'] = [['_vi_dd_post_motion', {'mode': vi_cmd_data['mode']}],]
    vi_cmd_data['action']['command'] = 'left_delete'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['_vi_move_caret_to_first_non_white_space_character',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_cc(vi_cmd_data):
    vi_cmd_data['can_yank'] = True
    # Even though this command operates CHARACTERWISE, when populating registers it switches to
    # LINEWISE.
    vi_cmd_data['yanks_linewise'] = True

    vi_cmd_data['motion']['command'] = 'no_op'
    vi_cmd_data['motion']['args'] = {'forward': True}
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['post_motion'] = [['visual_extend_to_line',],]

    # FIXME: cc should not delete empty lines, so we need a specific command here that takes that
    # into account.
    vi_cmd_data['action']['command'] = 'right_delete'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['follow_up_mode'] = 'vi_enter_insert_mode'
    vi_cmd_data['next_mode'] = MODE_INSERT

    return vi_cmd_data


def vi_y(vi_cmd_data):
    vi_cmd_data['motion_required'] = True
    vi_cmd_data['can_yank'] = True
    vi_cmd_data['restore_original_carets'] = True
    # The yanked text will be put in the clipboard if needed. This command shouldn't do any action.
    vi_cmd_data['action']['command'] = 'no_op'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['selection_modifier'] = ['_vi_collapse_to_begin',]
    # For example, 3yk operates linewise in _MODE_INTERNAL_NORMAL. This will cause the carets to
    # end up at BOL, so selection_modifier isn't enough to place them at the desirable point.
    # XXX: Maybe selection_modifier and align_with_xpos can be simplified somehow: linewise
    # commands in _MODE_INTERNAL_NORMAL probably behave the same?
    vi_cmd_data['align_with_xpos'] = True
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_yy(vi_cmd_data):
    # Assume NORMALMODE.
    # FIXME: Cannot copy (or maybe pasting is the problem) one empty line only.
    vi_cmd_data['mode'] = _MODE_INTERNAL_NORMAL
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['restore_original_carets'] = True

    vi_cmd_data['synthetize_new_line_at_eof'] = True

    vi_cmd_data['pre_motion'] = ['_vi_yy_pre_motion',]
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'lines', 'extend': True, 'forward': True}
    # TODO: yy should leave the caret where it found it. As a temporary solution, we'll leave it
    # at BOL, which is the lesser evil between that and HEOL.
    vi_cmd_data['post_motion'] = [['_vi_yy_post_motion',],]

    vi_cmd_data['count'] = vi_cmd_data['count'] - 1
    vi_cmd_data['can_yank'] = True

    # The yanked text will be put in the clipboard if needed. This command shouldn't do any action.
    vi_cmd_data['action']['command'] = 'no_op'
    vi_cmd_data['action']['args'] = {}

    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'
    vi_cmd_data['_mark_groups_for_gluing'] = False

    return vi_cmd_data


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


def vi_g_big_u(vi_cmd_data):
    vi_cmd_data['motion_required'] = True
    vi_cmd_data['action']['command'] = 'upper_case'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_g_u(vi_cmd_data):
    vi_cmd_data['motion_required'] = True
    vi_cmd_data['action']['command'] = 'lower_case'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_g_q(vi_cmd_data):
    vi_cmd_data['motion_required'] = True
    vi_cmd_data['action']['command'] = 'wrap_lines'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_z_action(vi_cmd_data):
    """This doesn't do anything by itself, but tells global state to wait for a second action that
       completes this one.
    """
    vi_cmd_data['motion_required'] = True
    # Let global state know we still need a second action to complete this one.
    vi_cmd_data['is_digraph_start'] = True
    vi_cmd_data['action']['command'] = 'no_op'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_z_enter(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_z_enter'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['_vi_move_caret_to_first_non_white_space_character',]

    return vi_cmd_data


def vi_z_t(vi_cmd_data):
    # Identical to vi_z_enter except the caret should remain untouched.
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_z_enter'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_zz(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_zz'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_z_minus(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_z_minus'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['_vi_move_caret_to_first_non_white_space_character',]

    return vi_cmd_data

def vi_z_b(vi_cmd_data):
    # Identical to vi_z_minus except the caret should remain untouched.
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_z_minus'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_double_lambda(vi_cmd_data):
    # Assume _MODE_INTERNAL_NORMAL.
    if vi_cmd_data['count'] > 1:
        vi_cmd_data['count'] = vi_cmd_data['count'] - 1
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'extend': True, 'forward': True}

    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'indent'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_double_antilambda(vi_cmd_data):
    # Assume _MODE_INTERNAL_NORMAL.
    if vi_cmd_data['count'] > 1:
        vi_cmd_data['motion']['command'] = 'move'
        vi_cmd_data['motion']['args'] = {'by': 'lines', 'extend': True, 'forward': True}

    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = 'unindent'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_r(vi_cmd_data):
    # TODO: If count > len(line), r should abort. We'd need _p_post_every_motion hook and tell
    # ViRun to cancel if selections didn't change.
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'characters', 'extend': True, 'forward': True}
    vi_cmd_data['action']['command'] = '_vi_r'
    vi_cmd_data['action']['args'] = {'character': vi_cmd_data['user_input'], 'mode': vi_cmd_data['mode']}
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_lambda(vi_cmd_data):
    vi_cmd_data['motion_required'] = True
    vi_cmd_data['action']['command'] = 'indent'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    if vi_cmd_data['mode'] in (MODE_VISUAL, MODE_VISUAL_LINE):
        vi_cmd_data['_repeat_action'] = True

    return vi_cmd_data


def vi_antilambda(vi_cmd_data):
    vi_cmd_data['motion_required'] = True
    vi_cmd_data['action']['command'] = 'unindent'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    if vi_cmd_data['mode'] in (MODE_VISUAL, MODE_VISUAL_LINE):
        vi_cmd_data['_repeat_action'] = True

    return vi_cmd_data


def vi_big_j(vi_cmd_data):
    vi_cmd_data['motion_required'] = False

    if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        vi_cmd_data['_repeat_action'] = True
        vi_cmd_data['count'] = (vi_cmd_data['count'] - 1 or 1)
        vi_cmd_data['action']['command'] = '_vi_big_j'
        vi_cmd_data['action']['args'] = {'mode': vi_cmd_data['mode']}
    else:
        vi_cmd_data['action']['command'] = 'no_op'
        vi_cmd_data['action']['args'] = {}

    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_big_u(vi_cmd_data):
    # XXX: Assume MODE_VISUAL or MODE_VISUAL_LINE
    # TODO: Is this required for a visual operation?
    vi_cmd_data['motion_required'] = False

    vi_cmd_data['motion']['command'] = 'no_op'
    vi_cmd_data['motion']['args'] = {}

    vi_cmd_data['action']['command'] = 'upper_case'
    vi_cmd_data['action']['args'] = {}

    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_u(vi_cmd_data):
    # XXX: Assume MODE_VISUAL or MODE_VISUAL_LINE
    # TODO: Is this required for a visual operation?
    vi_cmd_data['motion_required'] = False

    vi_cmd_data['motion']['command'] = 'no_op'
    vi_cmd_data['motion']['args'] = {}

    vi_cmd_data['action']['command'] = 'lower_case'
    vi_cmd_data['action']['args'] = {}

    vi_cmd_data['post_action'] = ['collapse_to_a',]
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_ctrl_w_action(vi_cmd_data):
    """This doesn't do anything by itself, but tells global state to wait for a second action that
       completes this one.
    """
    vi_cmd_data['motion_required'] = False
    # Let global state know we still need a second action to complete this one.
    vi_cmd_data['is_digraph_start'] = True
    vi_cmd_data['action']['command'] = 'no_op'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_ctrl_w_v(vi_cmd_data):
    vi_cmd_data['motion_required'] = False

    vi_cmd_data['action']['command'] = '_vi_ctrl_w_v_action'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_ctrl_r_action(vi_cmd_data):
    """This doesn't do anything by itself, but tells global state to wait for a second action that
       completes this one.
    """
    vi_cmd_data['_change_mode_to'] = MODE_NORMAL
    vi_cmd_data['must_blink_on_error'] = True
    vi_cmd_data['_exit_mode'] = MODE_INSERT
    vi_cmd_data['_exit_mode_command'] = 'vi_enter_insert_mode'
    vi_cmd_data['motion_required'] = False
    # Let global state know we still need a second action to complete this one.
    vi_cmd_data['is_digraph_start'] = True
    vi_cmd_data['action']['command'] = 'vi_enter_normal_mode'
    vi_cmd_data['action']['args'] = {}

    return vi_cmd_data


def vi_ctrl_r_equals(vi_cmd_data):
    vi_cmd_data['motion_required'] = False

    vi_cmd_data['action']['command'] = 'vi_expression_register'
    vi_cmd_data['action']['args'] = {'insert': True, 'next_mode': MODE_INSERT}

    return vi_cmd_data


def vi_ctrl_a(vi_cmd_data):
    vi_cmd_data['motion_required'] = False

    vi_cmd_data['action']['command'] = '_vi_ctrl_a'
    vi_cmd_data['action']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_ctrl_x(vi_cmd_data):
    vi_cmd_data['motion_required'] = False

    vi_cmd_data['action']['command'] = '_vi_ctrl_x'
    vi_cmd_data['action']['args'] = {'mode': vi_cmd_data['mode'], 'count': vi_cmd_data['count']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_esc(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    if vi_cmd_data['mode'] == MODE_NORMAL_INSERT:
        vi_cmd_data['action']['command'] = 'vi_run_normal_insert_mode_actions'
        vi_cmd_data['action']['args'] = {}
        vi_cmd_data['motion']['command'] = 'no_op'
        vi_cmd_data['motion']['args'] = {}
    if vi_cmd_data['mode'] in (MODE_INSERT, MODE_REPLACE,):
        vi_cmd_data['action']['command'] = 'vi_enter_normal_mode_from_insert_mode'
        vi_cmd_data['action']['args'] = {}
        vi_cmd_data['motion']['command'] = 'no_op'
        vi_cmd_data['motion']['args'] = {}
    elif vi_cmd_data['mode'] in (MODE_VISUAL, MODE_VISUAL_LINE,):
        vi_cmd_data['action']['command'] = 'vi_enter_normal_mode'
        vi_cmd_data['action']['args'] = {}
        vi_cmd_data['motion']['command'] = 'no_op'
        vi_cmd_data['motion']['args'] = {}
    elif vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
        # We reach this branch, for instance, when we have 'vi_search' regions outlined from a
        # previous search; we need to remove them.
        vi_cmd_data['action']['command'] = 'vi_enter_normal_mode'
        vi_cmd_data['action']['args'] = {}
        vi_cmd_data['motion']['command'] = 'no_op'
        vi_cmd_data['motion']['args'] = {}

    return vi_cmd_data

def vi_m(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_m'
    vi_cmd_data['action']['args'] = {'character': vi_cmd_data['user_input']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_equals(vi_cmd_data):
    vi_cmd_data['action']['command'] = 'reindent'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data


def vi_g_v(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_g_v'
    vi_cmd_data['action']['args'] = {}
    vi_cmd_data['follow_up_mode'] = 'vi_enter_visual_mode'

    return vi_cmd_data


def vi_equals_equals(vi_cmd_data):
    # FIXME: Sloppy implementation. I don't even know what the 'reindent' built-in is supposed to
    # do.

    # Assume NORMALMODE.
    vi_cmd_data['mode'] = _MODE_INTERNAL_NORMAL
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['restore_original_carets'] = True

    #////////////////////////////////////////////////////////////
    # FIXME: This looks bad here, but it will probably work at a basic level.
    # vi_cmd_data['pre_motion'] = ['_vi_yy_pre_motion',]
    vi_cmd_data['motion']['command'] = 'move'
    vi_cmd_data['motion']['args'] = {'by': 'lines', 'extend': True, 'forward': True}
    # TODO: yy should leave the caret where it found it. As a temporary solution, we'll leave it
    # at BOL, which is the lesser evil between that and HEOL.
    # vi_cmd_data['post_motion'] = [['_vi_yy_post_motion',],]
    #////////////////////////////////////////////////////////////

    vi_cmd_data['count'] = vi_cmd_data['count'] - 1
    vi_cmd_data['can_yank'] = True

    # The yanked text will be put in the clipboard if needed. This command shouldn't do any action.
    vi_cmd_data['action']['command'] = 'reindent'
    vi_cmd_data['action']['args'] = {}

    vi_cmd_data['follow_up_mode'] = 'vi_enter_normal_mode'

    return vi_cmd_data

def vi_q(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_q'
    vi_cmd_data['action']['args'] = {'name': vi_cmd_data['user_input']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data


def vi_at(vi_cmd_data):
    vi_cmd_data['motion_required'] = False
    vi_cmd_data['action']['command'] = '_vi_run_macro'
    vi_cmd_data['action']['args'] = {'name': vi_cmd_data['user_input']}
    vi_cmd_data['count'] = 1

    return vi_cmd_data
