"""
Vim commands used internally by Vintageous that also produce ST commands.

These are the core implementations for all Vim commands.
"""

from Vintageous.vi.utils import modes
from Vintageous.vi.inputs import input_types
from Vintageous.vi.inputs import parser_def
from Vintageous.vi import inputs
from Vintageous.vi import utils

import sublime_plugin


class cmd_types:
    """
    Types of command.
    """
    MOTION          = 1
    ACTION          = 2
    ANY             = 3
    OTHER           = 4
    USER            = 5
    OPEN_NAME_SPACE = 6


class ViCommandDefBase(object):
    """
    Base class for all Vim commands.
    """

    _serializable = ['_inp',]

    def __init__(self):
        self.input_parser = None
        self._inp = ''

    def __getitem__(self, key):
        # XXX: For compatibility. Should be removed eventually.
        return self.__dict__[key]

    @property
    def accept_input(self):
        return False

    @property
    def inp(self):
        """
        Current input for this command.
        """
        return self._inp

    def accept(self, key):
        """
        Processes input for this command.
        """
        _name = self.__class__.__name__
        assert self.input_parser, '{0} does not provide an input parser'.format(_name)
        raise NotImplementedError(
                '{0} must implement .accept()'.format(_name))

    def reset(self):
        self._inp = ''

    def to_json(self, state):
        """
        Returns the command as a valid Json object containing all necessary
        data to be run by Vintageous. This is usually the last step before
        handing the command off to ST.

        Every motion and operator must override this method.

        @state
          The current state.
        """
        raise NotImplementedError('command {0} must implement .to_json()'
                                              .format(self.__class__.__name__)
                                              )

    @classmethod
    def from_json(cls, data):
        """
        Instantiates a command from a valid Json object representing one.

        @data
          Serialized command data as provided by .serialize().
        """
        instance = cls()
        instance.__dict__.update(data)
        return instance

    def serialize(self):
        """
        Returns a valid Json object representing this command in a format
        Vintageous uses internally.
        """
        data = {'name': self.__class__.__name__,
                'data': {k: v for k, v in self.__dict__.items()
                              if k in self._serializable}
                }
        return data


class ViMissingCommandDef(ViCommandDefBase):
    def to_json(self):
        raise TypeError(
            'ViMissingCommandDef should not be used as a runnable command'
            )


class ViMotionDef(ViCommandDefBase):
    """
    Base class for all motions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updates_xpos = False
        self.scroll_into_view = False
        self.type = cmd_types.MOTION


class ViOperatorDef(ViCommandDefBase):
    """
    Base class for all operators.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updates_xpos = False
        self.scroll_into_view = False
        self.motion_required = False
        self.type = cmd_types.ACTION
        self.repeatable = False


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_d'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


class ViInsertLineBefore(ViOperatorDef):
    """
    Vim: `O`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_o'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        state.glue_until_normal_mode = True

        return cmd


class ViInsertLineAfter(ViOperatorDef):
    """
    Vim: `o`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
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


class ViRightDeleteChars(ViOperatorDef):
    """
    Vim: `x`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_x'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


class ViSubstituteChar(ViOperatorDef):
    """
    Vim: `s`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        # XXX: Handle differently from State?
        state.glue_until_normal_mode = True

        cmd = {}
        cmd['action'] = '_vi_s'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


class ViYankByChars(ViOperatorDef):
    """
    Vim: `y`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_y'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_equal'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_greater_than'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_less_than'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


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

    def to_json(self, state):
        # XXX: Implement basic serialization in base class?
        cmd = {}
        cmd['action'] = '_vi_c'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


class ViUndo(ViOperatorDef):
    """
    Vim: `u`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
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


class ViRedo(ViOperatorDef):
    """
    Vim: `C-r`
    """

    def __init__(self, inclusive=False, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_r'
        cmd['action_args'] = {'count': state.count, 'mode': state.mode}
        return cmd


class ViDeleteToEol(ViOperatorDef):
    """
    Vim: `D`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_d'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


class ViChangeToEol(ViOperatorDef):
    """
    Vim: `C`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_c'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register
                              }
        return cmd


