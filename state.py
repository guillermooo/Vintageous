import sublime
import sublime_plugin

import threading

from Vintageous.vi import motions
from Vintageous.vi import actions
from Vintageous.vi.constants import (MODE_INSERT, MODE_NORMAL, MODE_VISUAL,
                         MODE_VISUAL_LINE, MODE_NORMAL_INSERT,
                         _MODE_INTERNAL_NORMAL)
from Vintageous.vi.constants import mode_to_str
from Vintageous.vi.constants import digraphs
from Vintageous.vi.constants import DIGRAPH_MOTION
from Vintageous.vi import constants
from Vintageous.vi.settings import SettingsManager, VintageSettings, SublimeSettings
from Vintageous.vi.registers import Registers
from Vintageous.vi import registers


def new_vi_cmd_data(state):
    # XXX: Make this a method of VintageState instead? It's too tightly coupled with it anyway.
    """Returns a 'zeroed' vi_cmd_data instance.
    """

    # TODO: Encapsulate vi_cmd_data in a class?
    #
    # vi_cmd_data is a key data structure that drives the action/motion execution.
    # Keys and values must be valid JSON data types, because the data structure ends up being an
    # argument to an ST command.
    vi_cmd_data = {
        'pre_motion': None,
        'motion': {},
        # Whether the user needs to provide a motion. If there is no user-provided motion, a
        # motion specified by an action could still be run before the action.
        'motion_required': True,
        'action': {},
        'post_action': None,
        'count': state.count,
        'pre_every_motion': None,
        'post_every_motion': None,
        # This is the only hook that takes a list of commands to execute.
        # Specify commands as a list of [command, args] elements (don't use tuples).
        'post_motion': [],
        # Set to True if the command must be able to populate the registers. This will cause
        # Vintageous to propagate copied text to the unnamed register as needed.
        'can_yank': False,
        # Some commands operate CHARACTERWISE but always yank LINEWISE, so we need this.
        'yanks_linewise': False,
        # We set this to the user-supplied information.
        'register': state.register,
        'mode': MODE_NORMAL,
        'reposition_caret': None,
        'follow_up_mode': None,
        # Some digraphs can be computed on their own, like cc and dd, but others require an
        # explicit "wait for next command name" status, like gU, gu, etc. This property helps
        # with that.
        'is_digraph_start': False,
        # User input, such as arguments to the t and f commands.
        # TODO: Try to unify user-input collection (both for registers and this kind of
        # argument).
        'user_input': state.user_input,
        # TODO: Interim solution to avoid problems with this step. Many commands don't need
        # this and it's causing quite some trouble. Let commands specify an explicit command
        # to reorient the caret as occurs with other hooks.
        '__reorient_caret': False,
        # Whether the motion is considered a jump.
        'is_jump': False,
        # Some actions must be cancelled if the selections didn't change after the motion.
        # Others, on the contrary, must always go ahead.
        'cancel_action_if_motion_fails': False,
        # Some commands that don't take motions need to be repeated, but currently ViRun only
        # repeats the motion, so tell global state to repeat the action. An example would be
        # the J command.
        '_repeat_action': False,
        # Search string used last to find text in the buffer (like the / command).
        'last_buffer_search': state.last_buffer_search,
        # Search character used last to find text in the line (like the f command).
        'last_character_search': state.last_character_search,
        # Whether we want to save the original selections to restore them after the command.
        'restore_original_carets': False,
        # We keep track of the caret's x position so vertical motions like j, k can restore it
        # as needed. This item must not ever be reset. All horizontal motions must update it.
        # Vertical motions must adjust the selections .b end to factor in this data.
        'xpos': state.xpos,
        # Indicates whether xpos needs to be updated. Only vertical motions j and k need not
        # update xpos.
        'must_update_xpos': True,        
        # Whether we should make sure to show the first selection.
        'scroll_into_view': True,
    }
    
    return vi_cmd_data


