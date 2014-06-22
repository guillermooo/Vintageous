"""
Vim commands used internally by Vintageous that also produce ST commands.

These are the core implementations for all Vim commands.
"""

from Vintageous.vi.utils import modes
from Vintageous.vi.inputs import input_types
from Vintageous.vi.inputs import parser_def
from Vintageous.vi import inputs
from Vintageous.vi import utils
from Vintageous.vi.cmd_base import ViOperatorDef
from Vintageous.vi.cmd_base import ViMotionDef
from Vintageous.vi.cmd_base import ViMissingCommandDef
from Vintageous.vi import keys
from Vintageous.vi.keys import seqs

import sublime_plugin


_MODES_MOTION = (modes.NORMAL, modes.OPERATOR_PENDING, modes.VISUAL,
                 modes.VISUAL_LINE, modes.VISUAL_BLOCK)

_MODES_ACTION = (modes.NORMAL, modes.VISUAL, modes.VISUAL_LINE,
                 modes.VISUAL_BLOCK)


@keys.assign(seq=seqs.D, modes=_MODES_ACTION)
class ViDeleteByChars(ViOperatorDef):
    """
    Vim: `d`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_d'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


@keys.assign(seq=seqs.BIG_O, modes=_MODES_ACTION)
class ViInsertLineBefore(ViOperatorDef):
    """
    Vim: `O`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        state.glue_until_normal_mode = True

        cmd = {}
        cmd['action'] = '_vi_big_o'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.O, modes=_MODES_ACTION)
class ViInsertLineAfter(ViOperatorDef):
    """
    Vim: `o`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = False

    def translate(self, state):
        cmd = {}

        # XXX: Create a separate command?
        if state.mode in (modes.VISUAL, modes.VISUAL_LINE):
            cmd['action'] = '_vi_visual_o'
            cmd['action_args'] = {'mode': state.mode, 'count': 1}

        else:
            state.glue_until_normal_mode = True

            cmd = {}
            cmd['action'] = '_vi_o'
            cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.X, modes=_MODES_ACTION)
class ViRightDeleteChars(ViOperatorDef):
    """
    Vim: `x`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_x'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


@keys.assign(seq=seqs.S, modes=_MODES_ACTION)
class ViSubstituteChar(ViOperatorDef):
    """
    Vim: `s`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        # XXX: Handle differently from State?
        state.glue_until_normal_mode = True

        cmd = {}
        cmd['action'] = '_vi_s'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


@keys.assign(seq=seqs.Y, modes=_MODES_ACTION)
class ViYankByChars(ViOperatorDef):
    """
    Vim: `y`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_y'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


@keys.assign(seq=seqs.EQUAL, modes=_MODES_ACTION)
class ViReindent(ViOperatorDef):
    """
    Vim: `=`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_equal'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.GREATER_THAN, modes=_MODES_ACTION)
class ViIndent(ViOperatorDef):
    """
    Vim: `>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_greater_than'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.LESS_THAN, modes=_MODES_ACTION)
class ViUnindent(ViOperatorDef):
    """
    Vim: `<`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_less_than'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.C, modes=_MODES_ACTION)
class ViChangeByChars(ViOperatorDef):
    """
    Vim: `c`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        state.glue_until_normal_mode = True

        cmd = {}
        cmd['action'] = '_vi_c'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


@keys.assign(seq=seqs.U, modes=_MODES_ACTION)
class ViUndo(ViOperatorDef):
    """
    Vim: `u`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}

        if state.mode in (modes.VISUAL,
                          modes.VISUAL_LINE,
                          modes.VISUAL_BLOCK):
            cmd['action'] = '_vi_visual_u'
            cmd['action_args'] = {'count': state.count, 'mode': state.mode}
            return cmd

        cmd['action'] = '_vi_u'
        cmd['action_args'] = {'count': state.count}
        return cmd


@keys.assign(seq=seqs.CTRL_R, modes=_MODES_ACTION)
class ViRedo(ViOperatorDef):
    """
    Vim: `C-r`
    """

    def __init__(self, inclusive=False, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_r'
        cmd['action_args'] = {'count': state.count, 'mode': state.mode}
        return cmd


@keys.assign(seq=seqs.BIG_D, modes=_MODES_ACTION)
class ViDeleteToEol(ViOperatorDef):
    """
    Vim: `D`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_d'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


@keys.assign(seq=seqs.BIG_C, modes=_MODES_ACTION)
class ViChangeToEol(ViOperatorDef):
    """
    Vim: `C`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        state.glue_until_normal_mode = True

        cmd = {}
        cmd['action'] = '_vi_big_c'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register
                              }
        return cmd


@keys.assign(seq=seqs.G_BIG_U_BIG_U, modes=_MODES_ACTION)
@keys.assign(seq=seqs.G_BIG_U_G_BIG_U, modes=_MODES_ACTION)
class ViChangeToUpperCaseByLines(ViOperatorDef):
    """
    Vim: `gUU`, `gUgU`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_u_big_u'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.CC, modes=_MODES_ACTION)
class ViChangeLine(ViOperatorDef):
    """
    Vim: `cc`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        state.glue_until_normal_mode = True

        cmd = {}
        cmd['action'] = '_vi_cc_action'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.DD, modes=_MODES_ACTION)
class ViDeleteLine(ViOperatorDef):
    """
    Vim: `dd`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_dd_action'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.BIG_R, modes=_MODES_ACTION)
class ViEnterReplaceMode(ViOperatorDef):
    """
    Vim: `R`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_enter_replace_mode'
        cmd['action_args'] = {}
        state.glue_until_normal_mode = True
        return cmd


@keys.assign(seq=seqs.GREATER_THAN_GREATER_THAN, modes=_MODES_ACTION)
class ViIndentLine(ViOperatorDef):
    """
    Vim: `>>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_greater_than_greater_than'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.GUGU, modes=_MODES_ACTION)