class ViChangeToUpperCaseByLines(ViOperatorDef):
    """
    Vim: `gUU`, `gUgU`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_u_big_u'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViChangeLine(ViOperatorDef):
    """
    Vim: `cc`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        state.glue_until_normal_mode = True

        cmd = {}
        cmd['action'] = '_vi_cc_action'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViDeleteLine(ViOperatorDef):
    """
    Vim: `dd`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_dd_action'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViEnterReplaceMode(ViOperatorDef):
    """
    Vim: `R`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_enter_replace_mode'
        cmd['action_args'] = {}
        state.glue_until_normal_mode = True
        return cmd


class ViIndentLine(ViOperatorDef):
    """
    Vim: `>>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_greater_than_greater_than'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViChangeToLowerCaseByLines(ViOperatorDef):
    """
    Vim: `guu`, `gugu`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_guu'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_gu'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViReindentLine(ViOperatorDef):
    """
    Vim: `==`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_equal_equal'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViUnindentLine(ViOperatorDef):
    """
    Vim: `<<`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_less_than_less_than'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViYankLine(ViOperatorDef):
    """
    Vim: `yy`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_yy'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }
        return cmd


class ViInvertCaseByLines(ViOperatorDef):
    """
    Vim: `g~~`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_tilde_g_tilde'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViForceInvertCaseByChars(ViOperatorDef):
    """
    Vim: `~`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_tilde'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViSubstituteByLines(ViOperatorDef):
    """
    Vim: `S`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_s_action'
        cmd['action_args'] = {'mode': state.mode, 'count': 1, 'register': state.register}
        state.glue_until_normal_mode = True
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_tilde'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


# TODO: Duplicated.
class ViChangeToUpperCaseByChars(ViOperatorDef):
    """
    Vim: `~`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.motion_required = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_tilde'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViJoinLines(ViOperatorDef):
    """
    Vim: `J`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}

        if state.mode == modes.SELECT:
            # Exits select mode.
            cmd['action'] = '_vi_select_big_j'
            cmd['action_args'] = {'mode': state.mode, 'count': state.count}
            return cmd

        cmd['action'] = '_vi_big_j'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViSubtractFromNumber(ViOperatorDef):
    """
    Vim: `C-x`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_modify_numbers'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'subtract': True,
                              }
        return cmd


class ViAddToNumber(ViOperatorDef):
    """
    Vim: `C-a`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_modify_numbers'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViCopyLine(ViOperatorDef):
    """
    Vim: `yy`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True
        self.repeatable = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_y'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_j'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'separator': None}
        return cmd


class ViEnterVisualMode(ViOperatorDef):
    """
    Vim: `v`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_enter_visual_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


class ViScrollToScreenTop(ViOperatorDef):
    """
    Vim: `z<CR>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_z_enter'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViScrollToScreenBottom(ViOperatorDef):
    """
    Vim: `zb`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_z_minus'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViScrollToScreenCenter(ViOperatorDef):
    """
    Vim: `zz`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_zz'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_gq'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViPasteAfter(ViOperatorDef):
    """
    Vim: `p`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_p'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }

        return cmd


class ViPasteBefore(ViOperatorDef):
    """
    Vim: `P`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_p'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              }

        return cmd


class ViLeftDeleteChar(ViOperatorDef):
    """
    Vim: `X`
    """

    # TODO: z- and zb are different.
    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_x'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count, 'register': state.register}

        return cmd


class ViSendViewToRightPane(ViOperatorDef):
    """
    Vim: `<C-W-L>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_big_l'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViSendViewToLeftPane(ViOperatorDef):
    """
    Vim: `<C-W-H>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_big_h'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViActivateNextTab(ViOperatorDef):
    """
    Vim: `gt`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_gt'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViActivatePreviousTab(ViOperatorDef):
    """
    Vim: `gT`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_t'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViActivatePaneToTheRight(ViOperatorDef):
    """
    Vim: `<C-W-l>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_l'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViActivatePaneToTheLeft(ViOperatorDef):
    """
    Vim: `<C-W-h>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_h'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViSplitVertically(ViOperatorDef):
    """
    Vim: `<C-W-v>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_v'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViDestroyCurrentPane(ViOperatorDef):
    """
    Vim: `<C-W-q>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_w_q'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViEnterVisualLineMode(ViOperatorDef):
    """
    Vim: `V`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_enter_visual_line_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


