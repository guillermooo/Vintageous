from Vintageous.vi import inputs


MODE_INSERT = 1
MODE_NORMAL = 1 << 1
MODE_VISUAL = 1 << 2
MODE_VISUAL_LINE = 1 << 3
# The mode you enter when giving i a count.
MODE_NORMAL_INSERT = 1 << 4
# Vintageous always runs actions based on selections. Some Vim commands,
# however, behave differently depending on whether the current mode is NORMAL
# or VISUAL. To differentiate NORMAL mode operations (involving only an
# action, or a motion plus an action) from VISUAL mode, we need to add an
# additional mode for handling selections that won't interfere with the actual
# VISUAL mode.
#
# This is _MODE_INTERNAL_NORMAL's job. We consider _MODE_INTERNAL_NORMAL a
# pseudomode, because global state's .mode property should never set to it,
# yet it's set in vi_cmd_data often.
#
# Note that for pure motions we still use plain NORMAL mode.
_MODE_INTERNAL_NORMAL = 1 << 5
MODE_REPLACE = 1 << 6
MODE_SELECT = 1 << 7
MODE_VISUAL_BLOCK = 1 << 8


DIGRAPH_ACTION = 1
DIGRAPH_MOTION = 2
STASH = 3


INPUT_IMMEDIATE = 1
INPUT_AFTER_MOTION = 2
INPUT_SPECIAL = 3