@keys.assign(seq=seqs.GUU, modes=_MODES_ACTION)
class ViChangeToLowerCaseByLines(ViOperatorDef):
    """
    Vim: `guu`, `gugu`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_guu'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.GU, modes=_MODES_ACTION)
class ViChangeToLowerCaseByChars(ViOperatorDef):
    """
    Vim: `gu`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_gu'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.EQUAL_EQUAL, modes=_MODES_ACTION)
class ViReindentLine(ViOperatorDef):
    """
    Vim: `==`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_equal_equal'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.LESS_THAN_LESS_THAN, modes=_MODES_ACTION)
class ViUnindentLine(ViOperatorDef):
    """
    Vim: `<<`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_less_than_less_than'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.YY, modes=_MODES_ACTION)
@keys.assign(seq=seqs.BIG_Y, modes=_MODES_ACTION)
class ViYankLine(ViOperatorDef):
    """
    Vim: `yy`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_yy'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


@keys.assign(seq=seqs.G_TILDE_TILDE, modes=_MODES_ACTION)
class ViInvertCaseByLines(ViOperatorDef):
    """
    Vim: `g~~`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_tilde_g_tilde'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.TILDE, modes=_MODES_ACTION)
class ViForceInvertCaseByChars(ViOperatorDef):
    """
    Vim: `~`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_tilde'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.BIG_S, modes=_MODES_ACTION)
class ViSubstituteByLines(ViOperatorDef):
    """
    Vim: `S`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_s_action'
        cmd['action_args'] = {'mode': state.mode, 'count': 1, 'register': state.register}
        state.glue_until_normal_mode = True
        return cmd


@keys.assign(seq=seqs.G_TILDE, modes=_MODES_ACTION)
class ViInvertCaseByChars(ViOperatorDef):
    """
    Vim: `g~`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_tilde'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


# TODO: Duplicated.
@keys.assign(seq=seqs.G_BIG_U, modes=_MODES_ACTION)
class ViChangeToUpperCaseByChars(ViOperatorDef):
    """
    Vim: `gU`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_u'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.BIG_J, modes=_MODES_ACTION + (modes.SELECT,))
class ViJoinLines(ViOperatorDef):
    """
    Vim: `J`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}

        if state.mode == modes.SELECT:
            # Exits select mode.
            cmd['action'] = '_vi_select_big_j'
            cmd['action_args'] = {'mode': state.mode, 'count': state.count}
            return cmd

        cmd['action'] = '_vi_big_j'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.CTRL_X, modes=_MODES_ACTION)
class ViDecrement(ViOperatorDef):
    """
    Vim: `C-x`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_modify_numbers'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'subtract': True,
                              }
        return cmd


@keys.assign(seq=seqs.CTRL_A, modes=_MODES_ACTION)
class ViIncrement(ViOperatorDef):
    """
    Vim: `C-a`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_modify_numbers'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.G_BIG_J, modes=_MODES_ACTION)
class ViJoinLinesNoSeparator(ViOperatorDef):
    """
    # FIXME: Doesn't work.
    Vim: `gJ`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_j'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'separator': None}
        return cmd


@keys.assign(seq=seqs.V, modes=_MODES_ACTION)
class ViEnterVisualMode(ViOperatorDef):
    """
    Vim: `v`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_enter_visual_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


@keys.assign(seq=seqs.Z_ENTER, modes=_MODES_ACTION)
@keys.assign(seq=seqs.ZT, modes=_MODES_ACTION)
class ViScrollToScreenTop(ViOperatorDef):
    """
    Vim: `z<CR>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_z_enter'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.ZB, modes=_MODES_ACTION)
class ViScrollToScreenBottom(ViOperatorDef):
    """
    Vim: `zb`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_z_minus'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.ZZ, modes=_MODES_ACTION)
class ViScrollToScreenCenter(ViOperatorDef):
    """
    Vim: `zz`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_zz'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.GQ, modes=_MODES_ACTION)
class ViReformat(ViOperatorDef):
    """
    Vim: `gq`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.motion_required = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_gq'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.P, modes=_MODES_ACTION)
class ViPasteAfter(ViOperatorDef):
    """
    Vim: `p`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_p'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }

        return cmd


@keys.assign(seq=seqs.BIG_P, modes=_MODES_ACTION)
class ViPasteBefore(ViOperatorDef):
    """
    Vim: `P`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_p'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }

        return cmd


@keys.assign(seq=seqs.BIG_X, modes=_MODES_ACTION)
class ViLeftDeleteChar(ViOperatorDef):
    """
    Vim: `X`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_x'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}

        return cmd


@keys.assign(seq=seqs.CTRL_W_L, modes=_MODES_ACTION)
class ViSendViewToRightPane(ViOperatorDef):
    """
    Vim: `<C-W-L>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_big_l'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.CTRL_W_H, modes=_MODES_ACTION)