class ViRestoreVisualSelections(ViOperatorDef):
    """
    Vim: `gv`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_gv'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class StToggleSidebar(ViOperatorDef):
    """
    Vintageous: `<C-K-b>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'toggle_side_bar'
        cmd['action_args'] = {}
        return cmd


class StFinInFiles(ViOperatorDef):
    """
    Vintageous: `Ctrl+Shift+F`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'show_panel'
        cmd['action_args'] = {'panel': 'find_in_files'}
        return cmd


class StGotoSymbolInProject(ViOperatorDef):
    """
    Vintageous: `<C-S-f12>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'goto_symbol_in_project'
        cmd['action_args'] = {}
        return cmd


class StGotoSymbolInFile(ViOperatorDef):
    """
    Vintageous: `<C-f12>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'show_overlay'
        cmd['action_args'] = {'overlay': 'goto', 'text': '@'}
        return cmd


class StGotoDefinition(ViOperatorDef):
    """
    Vintageous: `f12`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'goto_definition'
        cmd['action_args'] = {}
        return cmd


class StToggleBookmark(ViOperatorDef):
    """
    Vintageous: `<C-f2>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'toggle_bookmark'
        cmd['action_args'] = {}
        return cmd


class StClearBookmarks(ViOperatorDef):
    """
    Vintageous: `<C-S-f2>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'clear_bookmarks'
        cmd['action_args'] = {}
        return cmd


class StPrevBookmark(ViOperatorDef):
    """
    Vintageous: `f2`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'prev_bookmark'
        cmd['action_args'] = {}
        return cmd


class StNextBookmark(ViOperatorDef):
    """
    Vintageous: `<S-f2>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'next_bookmark'
        cmd['action_args'] = {}
        return cmd


class ViRepeat(ViOperatorDef):
    """
    Vim: `.`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_dot'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'repeat_data': state.repeat_data,
                              }
        return cmd


class ViOpenRegisterFromInsertMode(ViOperatorDef):
    """
    TODO: Implement this.
    Vim: `<C-r>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_r'
        cmd['action_args'] = {'count': state.count, 'mode': state.mode}
        return cmd


class ViScrollByLinesUp(ViOperatorDef):
    """
    Vim: `<C-y>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_y'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViUndoLineChanges(ViOperatorDef):
    """
    TODO: Implement this.
    Vim: `U`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}

        if state.mode in (modes.VISUAL,
                          modes.VISUAL_LINE,
                          modes.VISUAL_BLOCK):
            cmd['action'] = '_vi_visual_big_u'
            cmd['action_args'] = {'count': state.count, 'mode': state.mode}
            return cmd

        return {}


class ViScrollByLinesDown(ViOperatorDef):
    """
    Vim: `<C-e>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_ctrl_e'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class StToggleFullScreen(ViOperatorDef):
    """
    Vintageous: `f11`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'toggle_full_screen'
        cmd['action_args'] = {}
        return cmd


class StBuild(ViOperatorDef):
    """
    Vintageous: `f7`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'build'
        cmd['action_args'] = {}
        return cmd


class StFindPrev(ViOperatorDef):
    """
    Vintageous: `Ctrl+F4`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'find_prev'
        cmd['action_args'] = {}
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_at'
        cmd['action_args'] = {'name': self.inp,
                              'count': state.count}
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_q'
        cmd['action_args'] = {'name': self.inp}
        return cmd


class StFindNext(ViOperatorDef):
    """
    Vintageous: `f3`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'find_next'
        cmd['action_args'] = {}
        return cmd


class StFindNextResult(ViOperatorDef):
    """
    Vintageous: `f4`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'next_result'
        cmd['action_args'] = {}
        return cmd


class StFindPrevResult(ViOperatorDef):
    """
    Vintageous: `Shift+F4`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'prev_result'
        cmd['action_args'] = {}
        return cmd


class ViQuit(ViOperatorDef):
    """
    TODO: Is this used?
    Vim: `ZZ`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'ex_quit'
        cmd['action_args'] = {'forced': True, 'count': state.count}
        return cmd


class ViEnterSelectModeForSearch(ViOperatorDef):
    """
    Vim: `gH`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_g_big_h'
        cmd['action_args'] = {}
        return cmd


class StPrevResult(ViOperatorDef):
    """
    Vim: `Shift+F4`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'prev_result'
        cmd['action_args'] = {}
        return cmd


class ViEnterSelectMode(ViOperatorDef):
    """
    Vim: `gh`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_enter_select_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


class ViEnterVisualBlockMode(ViOperatorDef):
    """
    Vim: `<C-v>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_enter_visual_block_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