def _init_vintageous(view):
    # Operate only on actual views.
    if (not getattr(view, 'settings') or
            view.settings().get('is_widget')):
        return

    state = VintageState(view)
    if state.mode not in (MODE_VISUAL, _MODE_INTERNAL_NORMAL,
                          MODE_VISUAL_LINE):
        state.reset()
        state.enter_normal_mode()


def plugin_loaded():
    view = sublime.active_window().active_view()
    _init_vintageous(view)


def unload_handler():
    for w in sublime.windows():
        for v in w.views():
            v.settings().set('command_mode', False)
            v.settings().set('inverse_caret_state', False)
            v.settings().set('vintage', {})


class VintageState(object):
    """ Stores per-view state using View.Settings() for storage.
    """

    # Makes yank data globally accesible.
    registers = Registers()

    def __init__(self, view):
        self.view = view
        # We have two types of settings: vi-specific (settings.vi) and regular
        # ST view settings (settings.view).
        self.settings = SettingsManager(self.view)

    def enter_normal_mode(self):
        self.settings.view['command_mode'] = True
        self.settings.view['inverse_caret_state'] = True
        # Make sure xpos is up to date when we return to normal mode. Insert mode does not affect
        # xpos.
        # XXX: Why is insert mode resetting xpos? xpos should never be reset?
        self.xpos = None if not self.view.sel() else self.view.rowcol(self.view.sel()[0].b)[1]
        self.mode = MODE_NORMAL

    def enter_visual_line_mode(self):
        self.mode = MODE_VISUAL_LINE

    def enter_insert_mode(self):
        self.settings.view['command_mode'] = False
        self.settings.view['inverse_caret_state'] = False
        self.mode = MODE_INSERT

    def enter_visual_mode(self):
        self.mode = MODE_VISUAL

    def enter_normal_insert_mode(self):
        self.mode = MODE_NORMAL_INSERT
        self.settings.view['command_mode'] = False
        self.settings.view['inverse_caret_state'] = False

    @property
    def mode(self):
        return self.settings.vi['mode']

    @mode.setter
    def mode(self, value):
        self.settings.vi['mode'] = value

    @property
    def action(self):
        return self.settings.vi['action']

    @action.setter
    def action(self, name):
        action = self.settings.vi['action']
        target = 'action'

        # Check for digraphs like cc, dd, yy.
        if action and name:
            name, type_ = digraphs.get((action, name), ('', None))
            # Some motion digraphs are captured as actions, but need to be stored as motions
            # instead so that the vi command is evaluated correctly.
            if type_ == DIGRAPH_MOTION:
                target = 'motion'
                self.settings.vi['action'] = None

        # Avoid recursion. The .reset() method will try to set this property to None, not ''.
        if name == '':
            self.reset()
            return

        self.settings.vi[target] = name

    @property
    def motion(self):
        return self.settings.vi['motion']

    @motion.setter
    def motion(self, name):
        self.settings.vi['motion'] = name

    @property
    def motion_digits(self):
        return self.settings.vi['motion_digits'] or []

    @motion_digits.setter
    def motion_digits(self, value):
        self.settings.vi['motion_digits'] = value

    def push_motion_digit(self, value):
        digits = self.settings.vi['motion_digits']
        if not digits:
            self.settings.vi['motion_digits'] = [value]
            return
        digits.append(value)
        self.settings.vi['motion_digits'] = digits

    @property
    def action_digits(self):
        return self.settings.vi['action_digits'] or []

    @action_digits.setter
    def action_digits(self, value):
        self.settings.vi['action_digits'] = value

    def push_action_digit(self, value):
        digits = self.settings.vi['action_digits']
        if not digits:
            self.settings.vi['action_digits'] = [value]
            return
        digits.append(value)
        self.settings.vi['action_digits'] = digits

    @property
    def count(self):
        motion_count = self.motion_digits and int(''.join(self.motion_digits)) or 1
        action_count = self.action_digits and int(''.join(self.action_digits)) or 1

        return (motion_count * action_count)

    @property
    def register(self):
        return self.settings.vi['register'] or None

    @property
    def expecting_register(self):
        return self.settings.vi['expecting_register']

    @expecting_register.setter
    def expecting_register(self, value):
        self.settings.vi['expecting_register'] = value

    @register.setter
    def register(self, name):
        # TODO: Check for valid register name.
        self.settings.vi['register'] = name
        self.expecting_register = False

    @property
    def expecting_user_input(self):
        return self.settings.vi['expecting_user_input']

    @expecting_user_input.setter
    def expecting_user_input(self, value):
        self.settings.vi['expecting_user_input'] = value

    @property
    def user_input(self):
        return self.settings.vi['user_input'] or None

    @user_input.setter
    def user_input(self, value):
        self.settings.vi['user_input'] = value
        self.expecting_user_input = False

    @property
    def last_buffer_search(self):
        return self.settings.vi['last_buffer_search'] or None

    @last_buffer_search.setter
    def last_buffer_search(self, value):
        self.settings.vi['last_buffer_search'] = value
        self.expecting_user_input = False

    @property
    def last_character_search(self):
        return self.settings.vi['last_character_search'] or None

    @last_character_search.setter
    def last_character_search(self, value):
        self.settings.vi['last_character_search'] = value
        self.expecting_user_input = False

    @property
    def xpos(self):
        xpos = self.settings.vi['xpos']
        return xpos if isinstance(xpos, int) else None

    @xpos.setter
    def xpos(self, value):
        self.settings.vi['xpos'] = value

    def parse_motion(self):
        vi_cmd_data = new_vi_cmd_data(self)

        # This should happen only at initialization.
        # XXX: This is effectively zeroing xpos. Shouldn't we move this into new_vi_cmd_data()?
        if vi_cmd_data['xpos'] is None:
            xpos = 0
            if self.view.sel():
                # XXX: Improvee this with .rowcol()
                xpos = self.view.sel()[0].b - self.view.line(self.view.sel()[0].b).a
            self.xpos = xpos
            vi_cmd_data['xpos'] = xpos

        # Make sure we run NORMAL mode actions in _MODE_INTERNAL_NORMAL mode.
        # XXX: This is effectively zeroing xpos. Shouldn't we move this into new_vi_cmd_data()?
        if self.mode in (MODE_VISUAL, MODE_VISUAL_LINE) or (self.motion and self.action):
            if self.mode not in (MODE_VISUAL, MODE_VISUAL_LINE):
                self.mode = _MODE_INTERNAL_NORMAL
                vi_cmd_data['mode'] = _MODE_INTERNAL_NORMAL
            else:
                vi_cmd_data['mode'] = self.mode

        motion = self.motion
        motion_func = None
        if motion:
            motion_func = getattr(motions, self.motion)
        if motion_func:
            vi_cmd_data = motion_func(vi_cmd_data)

        return vi_cmd_data

    def parse_action(self, vi_cmd_data):
        action_func = getattr(actions, self.action)
        if action_func:
            vi_cmd_data = action_func(vi_cmd_data)

        # Notify global state to go ahead with the command if there are selections and the action
        # is ready to be run (which is almost always the case except for some digraphs).
        # NOTE: By virtue of checking for non-empty selections instead of an explicit mode,
        # the user can run actions on selections created outside of Vintageous.
        # This seems to work well.
        if (self.view.has_non_empty_selection_region() and
            not vi_cmd_data['is_digraph_start']):
                vi_cmd_data['motion_required'] = False

        return vi_cmd_data

    def run(self):
        """Examines the current state and decides whether to actually run the action/motion.
        """

        # Action + motion, like in "3dj".
        if self.action and self.motion:
            vi_cmd_data = self.parse_motion()
            vi_cmd_data = self.parse_action(vi_cmd_data)

            self.view.run_command('vi_run', vi_cmd_data)
            self.reset()

        # Motion only, like in "3j".
        elif self.motion:
            self.view.run_command('vi_run', self.parse_motion())
            self.reset()

        # Action only, like in "d" or "esc". Some actions can be executed without a motion.
        elif self.action:
            vi_cmd_data = self.parse_motion()
            vi_cmd_data = self.parse_action(vi_cmd_data)

            # In cases like gg, we might receive the motion here, so check for that.
            if self.motion and not self.action:
                self.view.run_command('vi_run', self.parse_motion())
                self.reset()
                self.update_status()
                return

            if not vi_cmd_data['motion_required']:
                self.view.run_command('vi_run', vi_cmd_data)
                self.reset()

        self.update_status()

    def reset(self):
        self.motion = None
        self.action = None
        self.register = None
        self.user_input = None
        self.expecting_register = False
        self.expecting_user_input = False

        # In MODE_NORMAL_INSERT, we temporarily exit NORMAL mode, but when we get back to
        # it, we need to know the repeat digits, so keep them. An example command for this case
        # would be 5ifoobar\n<esc> starting in NORMAL mode.
        if self.mode == MODE_NORMAL_INSERT:
            return

        self.motion_digits = []
        self.action_digits = []

    def update_status(self):
        mode_name = mode_to_str(self.mode) or ""
        mode_name = "-- %s --" % mode_name if mode_name else ""
        sublime.status_message(mode_name)