class ViSendViewToLeftPane(ViOperatorDef):
    """
    Vim: `<C-W-H>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_big_h'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.GT, modes=_MODES_ACTION)
class ViActivateNextTab(ViOperatorDef):
    """
    Vim: `gt`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_gt'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.G_BIG_T, modes=_MODES_ACTION)
class ViActivatePreviousTab(ViOperatorDef):
    """
    Vim: `gT`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_t'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.CTRL_W_L, modes=_MODES_ACTION)
class ViActivatePaneToTheRight(ViOperatorDef):
    """
    Vim: `<C-W-l>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_l'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.CTRL_W_H, modes=_MODES_ACTION)
class ViActivatePaneToTheLeft(ViOperatorDef):
    """
    Vim: `<C-W-h>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_h'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.CTRL_W_V, modes=_MODES_ACTION)
class ViSplitVertically(ViOperatorDef):
    """
    Vim: `<C-W-v>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_v'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.CTRL_W_Q, modes=_MODES_ACTION)
class ViDestroyCurrentPane(ViOperatorDef):
    """
    Vim: `<C-W-q>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_q'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.BIG_V, modes=_MODES_ACTION)
class ViEnterVisualLineMode(ViOperatorDef):
    """
    Vim: `V`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_enter_visual_line_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


@keys.assign(seq=seqs.GV, modes=_MODES_ACTION)
class ViRestoreVisualSelections(ViOperatorDef):
    """
    Vim: `gv`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_gv'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.CTRL_K_CTRL_B, modes=_MODES_ACTION)
class StToggleSidebar(ViOperatorDef):
    """
    Vintageous: `<C-K-b>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'toggle_side_bar'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.CTRL_BIG_F, modes=_MODES_ACTION)
class StFinInFiles(ViOperatorDef):
    """
    Vintageous: `Ctrl+Shift+F`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'show_panel'
        cmd['action_args'] = {'panel': 'find_in_files'}
        return cmd


@keys.assign(seq=seqs.CTRL_O, modes=_MODES_ACTION)
class ViJumpBack(ViOperatorDef):
    """
    Vim: `<C-o>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'jump_back'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.CTRL_I, modes=_MODES_ACTION)
class ViJumpForward(ViOperatorDef):
    """
    Vim: `<C-i>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'jump_forward'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.SHIFT_CTRL_F12, modes=_MODES_ACTION)
class StGotoSymbolInProject(ViOperatorDef):
    """
    Vintageous: `<C-S-f12>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'goto_symbol_in_project'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.CTRL_F12, modes=_MODES_ACTION)
class StGotoSymbolInFile(ViOperatorDef):
    """
    Vintageous: `<C-f12>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'show_overlay'
        cmd['action_args'] = {'overlay': 'goto', 'text': '@'}
        return cmd


@keys.assign(seq=seqs.F12, modes=_MODES_ACTION)
class StGotoDefinition(ViOperatorDef):
    """
    Vintageous: `f12`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'goto_definition'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.CTRL_F2, modes=_MODES_ACTION)
class StToggleBookmark(ViOperatorDef):
    """
    Vintageous: `<C-f2>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'toggle_bookmark'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.CTRL_SHIFT_F2, modes=_MODES_ACTION)
class StClearBookmarks(ViOperatorDef):
    """
    Vintageous: `<C-S-f2>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'clear_bookmarks'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.F2, modes=_MODES_ACTION)
class StPrevBookmark(ViOperatorDef):
    """
    Vintageous: `f2`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'prev_bookmark'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.SHIFT_F2, modes=_MODES_ACTION)
class StNextBookmark(ViOperatorDef):
    """
    Vintageous: `<S-f2>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'next_bookmark'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.DOT, modes=_MODES_ACTION)
class ViRepeat(ViOperatorDef):
    """
    Vim: `.`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_dot'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'repeat_data': state.repeat_data,
                              }
        return cmd


@keys.assign(seq=seqs.CTRL_R, modes=_MODES_ACTION)
class ViOpenRegisterFromInsertMode(ViOperatorDef):
    """
    TODO: Implement this.
    Vim: `<C-r>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_r'
        cmd['action_args'] = {'count': state.count, 'mode': state.mode}
        return cmd


@keys.assign(seq=seqs.CTRL_Y, modes=_MODES_ACTION)
class ViScrollByLinesUp(ViOperatorDef):
    """
    Vim: `<C-y>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_y'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.BIG_U, modes=_MODES_ACTION)
class ViUndoLineChanges(ViOperatorDef):
    """
    TODO: Implement this.
    Vim: `U`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}

        if state.mode in (modes.VISUAL,
                          modes.VISUAL_LINE,
                          modes.VISUAL_BLOCK):
            cmd['action'] = '_vi_visual_big_u'
            cmd['action_args'] = {'count': state.count, 'mode': state.mode}
            return cmd

        return {}


@keys.assign(seq=seqs.CTRL_E, modes=_MODES_ACTION)
class ViScrollByLinesDown(ViOperatorDef):
    """
    Vim: `<C-e>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_e'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.F11, modes=_MODES_ACTION)
class StToggleFullScreen(ViOperatorDef):
    """
    Vintageous: `f11`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'toggle_full_screen'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.F7, modes=_MODES_ACTION)
class StBuild(ViOperatorDef):
    """
    Vintageous: `f7`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'build'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.SHIFT_F4, modes=_MODES_ACTION)