class StShowGotoAnything(ViOperatorDef):
    """
    Vintageous: `<C-p>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'show_overlay'
        cmd['action_args'] = {'overlay': 'goto', 'show_files': True}
        return cmd


class StShowSwitchProject(ViOperatorDef):
    """
    Vintageous: `<C-M-p>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'prompt_select_workspace'
        cmd['action_args'] = {}
        return cmd


class StShowCommandPalette(ViOperatorDef):
    """
    Vintageous: `<C-S-p>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'show_overlay'
        cmd['action_args'] = {'overlay': 'command_palette'}
        return cmd


class ViEnterInserMode(ViOperatorDef):
    """
    Vim: `i`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_enter_insert_mode'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        state.glue_until_normal_mode = True
        return cmd


class ViEnterNormalMode(ViOperatorDef):
    """
    Vim: `<esc>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_enter_normal_mode'
        cmd['action_args'] = {'mode': state.mode}
        return cmd


class ViInsertAfterChar(ViOperatorDef):
    """
    Vim: `a`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_a'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        if state.mode != modes.SELECT:
            state.glue_until_normal_mode = True

        return cmd


class ViInsertAtEol(ViOperatorDef):
    """
    Vim: `A`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_a'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        if state.mode != modes.SELECT:
            state.glue_until_normal_mode = True

        return cmd


class ViInsertAtBol(ViOperatorDef):
    """
    Vim: `I`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_big_i'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}

        if state.mode != modes.SELECT:
            state.glue_until_normal_mode = True

        return cmd


class ViEnterCommandLineMode(ViOperatorDef):
    """
    Vim: `:`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'vi_colon_input'
        cmd['action_args'] = {}
        return cmd


class StSortLines(ViOperatorDef):
    """
    Vintageous: `f9`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'sort_lines'
        cmd['action_args'] = {'case_sensitive': False}
        return cmd


class ViShowFileStatus(ViOperatorDef):
    """
    Vim: `<C-g>`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'ex_file'
        cmd['action_args'] = {}
        return cmd


class ViExitEditor(ViOperatorDef):
    """
    Vim: `ZQ`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'ex_quit'
        cmd['action_args'] = {'forced': True, 'count': state.count}
        return cmd


class ViCloseFile(ViOperatorDef):
    """
    Vim: `ZZ`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'ex_exit'
        cmd['action_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class StToggleSpelling(ViOperatorDef):
    """
    Vintageous: `f6`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = 'toggle_setting'
        cmd['action_args'] = {'setting': 'spell_check'}
        return cmd


class ViGotoSymbolInProject(ViOperatorDef):
    """
    Vim: `gD`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['action'] = '_vi_go_to_symbol'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'globally': True}
        return cmd


class ViDeselectInstance(ViOperatorDef):
    """
    Vim: `k`
    """

    def __init__(self, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        """
        Non-standard.
        """
        if state.mode != modes.SELECT:
            raise ValueError('bad mode, expected mode_select, got {0}'.format(state.mode))

        cmd = {}
        cmd['action'] = 'soft_undo'
        cmd['action_args'] = {} # {'mode': state.mode, 'count': state.count}
        return cmd


class ViGotoSymbolInFile(ViMotionDef):
    """
    Vim: `gD`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_go_to_symbol'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'globally': False}
        return cmd


class ViMoveRightByChars(ViMotionDef):
    """
    Vim: `l`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}

        if state.mode == modes.SELECT:
            cmd['motion'] = 'find_under_expand_skip'
            cmd['motion_args'] = {}
            return cmd

        cmd['motion'] = '_vi_l'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViShiftEnterMotion(ViMotionDef):
    """
    Vim: `<S-CR>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_shift_enter'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveByWordsBackward(ViMotionDef):
    """
    Vim: `b`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_b'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveByBigWordsBackward(ViMotionDef):
    """
    Vim: `B`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_b'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveByBigWords(ViMotionDef):
    """
    Vim: `W`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_w'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveByWordEnds(ViMotionDef):
    """
    Vim: `e`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_e'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViGotoScreenTop(ViMotionDef):
    """
    Vim: `H`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_h'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveByWordEndsBackward(ViMotionDef):
    """
    Vim: `ge`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ge'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViGotoScreenBottom(ViMotionDef):
    """
    Vim: `L`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_l'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViGotoScreenMiddle(ViMotionDef):
    """
    Vim: `M`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_m'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveHalfScreenDown(ViMotionDef):
    """
    Vim: `<C-d>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ctrl_d'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveHalfScreenUp(ViMotionDef):
    """
    Vim: `<C-u>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ctrl_u'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveScreenDown(ViMotionDef):
    """
    Vim: `<C-f>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ctrl_f'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveScreenUp(ViMotionDef):
    """
    Vim: `<C-b>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_ctrl_b'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_backtick'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'character': self.inp}
        return cmd


class ViMoveToEol(ViMotionDef):
    """
    Vim: `$`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_dollar'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViMotionEnter(ViMotionDef):
    """
    Vim: `<CR>`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_enter'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViMoveToSoftEol(ViMotionDef):
    """
    Vim: `g_`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_g__'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveByScreenLineDown(ViMotionDef):
    """
    Vim: `gj`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_gj'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViMoveByScreenLineUp(ViMotionDef):
    """
    Vim: `gk`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_gk'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViMoveByBlockUp(ViMotionDef):
    """
    Vim: `{`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_left_brace'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViRepeatCharSearchForward(ViMotionDef):
    """
    Vim: `;`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_semicolon'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


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

    def to_json(self, state):
        if self.inp == "'":
            return vi_quote_quote(state, **kwargs)

        cmd = {}
        cmd['is_jump'] = True

        cmd['motion'] = '_vi_quote'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'character': self.inp,
                              }
        return cmd


