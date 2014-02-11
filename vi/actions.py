from Vintageous.vi.utils import modes


def vi_a(state):
    cmd = {}
    cmd['action'] = '_vi_a'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    state.glue_until_normal_mode = True
    return cmd


def vi_m(state):
    cmd = {}
    cmd['action'] = '_vi_m'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'character': state.user_input}
    return cmd


def vi_gd(state):
    cmd = {}
    cmd['is_jump'] = True
    cmd['action'] = '_vi_go_to_symbol'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'globally': False}
    return cmd


def vi_big_v(state):
    cmd = {}
    cmd['action'] = '_enter_visual_line_mode'
    cmd['action_args'] = {'mode': state.mode}
    return cmd

def vi_g_big_d(state):
    cmd = {}
    cmd['is_jump'] = True
    cmd['action'] = '_vi_go_to_symbol'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'globally': True}
    return cmd


def vi_big_a(state):
    cmd = {}
    cmd['action'] = '_vi_big_a'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    state.glue_until_normal_mode = True
    return cmd


def vi_big_i(state):
    cmd = {}
    cmd['action'] = '_vi_big_i'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    state.glue_until_normal_mode = True
    return cmd


def vi_ctrl_p(state):
    cmd = {}
    cmd['action'] = 'show_overlay'
    cmd['action_args'] = {'overlay': 'goto', 'show_files': True}
    return cmd


def vi_f12(state):
    cmd = {}
    cmd['action'] = 'goto_definition'
    cmd['action_args'] = {}
    return cmd

def vi_ctrl_f12(state):
    cmd = {}
    cmd['action'] = 'show_overlay'
    cmd['action_args'] = {'overlay': 'goto', 'text': '@'}
    return cmd


def vi_shift_ctrl_f12(state):
    cmd = {}
    cmd['action'] = 'goto_symbol_in_project'
    cmd['action_args'] = {}
    return cmd


def vi_ctrl_alt_p(state):
    cmd = {}
    cmd['action'] = 'prompt_select_workspace'
    cmd['action_args'] = {}
    return cmd


def vi_colon(state):
    cmd = {}
    cmd['action'] = 'vi_colon_input'
    cmd['action_args'] = {}
    return cmd


def vi_i(state):
    cmd = {}
    cmd['action'] = '_enter_insert_mode'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    state.glue_until_normal_mode = True
    return cmd


def vi_big_r(state):
    cmd = {}
    cmd['action'] = '_enter_replace_mode'
    cmd['action_args'] = {}
    state.glue_until_normal_mode = True
    return cmd


def vi_dd(state):
    cmd = {}
    cmd['action'] = '_vi_dd_action'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_cc(state):
    cmd = {}
    cmd['action'] = '_vi_cc_action'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    state.glue_until_normal_mode = True
    return cmd



def vi_d(state):
    cmd = {}
    cmd['action'] = '_vi_d'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}
    return cmd


def vi_big_d(state):
    cmd = {}
    cmd['action'] = '_vi_big_d'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_big_c(state):
    cmd = {}
    cmd['action'] = '_vi_big_c'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_esc(state):
    cmd = {}
    cmd['action'] = '_enter_normal_mode'
    cmd['action_args'] = {'mode': state.mode}
    return cmd


def vi_v(state):
    cmd = {}
    cmd['action'] = '_enter_visual_mode'
    cmd['action_args'] = {'mode': state.mode}
    return cmd


def vi_gU(state):
    cmd = {}
    cmd['action'] = '_vi_g_big_u'
    cmd['action_args'] = {'mode': state.mode}
    return cmd


def vi_gu(state):
    cmd = {}
    cmd['action'] = '_vi_gu'
    cmd['action_args'] = {'mode': state.mode}
    return cmd


def vi_u(state):
    cmd = {}
    cmd['action'] = '_vi_u'
    cmd['action_args'] = {'count': state.count}
    return cmd


def vi_ctrl_r(state):
    cmd = {}
    cmd['action'] = '_vi_ctrl_r'
    cmd['action_args'] = {'count': state.count}
    return cmd


def vi_c(state):
    cmd = {}
    cmd['action'] = '_vi_c'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    state.glue_until_normal_mode = True
    return cmd


def vi_dot(state):
    cmd = {}
    cmd['action'] = '_vi_dot'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count,
                          'repeat_data': state.repeat_data}
    return cmd