class VintageStateTracker(sublime_plugin.EventListener):
    def on_load(self, view):
        _init_vintageous(view)

    # def on_activated(self, view):
        # _init_vintageous(view)

    def on_query_context(self, view, key, operator, operand, match_all):
        vintage_state = VintageState(view)

        # TODO: Move contexts to a separate file to reduce clutter.

        if key == "vi_mode_can_push_digit":
            motion_digits = not vintage_state.motion
            action_digits = vintage_state.motion

            if operator == sublime.OP_EQUAL:
                return motion_digits or action_digits
            elif operator == sublime.OP_NOT_EQUAL:
                return False

        # TODO: Perhaps unify all data collection in one single context.
        elif key == 'vi_state_expecting_register':
            if operator == sublime.OP_EQUAL:
                return vintage_state.expecting_register
            elif operator == sublime.OP_NOT_EQUAL:
                return not vintage_state.expecting_register

        # TODO: Perhaps unify all data collection in one single context.
        elif key == 'vi_state_expecting_user_input':
            if operator == sublime.OP_EQUAL:
                return vintage_state.expecting_user_input
            elif operator == sublime.OP_NOT_EQUAL:
                return not vintage_state.expecting_user_input

        # TODO: This context should encompass any state in which the next input character will be
        #       consumed as user-provided input. However, it seems simpler to unify data collection
        #       in one single context to begin with and get rid of this.
        #
        # This context signals when we're expecting the user to provide an arbirtrary char as
        # input for an incomplete command. It helps to disable some key bindings in this event.
        #
        # TODO: Note that offending key bindings seem to always be sequences suchs as ["'", "'"].
        #       We should try to never use them to avoid timeout weirdness and let double commands
        #       use Vintageous' own system for composite commands instead. If sequences exist now,
        #       it's because they seemed easier as a first implementation.
        #
        elif key == 'vi_state_next_character_is_user_input':
            if operator == sublime.OP_EQUAL:
                if operand == True:
                    return (vintage_state.expecting_user_input or
                            vintage_state.expecting_register)
                elif operand == False:
                    return not (vintage_state.expecting_user_input or
                                vintage_state.expecting_register)
            elif operator == sublime.OP_NOT_EQUAL:
                return not (vintage_state.expecting_user_input or
                            vintage_state.expecting_register)

        elif key == 'vi_mode_normal':
            if operator == sublime.OP_EQUAL:
                return vintage_state.mode == MODE_NORMAL
            elif operator == sublime.OP_NOT_EQUAL:
                return vintage_state.mode != MODE_NORMAL

        elif key == 'vi_mode_visual':
            if operator == sublime.OP_EQUAL:
                return vintage_state.mode == MODE_VISUAL
            elif operator == sublime.OP_NOT_EQUAL:
                return vintage_state.mode != MODE_VISUAL

        elif key == 'vi_mode_visual_line':
            if operator == sublime.OP_EQUAL:
                return vintage_state.mode == MODE_VISUAL_LINE
            elif operator == sublime.OP_NOT_EQUAL:
                return vintage_state.mode != MODE_VISUAL_LINE

        elif key == 'vi_mode_visual_any':
            value = vintage_state.mode in (MODE_VISUAL_LINE, MODE_VISUAL)
            if operator == sublime.OP_EQUAL:
                if operand == True:
                    return value
                return not value
            elif operator == sublime.OP_NOT_EQUAL:
                if operand == True:
                    return not value
                return value

        elif key == "vi_mode_cannot_push_0":
            if operator == sublime.OP_EQUAL:
                value = not (vintage_state.motion_digits or
                             vintage_state.action_digits)
                return value

        elif key == "vi_mode_normal_insert":
            value = vintage_state.mode == MODE_NORMAL_INSERT
            if operator == sublime.OP_EQUAL:
                return value
            elif operator == sublime.OP_NOT_EQUAL:
                return not value

        elif key == "vi_has_motion_count":
            value = vintage_state.motion_digits
            if operator == sublime.OP_EQUAL:
                return value
            elif operator == sublime.OP_NOT_EQUAL:
                return not value

        elif key == "vi_has_action":
            value = vintage_state.action
            value = value and (value not in constants.INCOMPLETE_ACTIONS)
            if operator == sublime.OP_EQUAL:
                return value
            elif operator == sublime.OP_NOT_EQUAL:
                return not value

        elif key == "vi_has_incomplete_action":
            value = vintage_state.action in constants.INCOMPLETE_ACTIONS
            if operator == sublime.OP_EQUAL:
                return value
            elif operator == sublime.OP_NOT_EQUAL:
                return not value

        # Used to disable commands that enter normal mode. Input widgets should always operate in
        # insert mode (actually, they should be completely ignored by Vintageous at this stage).
        elif key == 'vi_is_sublime_widget_or_console':
            # !! The following check is based on an implementation detail of Sublime Text. !!
            is_console = False if (getattr(view, 'settings') is not None) else True
            is_widget = view.settings().get('is_widget')
            if operator == sublime.OP_EQUAL:
                if operand is True:
                    return (is_console or is_widget)

                if operand is False:
                    return not (is_console or is_widget)
            elif operator == sublime.OP_NOT_EQUAL:
                if operand is True:
                    return not (is_console or is_widget)

                if operand is False:
                    return (is_console or is_widget)
        return False


class ViFocusRestorerEvent(sublime_plugin.EventListener):
    def __init__(self):
        self.timer = None

    def action(self):
        self.timer = None

    def on_activated(self, view):
        if self.timer:
            # Switching to a view; enter normal mode.
            self.timer.cancel()
            _init_vintageous(view)
        else:
            # Switching back from another application. Ignore.
            pass

    def on_deactivated(self, view):
        self.timer = threading.Timer(0.25, self.action)
        self.timer.start()


class IrreversibleTextCommand(sublime_plugin.TextCommand):
    """ Abstract class.

        The undo stack will ignore commands derived from this class. This is
        useful to prevent global state management commands from shadowing
        commands performing edits to the buffer, which are the important ones
        to keep in the undo history.
    """
    def __init__(self, view):
        sublime_plugin.TextCommand.__init__(self, view)

    def run_(self, edit_token, kwargs):
        if kwargs and 'event' in kwargs:
            del kwargs['event']

        if kwargs:
            self.run(**kwargs)
        else:
            self.run()

    def run(self, **kwargs):
        pass