class ViMoveByBlockDown(ViMotionDef):
    """
    Vim: `}`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_right_brace'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViMoveBySentenceUp(ViMotionDef):
    """
    Vim: `(`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_left_paren'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViMoveBySentenceDown(ViMotionDef):
    """
    Vim: `)`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_right_paren'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViMoveBySquareBracketUp(ViMotionDef):
    """
    Vim: `[`
    """
    # TODO: Revise this.
    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['is_jump'] = True
        cmd['motion'] = '_vi_left_square_bracket'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              }
        return cmd


class ViGotoLinesPercent(ViMotionDef):
    """
    Vim: `%`
    """
    # TODO: Revise this.
    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_percent'

        percent = None
        if state.motion_count or state.action_count:
            percent = state.count

        cmd['motion_args'] = {'mode': state.mode, 'percent': percent}

        return cmd


class ViRepeatCharSearchBackward(ViMotionDef):
    """
    Vim: `,`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        forward = state.last_char_search_command in ('vi_t', 'vi_f')
        inclusive = state.last_char_search_command in ('vi_f', 'vi_big_f')

        cmd['motion'] = ('_vi_find_in_line' if not forward
                                            else '_vi_reverse_find_in_line')
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count,
                              'char': state.last_character_search,
                              'change_direction': False,
                              'inclusive': inclusive,
                              'skipping': not inclusive}

        return cmd


class ViMoveByLineCols(ViMotionDef):
    """
    Vim: `|`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_pipe'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveByBigWordEnds(ViMotionDef):
    """
    Vim: `E`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_e'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveLeftByChars(ViMotionDef):
    """
    Vim: `h`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}

        if state.mode == modes.SELECT:
            cmd['motion'] = 'find_under_expand_skip'
            cmd['motion_args'] = {}
            return cmd

        cmd['motion'] = '_vi_h'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViMoveByWords(ViMotionDef):
    """
    Vim: `w`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.updates_xpos = True
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_w'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}

        return cmd


class ViMoveDownByLines(ViMotionDef):
    """
    Vim: `j`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}

        if state.mode == modes.SELECT:
            cmd['motion'] = '_vi_select_j'
            cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
            return cmd

        cmd['motion'] = '_vi_j'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count, 'xpos': state.xpos}
        return cmd


class ViMoveUpByLines(ViMotionDef):
    """
    Vim: `k`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_k'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'xpos': state.xpos}
        return cmd


class ViMoveToBol(ViMotionDef):
    """
    Vim: `^`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_hat'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


class ViMoveToHardBol(ViMotionDef):
    """
    Vim: `0`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_zero'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