# TODO: We should separate digraph actions from digraph motions?
digraphs = {
    ('vi_d', 'vi_d'): ('vi_dd', DIGRAPH_ACTION),
    ('vi_c', 'vi_c'): ('vi_cc', DIGRAPH_ACTION),
    ('vi_y', 'vi_y'): ('vi_yy', DIGRAPH_ACTION),

    ('vi_equals', 'vi_equals'): ('vi_equals_equals', DIGRAPH_ACTION),
    ('vi_lambda', 'vi_lambda'): ('vi_double_lambda', DIGRAPH_ACTION),
    ('vi_antilambda', 'vi_antilambda'): ('vi_double_antilambda', DIGRAPH_ACTION),

    ('vi_g_action', 'vi_tilde'): ('vi_g_tilde', DIGRAPH_ACTION),
    # Ex: g~g (incomplete)
    ('vi_g_tilde', 'vi_g_action'): ('vi_g_tilde', STASH),
    # Ex: g~g~ (complete)
    ('vi_g_tilde', 'vi_g_tilde'): ('vi_g_tilde_g_tilde', DIGRAPH_ACTION),
    # Ex: g~~ (complete)
    ('vi_g_tilde', 'vi_tilde'): ('vi_g_tilde_g_tilde', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_big_u'): ('vi_g_big_u', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_u'): ('vi_g_u', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_q'): ('vi_g_q', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_v'): ('vi_g_v', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_h'): ('vi_enter_select_mode', DIGRAPH_ACTION),
    # Because the order in which commands appear in the key map file, we can
    # take advantage of vi_t without creating a g<stuff>-specific 't' binding.
    # TODO: We should be able to do the same with all the other key bindings
    # prefixed with 'g'.
    ('vi_g_action', 'vi_t'): ('vi_g_t', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_big_t'): ('vi_g_big_t', DIGRAPH_ACTION),
    ('vi_g_action', 'vi_g_e'): ('vi_g_e', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_gg'): ('vi_gg', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g_d'): ('vi_g_d', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g__'): ('vi_g__', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g_big_d'): ('vi_g_big_d', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g_star'): ('vi_g_star', DIGRAPH_MOTION),
    ('vi_g_action', 'vi_g_octothorp'): ('vi_g_octothorp', DIGRAPH_MOTION),

    ('vi_z_action', 'vi_z_enter'): ('vi_z_enter', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_z_t'): ('vi_z_t', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_z_minus'): ('vi_z_minus', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_z_b'): ('vi_z_b', DIGRAPH_ACTION),
    ('vi_z_action', 'vi_zz'): ('vi_zz', DIGRAPH_ACTION),

    ('vi_ctrl_r_action', 'vi_ctrl_r_equals'): ('vi_ctrl_r_equals', DIGRAPH_ACTION),

    ('vi_ctrl_w_action', 'vi_ctrl_w_v'): ('vi_ctrl_w_v', DIGRAPH_ACTION),
    # TODO: vi_g_q is a bad name, since 'q' combines both with g and ctrl+w.
    ('vi_ctrl_w_action', 'vi_g_q'): ('vi_ctrl_w_q', DIGRAPH_ACTION),
    # TODO: vi_g_v is a bad name, since 'v' combines both with g and ctrl+w.
    ('vi_ctrl_w_action', 'vi_g_v'): ('vi_ctrl_w_v', DIGRAPH_ACTION),
    ('vi_ctrl_w_action', 'vi_ctrl_w_l'): ('vi_ctrl_w_l', DIGRAPH_ACTION),
    ('vi_ctrl_w_action', 'vi_ctrl_w_h'): ('vi_ctrl_w_h', DIGRAPH_ACTION),
    ('vi_ctrl_w_action', 'vi_ctrl_w_big_l'): ('vi_ctrl_w_big_l', DIGRAPH_ACTION),
    ('vi_ctrl_w_action', 'vi_ctrl_w_big_h'): ('vi_ctrl_w_big_h', DIGRAPH_ACTION),

    # XXX: I don't think the following is needed.
    ('vi_f_first_step', 'vi_set_user_input'): ('vi_f', DIGRAPH_MOTION),
}


ACTION_OR_MOTION = 1
ACTION_ONLY = 2

# Actions that cannot run on their own --they require a qualifier.
INCOMPLETE_ACTIONS = {'vi_g_action': ACTION_OR_MOTION,
                      'vi_z_action': ACTION_ONLY,
                      'vi_ctrl_w_action': ACTION_ONLY,
                      'vi_ctrl_r_action': ACTION_ONLY,
                    }
ACTIONS_EXITING_TO_INSERT_MODE = ('vi_ctrl_r_action',)


# TODO: Test me
# Vim translates some motions when combined with certain actions.
MOTION_TRANSLATION_TABLE = {
    ('vi_c', 'vi_w'): 'vi_e',
}

ACTION_TO_NAMESPACE_TABLE = {
    'vi_ctrl_w_action': 'ctrl_w',
    'vi_g_action': 'g',
    'vi_z_action': 'z',
    'vi_ctrl_r_action': 'ctrl_r',
}


INPUT_FOR_MOTIONS = {
    'vi_f': (INPUT_IMMEDIATE, inputs.vi_f),
    'vi_t': (INPUT_IMMEDIATE, inputs.vi_t),
    'vi_big_f': (INPUT_IMMEDIATE, inputs.vi_big_f),
    'vi_big_t': (INPUT_IMMEDIATE, inputs.vi_big_t),
    'vi_inclusive_text_object': (INPUT_IMMEDIATE, inputs.vi_inclusive_text_object),
    'vi_exclusive_text_object': (INPUT_IMMEDIATE, inputs.vi_exclusive_text_object),
    'vi_quote': (INPUT_IMMEDIATE, inputs.vi_quote),
    'vi_forward_slash': (INPUT_IMMEDIATE, inputs.vi_forward_slash),
    'vi_question_mark': (INPUT_IMMEDIATE, inputs.vi_question_mark),
}


INPUT_FOR_ACTIONS = {
    'vi_m': (INPUT_IMMEDIATE, inputs.vi_m),
    'vi_r': (INPUT_IMMEDIATE, inputs.vi_r),
    'vi_q': (INPUT_IMMEDIATE, inputs.vi_q),
    'vi_at': (INPUT_IMMEDIATE, inputs.vi_at),
}


def action_to_namespace(action):
    return ACTION_TO_NAMESPACE_TABLE.get(action)


# TODO: This does not belong here.
def mode_to_str(mode):
    if mode == MODE_INSERT:
        return "INSERT"
    elif mode == MODE_NORMAL:
        return "NORMAL"
    elif mode == MODE_VISUAL:
        return "VISUAL"
    elif mode == MODE_VISUAL_LINE:
        return "VISUAL LINE"
    elif mode == MODE_SELECT:
        return "SELECT"
    elif mode == MODE_NORMAL_INSERT:
        return "INSERT"
    elif mode == MODE_VISUAL_BLOCK:
        return "VISUAL BLOCK"
    elif mode == MODE_REPLACE:
        # XXX: I'm not sure whether Vim prints to the status bar in this case,
        # but since Sublime Text won't let us use a block cursor, let's give
        # some feeback to the user.
        return "REPLACE"
    return "<unknown>"


# TODO: Move this to somewhere where it's easy to import from and use it for
# transformers.
def regions_transformer(view, f):
    """
    Applies ``f`` to every selection region in ``view`` and replaces the
    existing selections.
    """
    sels = list(view.sel())

    new_sels = []
    for s in sels:
        new_sels.append(f(view, s))

    view.sel().clear()
    for s in new_sels:
        view.sel().add(s)

def regions_transformer_reversed(view, f):
    """
    Applies ``f`` to every selection region in ``view`` and replaces the
    existing selections.
    """
    sels = reversed(list(view.sel()))

    new_sels = []
    for s in sels:
        new_sels.append(f(view, s))

    view.sel().clear()
    for ns in new_sels:
        view.sel().add(ns)