class StFindPrev(ViOperatorDef):
    """
    Vintageous: `Ctrl+F4`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'find_prev'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.AT, modes=_MODES_ACTION)
class ViOpenMacrosForRepeating(ViOperatorDef):
    """
    Vim: `@`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        assert len(key) == 1, '`@` only accepts a single char'
        self._inp = key
        return True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_at'
        cmd['action_args'] = {'name': self.inp,
                              'count': state.count}
        return cmd


@keys.assign(seq=seqs.Q, modes=_MODES_ACTION)
class ViToggleMacroRecorder(ViOperatorDef):
    """
    Vim: `q`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        assert len(key) == 1, '`q` only accepts a single char'
        self._inp = key
        return True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_q'
        cmd['action_args'] = {'name': self.inp}
        return cmd


@keys.assign(seq=seqs.F3, modes=_MODES_ACTION)
class StFindNext(ViOperatorDef):
    """
    Vintageous: `f3`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'find_next'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.F4, modes=_MODES_ACTION)
class StFindNextResult(ViOperatorDef):
    """
    Vintageous: `f4`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'next_result'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.SHIFT_F4, modes=_MODES_ACTION)
class StFindPrevResult(ViOperatorDef):
    """
    Vintageous: `Shift+F4`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'prev_result'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.BIG_Z_BIG_Z, modes=_MODES_ACTION)
class ViQuit(ViOperatorDef):
    """
    TODO: Is this used?
    Vim: `ZZ`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'ex_quit'
        cmd['action_args'] = {'forced': True, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.G_BIG_H, modes=_MODES_ACTION)
class ViEnterSelectModeForSearch(ViOperatorDef):
    """
    Vim: `gH`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_h'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.SHIFT_F4, modes=_MODES_ACTION)
class StPrevResult(ViOperatorDef):
    """
    Vim: `Shift+F4`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'prev_result'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.GH, modes=_MODES_ACTION)
class ViEnterSelectMode(ViOperatorDef):
    """
    Vim: `gh`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_enter_select_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


@keys.assign(seq=seqs.CTRL_V, modes=_MODES_ACTION)
class ViEnterVisualBlockMode(ViOperatorDef):
    """
    Vim: `<C-v>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_enter_visual_block_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


@keys.assign(seq=seqs.CTRL_P, modes=_MODES_ACTION)
class StShowGotoAnything(ViOperatorDef):
    """
    Vintageous: `<C-p>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'show_overlay'
        cmd['action_args'] = {'overlay': 'goto', 'show_files': True}
        return cmd


@keys.assign(seq=seqs.J, modes=(modes.SELECT,))
class ViAddSelection(ViOperatorDef):
    """
    Vintageous: `<C-p>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_select_j'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.ALT_CTRL_P, modes=_MODES_ACTION)
class StShowSwitchProject(ViOperatorDef):
    """
    Vintageous: `<C-M-p>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'prompt_select_workspace'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.CTRL_BIG_P, modes=_MODES_ACTION)
class StShowCommandPalette(ViOperatorDef):
    """
    Vintageous: `<C-S-p>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'show_overlay'
        cmd['action_args'] = {'overlay': 'command_palette'}
        return cmd


@keys.assign(seq=seqs.I, modes=_MODES_ACTION + (modes.SELECT,))
class ViEnterInserMode(ViOperatorDef):
    """
    Vim: `i`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        state.glue_until_normal_mode = True

        cmd = {}
        cmd['action'] = '_enter_insert_mode'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.ESC, modes=_MODES_ACTION)
@keys.assign(seq=seqs.CTRL_C, modes=_MODES_ACTION)
@keys.assign(seq=seqs.CTRL_LEFT_SQUARE_BRACKET, modes=_MODES_ACTION)
class ViEnterNormalMode(ViOperatorDef):
    """
    Vim: `<esc>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_enter_normal_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


@keys.assign(seq=seqs.A, modes=_MODES_ACTION)
class ViInsertAfterChar(ViOperatorDef):
    """
    Vim: `a`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_a'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        if state.mode != modes.SELECT:
            state.glue_until_normal_mode = True

        return cmd


@keys.assign(seq=seqs.BIG_A, modes=_MODES_ACTION + (modes.SELECT,))
class ViInsertAtEol(ViOperatorDef):
    """
    Vim: `A`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_a'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        if state.mode != modes.SELECT:
            state.glue_until_normal_mode = True

        return cmd


@keys.assign(seq=seqs.BIG_I, modes=_MODES_ACTION)
class ViInsertAtBol(ViOperatorDef):
    """
    Vim: `I`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_i'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        if state.mode != modes.SELECT:
            state.glue_until_normal_mode = True

        return cmd


@keys.assign(seq=seqs.COLON, modes=_MODES_ACTION)
class ViEnterCommandLineMode(ViOperatorDef):
    """
    Vim: `:`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'vi_colon_input'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.F9, modes=_MODES_ACTION)