def vi_o(state, **kwargs):
    cmd = {}

    if state.mode in (modes.VISUAL, modes.VISUAL_LINE):
        cmd['action'] = '_vi_visual_o'
        cmd['action_args'] = {'mode': state.mode, 'count': 1}
    else:
        cmd = {}
        cmd['action'] = '_vi_o'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        state.glue_until_normal_mode = True

    return cmd


def vi_big_s(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_big_s_action'
    cmd['action_args'] = {'mode': state.mode, 'count': 1, 'register': state.register}
    state.glue_until_normal_mode = True

    return cmd


def vi_s(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_s'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}
    state.glue_until_normal_mode = True

    return cmd


def vi_x(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_x'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}
    state.glue_until_normal_mode = True

    return cmd


def vi_r(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_r'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register, 'char': state.user_input}

    return cmd


def vi_less_than_less_than(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_less_than_less_than'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_equal_equal(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_equal_equal'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_greater_than_greater_than(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_greater_than_greater_than'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_greater_than(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_greater_than'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}

    return cmd

def vi_less_than(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_less_than'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}

    return cmd

def vi_equal(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_equal'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_yy(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_yy'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}
    return cmd


def vi_y(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_y'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}
    return cmd


def vi_f7(state, **kwargs):
    cmd = {}
    cmd['action'] = 'build'
    cmd['action_args'] = {}
    return cmd


def vi_big_o(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_big_o'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    state.glue_until_normal_mode = True

    return cmd


def vi_big_x(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_big_x'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}

    return cmd


def vi_big_p(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_big_p'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}

    return cmd


def vi_p(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_p'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}

    return cmd


def vi_gq(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_gq'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}

    return cmd


def vi_gt(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_gt'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_g_big_t(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_g_big_t'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_ctrl_w_q(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_ctrl_w_q'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_ctrl_w_v(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_ctrl_w_v'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_ctrl_w_l(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_ctrl_w_l'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd

def vi_ctrl_w_h(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_ctrl_w_h'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_ctrl_w_big_h(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_ctrl_w_big_h'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_ctrl_w_big_l(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_ctrl_w_big_l'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_z_enter(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_z_enter'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_zz(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_zz'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_z_minus(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_z_minus'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_z_b(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_z_minus'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_ctrl_x(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_modify_numbers'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'subtract': True}
    return cmd


def vi_ctrl_a(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_modify_numbers'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_big_j(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_big_j'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_g_big_j(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_big_j'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'separator': None}
    return cmd


def vi_gv(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_gv'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_ctrl_e(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_ctrl_e'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_ctrl_y(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_ctrl_y'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd

def vi_ctrl_big_p(state, **kwargs):
    cmd = {}
    cmd['action'] = 'show_overlay'
    cmd['action_args'] = {'overlay': 'command_palette'}
    return cmd


def vi_f11(state, **kwargs):
    cmd = {}
    cmd['action'] = 'toggle_full_screen'
    cmd['action_args'] = {}
    return cmd


def vi_big_y(state, **kwargs):
    cmd = {}
    cmd['action'] = '_vi_big_y'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_big_z_big_z(state, **kwargs):
    cmd = {}
    cmd['action'] = 'ex_exit'
    cmd['action_args'] = {'mode': state.mode, 'count': state.count}
    return cmd


def vi_big_z_big_q(state, **kwargs):
    cmd = {}
    cmd['action'] = 'ex_quit'
    cmd['action_args'] = {'forced': True, 'count': state.count}
    return cmd


def vi_gh(state, **kwargs):
    cmd = {}
    cmd['action'] = '_enter_select_mode'
    cmd['action_args'] = {'mode': state.mode}
    return cmd


def vi_f4(state, **kwargs):
    cmd = {}
    cmd['action'] = 'next_result'
    cmd['action_args'] = {}
    return cmd


def vi_ctrl_r_equal(state):
    cmd = {}
    cmd['action'] = '_vi_ctrl_r_equal'
    cmd['action_args'] = {'insert': True}


def vi_q(state):
    cmd = {}
    cmd['action'] = '_vi_q'
    cmd['action_args'] = {'name': state.user_input}
    return cmd

def vi_at(state):
    cmd = {}
    cmd['action'] = '_vi_at'
    cmd['action_args'] = {'name': state.user_input, 'count': state.count}
    return cmd