class ViRepeatSearchForward(ViMotionDef):
    """
    Vim: `;`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_n'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'search_string': state.last_buffer_search}

        return cmd


class ViRepeatSearchBackward(ViMotionDef):
    """
    Vim: `,`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_big_n'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'search_string': state.last_buffer_search}

        return cmd


class ViFindWord(ViMotionDef):
    """
    Vim: `*`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_star'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_octothorp'
        cmd['motion_args'] = {'count': state.count, 'mode': state.mode}

        return cmd


class ViOpenNameSpace(ViMotionDef):
    """
    Vim: `g`, `z`, ...
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)

    def to_json(self, state):
        return {}


class ViOpenRegister(ViMotionDef):
    """
    Vim: `"`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)

    def to_json(self, state):
        return {}


class ViGotoBof(ViMotionDef):
    """
    Vim: `gg`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}
        # cmd['is_jump'] = True

        if state.action_count or state.motion_count:
            cmd['motion'] = '_vi_go_to_line'
            cmd['motion_args'] = {'line': state.count, 'mode': state.mode}
            return cmd

        cmd['motion'] = '_vi_gg'
        cmd['motion_args'] = {'mode': state.mode, 'count': state.count}
        return cmd


class ViGotoEof(ViMotionDef):
    """
    Vim: `G`
    """

    def __init__(self, *args, **kwargs):
        ViMotionDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True

    def to_json(self, state):
        cmd = {}

        if state.action_count or state.motion_count:
            cmd['motion'] = '_vi_go_to_line'
            cmd['motion_args'] = {'line': state.count, 'mode': state.mode}
        else:
            cmd['motion'] = '_vi_big_g'
            cmd['motion_args'] = {'mode': state.mode}

        return cmd


class ViReplaceCharacters(ViOperatorDef):
    """
    Vim: `r`
    """

    def __init__(self, inclusive=False, *args, **kwargs):
        ViOperatorDef.__init__(self, *args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True

        self.input_parser = parser_def(command=inputs.one_char,
                       interactive_command=None,
                       input_param=None,
                       on_done=None,
                       type=input_types.INMEDIATE)

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        assert len(key) == 1, '`r` only accepts a single char'
        self._inp = utils.translate_char(key)
        return True

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_r'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'register': state.register,
                              'char': self.inp,
                              }
        return cmd


class ViSetMark(ViOperatorDef):
    """
    Vim: `m`
    """

    def __init__(self, inclusive=False, *args, **kwargs):
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

    def to_json(self, state):
        cmd = {}
        cmd['action'] = '_vi_m'
        cmd['action_args'] = {'mode': state.mode,
                              'count': state.count,
                              'character': self.inp,
                              }
        return cmd


class ViSearchCharForward(ViMotionDef):
    """
    Vim: `f`
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
        assert len(key) == 1, '`f`, `t`, `F`, `T` only accept a single char'
        self._inp = key
        return True

    def to_json(self, state):
        cmd = {}
        state.last_char_search_command = 'vi_f'
        state.last_character_search = self.inp
        cmd['motion'] = '_vi_find_in_line'
        cmd['motion_args'] = {'char': self.inp,
                              'mode': state.mode,
                              'count': state.count,
                              'inclusive': self.inclusive,
                              }
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_select_text_object'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'text_object': self.inp,
                              'inclusive': True,
                              }
        return cmd


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

    def to_json(self, state):
        cmd = {}
        cmd['motion'] = '_vi_select_text_object'
        cmd['motion_args'] = {'mode': state.mode,
                              'count': state.count,
                              'text_object': self.inp,
                              'inclusive': False,
                              }
        return cmd


class ViSearchCharBackward(ViMotionDef):
    """
    Vim: `t`
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
        assert len(key) == 1, '`t` only accepts a single char'
        self._inp = key
        return True

    def to_json(self, state):
        cmd = {}
        state.last_char_search_command = 'vi_big_f'
        state.last_character_search = self.inp
        cmd['motion'] = '_vi_reverse_find_in_line'
        cmd['motion_args'] = {'char': self.inp,
                              'mode': state.mode,
                              'count': state.count,
                              'inclusive': self.inclusive,
                              }
        return cmd


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

    def to_json(self, state):
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

    def to_json(self, state):
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

    def to_json(self, state):
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

    def to_json(self, state):
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
