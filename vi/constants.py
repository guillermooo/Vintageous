MODE_INSERT = 1
MODE_NORMAL = 1 << 1
MODE_VISUAL = 1 << 2
MODE_VISUAL_LINE = 1 << 3
# The mode you enter when giving i a count.
MODE_NORMAL_INSERT = 1 << 4
# Vintageous always runs actions based on selections. Some Vim commands, however, behave
# differently depending on whether the current mode is NORMAL or VISUAL. To differentiate NORMAL
# mode operations (involving only an action, or a motion plus an action) from VISUAL mode, we
# need to add an additional mode for handling selections that won't interfere with the actual
# VISUAL mode.
#
# This is _MODE_INTERNAL_NORMAL's job. We consider _MODE_INTERNAL_NORMAL a pseudomode, because
# global state's .mode property should never set to it, yet it's set in vi_cmd_data often.
#
# Note that for pure motions we still use plain NORMAL mode.
_MODE_INTERNAL_NORMAL = 1 << 5
MODE_REPLACE = 1 << 6


DIGRAPH_ACTION = 1
DIGRAPH_MOTION = 2


digraphs = {
    ('vi_d', 'vi_d'): ('vi_dd', DIGRAPH_ACTION),
    ('vi_c', 'vi_c'): ('vi_cc', DIGRAPH_ACTION),
    ('vi_y', 'vi_y'): ('vi_yy', DIGRAPH_ACTION),
    ('vi_equals', 'vi_equals'): ('vi_equals_equals', DIGRAPH_ACTION),
    ('vi_lambda', 'vi_lambda'): ('vi_double_lambda', DIGRAPH_ACTION),
    ('vi_antilambda', 'vi_antilambda'): ('vi_double_antilambda', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_big_u'): ('vi_g_big_u', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_u'): ('vi_g_u', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_q'): ('vi_g_q', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_v'): ('vi_g_v', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_z_enter'): ('vi_z_enter', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_z_t'): ('vi_z_t', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_z_minus'): ('vi_z_minus', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_z_b'): ('vi_z_b', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_zz'): ('vi_zz', DIGRAPH_ACTION),

    ('vi_ctrl_w_action', 'vi_ctrl_w_v'): ('vi_ctrl_w_v', DIGRAPH_ACTION),
    ('vi_ctrl_r_action', 'vi_ctrl_r_equals'): ('vi_ctrl_r_equals', DIGRAPH_ACTION),

    ('vi_g_action', 'vi_gg'): ('vi_gg', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g_d'): ('vi_g_d', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g_big_d'): ('vi_g_big_d', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g_star'): ('vi_g_star', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g_octothorp'): ('vi_g_octothorp', DIGRAPH_MOTION),
    # XXX: I don't think the following is needed.
    ('vi_f_first_step', 'vi_set_user_input'): ('vi_f', DIGRAPH_MOTION),
}


# Actions that cannot run on their own --they require a qualifier.
INCOMPLETE_ACTIONS = ('vi_g_action', 'vi_z_action', 'vi_ctrl_w_action',
                      'vi_ctrl_r_action')
ACTIONS_EXITING_TO_INSERT_MODE = ('vi_ctrl_r_action',)


# TODO: This does not belong here.
def mode_to_str(mode):
    if mode == MODE_INSERT:
        return "INSERT"
    elif mode == MODE_NORMAL:
        return ""
    elif mode == MODE_VISUAL:
        return "VISUAL"
    elif mode == MODE_VISUAL_LINE:
        return "VISUAL LINE"
    elif mode == MODE_NORMAL_INSERT:
        return "INSERT"
    elif mode == MODE_REPLACE:
        # XXX: I'm not sure whether Vim prints to the status bar in this case, but since Sublime
        # Text won't let us use a block cursor, let's give some feeback to the user.
        return "REPLACE"
    return "<unknown>"


# TODO: Move this to somewhere where it's easy to import from and use it for transformers.
def regions_transformer(view, f):
    """Applies ``f`` to every selection region in ``view`` and replaces the existing selections.
    """
    sels = list(view.sel())
    view.sel().clear()

    new_sels = []
    for s in sels:
        new_sels.append(f(view, s))

    for s in new_sels:
        view.sel().add(s)