class StSortLines(ViOperatorDef):
    """
    Vintageous: `f9`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'sort_lines'
        cmd['action_args'] = {'case_sensitive': False}
        return cmd


@keys.assign(seq=seqs.CTRL_G, modes=_MODES_ACTION)
class ViShowFileStatus(ViOperatorDef):
    """
    Vim: `<C-g>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'ex_file'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.BIG_Z_BIG_Q, modes=_MODES_ACTION)
class ViExitEditor(ViOperatorDef):
    """
    Vim: `ZQ`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'ex_quit'
        cmd['action_args'] = {'forced': True, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.BIG_Z_BIG_Z, modes=_MODES_ACTION)
class ViCloseFile(ViOperatorDef):
    """
    Vim: `ZZ`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'ex_exit'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.F6, modes=_MODES_ACTION)
class StToggleSpelling(ViOperatorDef):
    """
    Vintageous: `f6`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = 'toggle_setting'
        cmd['action_args'] = {'setting': 'spell_check'}
        return cmd


@keys.assign(seq=seqs.G_BIG_D, modes=_MODES_ACTION)
class ViGotoSymbolInProject(ViOperatorDef):
    """
    Vim: `gD`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['action'] = '_vi_go_to_symbol'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'globally': True}
        return cmd


@keys.assign(seq=seqs.K, modes=(modes.SELECT,))
class ViDeselectInstance(ViOperatorDef):
    """
    Vintageous: `k` (select mode)
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        """
        Non-standard.
        """
        if state.mode != modes.SELECT:
            raise ValueError('bad mode, expected mode_select, got {0}'.format(state.mode))

        cmd = {}
        cmd['action'] = 'soft_undo'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.L, modes=(modes.SELECT,))
class ViSkipInstance(ViOperatorDef):
    """
    Vintageous: `l` (select mode)
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        """
        Non-standard.
        """
        if state.mode != modes.SELECT:
            raise ValueError('bad mode, expected mode_select, got {0}'.format(state.mode))

        cmd = {}
        cmd['action'] = 'find_under_expand_skip'
        cmd['action_args'] = {}
        return cmd


@keys.assign(seq=seqs.GD, modes=_MODES_MOTION)
class ViGotoSymbolInFile(ViMotionDef):
    """
    Vim: `gd`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_go_to_symbol'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'globally': False}
        return cmd


@keys.assign(seq=seqs.L, modes=_MODES_MOTION)
@keys.assign(seq=seqs.RIGHT, modes=_MODES_MOTION)
@keys.assign(seq=seqs.SPACE, modes=_MODES_MOTION)
class ViMoveRightByChars(ViMotionDef):
    """
    Vim: `l`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_l'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.SHIFT_ENTER, modes=_MODES_MOTION)
class ViShiftEnterMotion(ViMotionDef):
    """
    Vim: `<S-CR>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_shift_enter'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.B, modes=_MODES_MOTION)
class ViMoveByWordsBackward(ViMotionDef):
    """
    Vim: `b`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_b'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.BIG_B, modes=_MODES_MOTION)
class ViMoveByBigWordsBackward(ViMotionDef):
    """
    Vim: `B`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_b'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.BIG_W, modes=_MODES_MOTION)
class ViMoveByBigWords(ViMotionDef):
    """
    Vim: `W`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_w'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.E, modes=_MODES_MOTION)
class ViMoveByWordEnds(ViMotionDef):
    """
    Vim: `e`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_e'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.BIG_H, modes=_MODES_MOTION)
class ViGotoScreenTop(ViMotionDef):
    """
    Vim: `H`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_h'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.GE, modes=_MODES_MOTION)
class ViMoveByWordEndsBackward(ViMotionDef):
    """
    Vim: `ge`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ge'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.G_BIG_E, modes=_MODES_MOTION)
class ViMoveByBigWordEndsBackward(ViMotionDef):
    """
    Vim: `gE`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_g_big_e'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.BIG_L, modes=_MODES_MOTION)
class ViGotoScreenBottom(ViMotionDef):
    """
    Vim: `L`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_l'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.BIG_M, modes=_MODES_MOTION)
class ViGotoScreenMiddle(ViMotionDef):
    """
    Vim: `M`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_m'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.CTRL_D, modes=_MODES_MOTION)
class ViMoveHalfScreenDown(ViMotionDef):
    """
    Vim: `<C-d>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ctrl_d'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.CTRL_U, modes=_MODES_MOTION)
class ViMoveHalfScreenUp(ViMotionDef):
    """
    Vim: `<C-u>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ctrl_u'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.CTRL_F, modes=_MODES_MOTION)
@keys.assign(seq=seqs.PAGE_UP, modes=_MODES_MOTION)
class ViMoveScreenDown(ViMotionDef):
    """
    Vim: `<C-f>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ctrl_f'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.CTRL_B, modes=_MODES_MOTION)
@keys.assign(seq=seqs.PAGE_DOWN, modes=_MODES_MOTION)
class ViMoveScreenUp(ViMotionDef):
    """
    Vim: `<C-b>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ctrl_b'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.BACKTICK, modes=_MODES_MOTION)
class ViGotoExactMarkXpos(ViMotionDef):
    """
    Vim: ```
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        assert len(key) == 1, '``` only accepts a single char'
        self._inp = key
        return True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_backtick'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'character': self.inp}
        return cmd


@keys.assign(seq=seqs.DOLLAR, modes=_MODES_MOTION)
@keys.assign(seq=seqs.END, modes=_MODES_MOTION)
class ViMoveToEol(ViMotionDef):
    """
    Vim: `$`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_dollar'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.ENTER, modes=_MODES_MOTION)
class ViMotionEnter(ViMotionDef):
    """
    Vim: `<CR>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_enter'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.G_UNDERSCORE, modes=_MODES_MOTION)
class ViMoveToSoftEol(ViMotionDef):
    """
    Vim: `g_`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_g__'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.GJ, modes=_MODES_MOTION)
class ViMoveByScreenLineDown(ViMotionDef):
    """
    Vim: `gj`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_gj'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.GK, modes=_MODES_MOTION)
class ViMoveByScreenLineUp(ViMotionDef):
    """
    Vim: `gk`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_gk'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.LEFT_BRACE, modes=_MODES_MOTION)
class ViMoveByBlockUp(ViMotionDef):
    """
    Vim: `{`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_left_brace'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.SEMICOLON, modes=_MODES_MOTION)
class ViRepeatCharSearchForward(ViMotionDef):
    """
    Vim: `;`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        forward = state.last_char_search_command in ('vi_t', 'vi_f')
        inclusive = state.last_char_search_command in ('vi_f', 'vi_big_f')

        cmd['motion'] = ('_vi_find_in_line' if forward
                                            else '_vi_reverse_find_in_line')

        cmd['motion_args'] = {'mode': state.mode, 'count': state.count,
                              'char': state.last_character_search,
                              'inclusive': inclusive}

        return cmd


@keys.assign(seq=seqs.QUOTE, modes=_MODES_MOTION)
class ViGotoMark(ViMotionDef):
    """
    Vim: `'`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        assert len(key) == 1, '`\'` only accepts a single char'
        self._inp = key
        return True

    def translate(self, state):
        cmd = {}

        if self.inp == "'":
            cmd['is_jump'] = True
            cmd['motion'] = '_vi_quote_quote'
            cmd['motion_args'] = {} # {'mode': state.mode, 'count': state.count}
            return cmd

        cmd['is_jump'] = True
        cmd['motion'] = '_vi_quote'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'character': self.inp,
                              }
        return cmd


@keys.assign(seq=seqs.RIGHT_BRACE, modes=_MODES_MOTION)
class ViMoveByBlockDown(ViMotionDef):
    """
    Vim: `}`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_right_brace'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.LEFT_PAREN, modes=_MODES_MOTION)
class ViMoveBySentenceUp(ViMotionDef):
    """
    Vim: `(`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_left_paren'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.RIGHT_PAREN, modes=_MODES_MOTION)
class ViMoveBySentenceDown(ViMotionDef):
    """
    Vim: `)`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_right_paren'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.LEFT_SQUARE_BRACKET, modes=_MODES_MOTION)
class ViGotoOpeningBracket(ViMotionDef):
    """
    Vim: `[`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True
        self.input_parser = parser_def(command=inputs.vi_left_square_bracket,
                                       interactive_command=None,
                                       input_param=None,
                                       on_done=None,
                                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        translated = utils.translate_char(key)
        assert len(translated) == 1, '`[` only accepts a single char'
        self._inp = translated
        return True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_left_square_bracket'
        cmd['motion_args'] = {'char': self.inp,
                              'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.RIGHT_SQUARE_BRACKET, modes=_MODES_MOTION)
class ViGotoClosingBracket(ViMotionDef):
    """
    Vim: `]`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True
        self.input_parser = parser_def(command=inputs.vi_left_square_bracket,
                                       interactive_command=None,
                                       input_param=None,
                                       on_done=None,
                                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        translated = utils.translate_char(key)
        assert len(translated) == 1, '`]` only accepts a single char'
        self._inp = translated
        return True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_right_square_bracket'
        cmd['motion_args'] = {'char': self.inp,
                              'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.PERCENT, modes=_MODES_MOTION)
class ViGotoLinesPercent(ViMotionDef):
    """
    Vim: `%`
    """
    # TODO: Revise this.
    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_percent'

        percent = None
        if state.motion_count or state.action_count:
            percent = state.count

        cmd['motion_args'] = {'mode': state.mode, 'percent': percent}

        return cmd


@keys.assign(seq=seqs.COMMA, modes=_MODES_MOTION)
class ViRepeatCharSearchBackward(ViMotionDef):
    """
    Vim: `,`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        forward = state.last_char_search_command in ('vi_t', 'vi_f')
        inclusive = state.last_char_search_command in ('vi_f', 'vi_big_f')

        cmd['motion'] = ('_vi_find_in_line' if not forward
                                            else '_vi_reverse_find_in_line')
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count,
                              'char': state.last_character_search,
                              'inclusive': inclusive}

        return cmd


@keys.assign(seq=seqs.PIPE, modes=_MODES_MOTION)
class ViMoveByLineCols(ViMotionDef):
    """
    Vim: `|`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_pipe'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.BIG_E, modes=_MODES_MOTION)
class ViMoveByBigWordEnds(ViMotionDef):
    """
    Vim: `E`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_e'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.H, modes=_MODES_MOTION)
@keys.assign(seq=seqs.LEFT, modes=_MODES_MOTION)
@keys.assign(seq=seqs.BACKSPACE, modes=_MODES_MOTION)
class ViMoveLeftByChars(ViMotionDef):
    """
    Vim: `h`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}

        if state.mode == modes.SELECT:
            cmd['motion'] = 'find_under_expand_skip'
            cmd['motion_args'] = {}
            return cmd

        cmd['motion'] = '_vi_h'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.W, modes=_MODES_MOTION)
class ViMoveByWords(ViMotionDef):
    """
    Vim: `w`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_w'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


@keys.assign(seq=seqs.J, modes=_MODES_MOTION)
@keys.assign(seq=seqs.DOWN, modes=_MODES_MOTION)
class ViMoveDownByLines(ViMotionDef):
    """
    Vim: `j`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_j'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'xpos': state.xpos}
        return cmd


@keys.assign(seq=seqs.K, modes=_MODES_MOTION)
@keys.assign(seq=seqs.UP, modes=_MODES_MOTION)
class ViMoveUpByLines(ViMotionDef):
    """
    Vim: `k`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_k'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'xpos': state.xpos}
        return cmd


@keys.assign(seq=seqs.HAT, modes=_MODES_MOTION)
@keys.assign(seq=seqs.HOME, modes=_MODES_MOTION)
class ViMoveToBol(ViMotionDef):
    """
    Vim: `^`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_hat'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


@keys.assign(seq=seqs.UNDERSCORE, modes=_MODES_MOTION)
class ViMoveToBol(ViMotionDef):
    """
    Vim: `^`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_underscore'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


@keys.assign(seq=seqs.ZERO, modes=_MODES_MOTION)
class ViMoveToHardBol(ViMotionDef):
    """
    Vim: `0`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_zero'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


@keys.assign(seq=seqs.N, modes=_MODES_MOTION)
class ViRepeatSearchForward(ViMotionDef):
    """
    Vim: `;`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_n'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'search_string': state.last_buffer_search}

        return cmd


@keys.assign(seq=seqs.BIG_N, modes=_MODES_MOTION)
class ViRepeatSearchBackward(ViMotionDef):
    """
    Vim: `,`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_n'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'search_string': state.last_buffer_search}

        return cmd


@keys.assign(seq=seqs.STAR, modes=_MODES_MOTION)
class ViFindWord(ViMotionDef):
    """
    Vim: `*`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_star'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


@keys.assign(seq=seqs.OCTOTHORP, modes=_MODES_MOTION)
class ViReverseFindWord(ViMotionDef):
    """
    Vim: `#`
    """

    # Trivia: Octothorp seems to be a symbol used in maps to represent a
    #         small village surrounded by eight fields.

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_octothorp'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


@keys.assign(seq=seqs.BIG_Z, modes=_MODES_MOTION)
@keys.assign(seq=seqs.CTRL_K, modes=_MODES_MOTION)
@keys.assign(seq=seqs.CTRL_W, modes=_MODES_MOTION)
@keys.assign(seq=seqs.G, modes=_MODES_MOTION)
@keys.assign(seq=seqs.Z, modes=_MODES_MOTION)
# TODO: This is called a 'submode' in the vim docs.
@keys.assign(seq=seqs.CTRL_X, modes=[modes.INSERT])
# FIXME: This should not be a motion.
class ViOpenNameSpace(ViMotionDef):
    """
    Vim: `g`, `z`, ...
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)

    def translate(self, state):
        return {}


@keys.assign(seq=seqs.DOUBLE_QUOTE, modes=_MODES_MOTION)
class ViOpenRegister(ViMotionDef):
    """
    Vim: `"`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)

    def translate(self, state):
        return {}


@keys.assign(seq=seqs.GG, modes=_MODES_MOTION)
class ViGotoBof(ViMotionDef):
    """
    Vim: `gg`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}
        # cmd['is_jump'] = True

        if state.action_count or state.motion_count:
            cmd['motion'] = '_vi_go_to_line'
            cmd['motion_args'] = {'line': state.count, 'mode': state.mode}
            return cmd

        cmd['motion'] = '_vi_gg'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.BIG_G, modes=_MODES_MOTION)
class ViGotoEof(ViMotionDef):
    """
    Vim: `G`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}

        if state.action_count or state.motion_count:
            cmd['motion'] = '_vi_go_to_line'
            cmd['motion_args'] = {'line': state.count, 'mode': state.mode}
        else:
            cmd['motion'] = '_vi_big_g'
            cmd['motion_args'] = {'mode': state.mode}

        return cmd


@keys.assign(seq=seqs.R, modes=_MODES_ACTION)
class ViReplaceCharacters(ViOperatorDef):
    """
    Vim: `r`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True
        self.repeatable = True

        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        translated = utils.translate_char(key)
        assert len(translated) == 1, '`r` only accepts a single char'
        self._inp = translated
        return True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_r'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              'char': self.inp,
                              }
        return cmd


@keys.assign(seq=seqs.M, modes=_MODES_ACTION)
class ViSetMark(ViOperatorDef):
    """
    Vim: `m`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        assert len(key) == 1, '`m` only accepts a single char'
        self._inp = key
        return True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_m'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'character': self.inp,
                              }
        return cmd


@keys.assign(seq=seqs.T, modes=_MODES_MOTION)
@keys.assign(seq=seqs.F, modes=_MODES_MOTION, inclusive=True)
class ViSearchCharForward(ViMotionDef):
    """
    Vim: `f`, `t`
    """

    def __init__(self, inclusive=False, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self._serializable.append('inclusive')
        self.scroll_into_view = True
        self.updates_xpos = True
        self.inclusive = inclusive
        self.input_parser = parser_def(command=inputs.one_char,
                                       interactive_command=None,
                                       input_param=None,
                                       on_done=None,
                                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        translated = utils.translate_char(key)
        assert len(translated) == 1, '`f`, `t`, `F`, `T` only accept a single char'
        self._inp = translated
        return True

    def translate(self, state):
        cmd = {}
        if self.inclusive:
            state.last_char_search_command = 'vi_f'
        else:
            state.last_char_search_command = 'vi_t'
        state.last_character_search =  self.inp
        cmd['motion'] = '_vi_find_in_line'
        cmd['motion_args'] = {'char': self.inp,
                              'mode': state.mode,
                              'count': state.count,
                              'inclusive': self.inclusive,
                              }
        return cmd


@keys.assign(seq=seqs.A, modes=[modes.OPERATOR_PENDING,
                                modes.VISUAL,
                                modes.VISUAL_BLOCK])
class ViATextObject(ViMotionDef):
    """
    Vim: `a`
    """

    def __init__(self, inclusive=False, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True
        self.inclusive = inclusive

    # TODO: rename to "vi_a_text_object".
        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        assert len(key) == 1, '`a` only accepts a single char'
        self._inp = key
        return True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_select_text_object'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'text_object': self.inp,
                              'inclusive': True,
                              }
        return cmd


@keys.assign(seq=seqs.I, modes=[modes.OPERATOR_PENDING,
                                modes.VISUAL,
                                modes.VISUAL_BLOCK])
class ViITextObject(ViMotionDef):
    """
    Vim: `i`
    """

    def __init__(self, inclusive=False, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True
        self.inclusive = inclusive

        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        assert len(key) == 1, '`i` only accepts a single char'
        self._inp = key
        return True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_select_text_object'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'text_object': self.inp,
                              'inclusive': False,
                              }
        return cmd


@keys.assign(seq=seqs.BIG_T, modes=_MODES_MOTION)
@keys.assign(seq=seqs.BIG_F, modes=_MODES_MOTION, inclusive=True)
class ViSearchCharBackward(ViMotionDef):
    """
    Vim: `T`, `F`
    """

    def __init__(self, inclusive=False, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self._serializable.append('inclusive')
        self.scroll_into_view = True
        self.updates_xpos = True
        self.inclusive = inclusive

        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        translated = utils.translate_char(key)
        assert len(translated) == 1, '`t` only accepts a single char'
        self._inp = translated
        return True

    def translate(self, state):
        cmd = {}
        if self.inclusive:
            state.last_char_search_command = 'vi_big_f'
        else:
            state.last_char_search_command = 'vi_big_t'
        state.last_character_search = self.inp
        cmd['motion'] = '_vi_reverse_find_in_line'
        cmd['motion_args'] = {'char': self.inp,
                              'mode': state.mode,
                              'count': state.count,
                              'inclusive': self.inclusive,
                              }
        return cmd


@keys.assign(seq=seqs.SLASH, modes=_MODES_MOTION)
class ViSearchForward(ViMotionDef):
    """
    Vim: `/`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

        self.input_parser = parser_def(command='_vi_slash',
                                       interactive_command='_vi_slash',
                                       type=input_types.VIA_PANEL,
                                       on_done=None,
                                       input_param='default')

    @property
    def accept_input(self):
        if not self.inp:
            return True
        return not self.inp.lower().endswith('<cr>')

    def accept(self, key):
        self._inp += key
        return True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_slash'
        cmd['motion_args'] = {}

        return cmd


class ViSearchForwardImpl(ViMotionDef):
    """
    Vim: --
    """

    def __init__(self, *args, term='', **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self._inp = term
        self.updates_xpos = True

    def translate(self, state):
        if not self.inp:
            self._inp = state.last_buffer_search
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_slash_impl'
        cmd['motion_args'] = {'search_string': self.inp,
                              'mode': state.mode,
                              'count': state.count,
                              }

        return cmd


@keys.assign(seq=seqs.QUESTION_MARK, modes=_MODES_MOTION)
class ViSearchBackward(ViMotionDef):
    """
    Vim: `?`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

        self.input_parser = parser_def(command='_vi_question_mark',
                                       interactive_command='_vi_question_mark',
                                       type=input_types.VIA_PANEL,
                                       on_done=None,
                                       input_param='default')

    @property
    def accept_input(self):
        if not self.inp:
            return True
        return not self.inp.lower().endswith('<cr>')

    def accept(self, key):
        self._inp += key
        return True

    def translate(self, state):
        cmd = {}
        cmd['motion'] = '_vi_question_mark'
        cmd['motion_args'] = {}
        return cmd


class ViSearchBackwardImpl(ViMotionDef):
    """
    Vim: --
    """

    def __init__(self, *args, term='', **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True
        self._inp = term

    def translate(self, state):
        if not self.inp:
            self._inp = state.last_buffer_search
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_question_mark_impl'
        cmd['motion_args'] = {'search_string': self.inp,
                              'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.CTRL_X_CTRL_L, modes=[modes.INSERT])
class ViInsertLineWithCommonPrefix(ViOperatorDef):
    """
    Vim: `i_CTRL_X_CTRL_L`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_x_ctrl_l'
        cmd['action_args'] = {'mode': state.mode,
                              'register': state.register,
                              }
        return cmd


@keys.assign(seq=seqs.GM, modes=_MODES_MOTION)
class ViMoveHalfScreenHorizontally(ViMotionDef):
    """
    Vim: `gm`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def translate(self, state):
        cmd = {}

        cmd['motion'] = '_vi_gm'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


@keys.assign(seq=seqs.GC, modes=_MODES_ACTION)
class ViToggleCommentByLines(ViOperatorDef):
    """
    Vim: `gc`

    Non-standard.
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_gc'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


@keys.assign(seq=seqs.G_BIG_C, modes=_MODES_ACTION)
class ViToggleBlockCommentByLines(ViOperatorDef):
    """
    Vim: `gC`

    Non-standard.
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def translate(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_c'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd
