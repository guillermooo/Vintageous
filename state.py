import sublime
import sublime_plugin

import threading

from Vintageous.vi import actions
from Vintageous.vi import constants
from Vintageous.vi import motions
from Vintageous.vi import registers
from Vintageous.vi import utils
from Vintageous.vi.cmd_data import CmdData
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import ACTIONS_EXITING_TO_INSERT_MODE
from Vintageous.vi.constants import DIGRAPH_MOTION
from Vintageous.vi.constants import digraphs
from Vintageous.vi.constants import MODE_INSERT
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_NORMAL_INSERT
from Vintageous.vi.constants import MODE_REPLACE
from Vintageous.vi.constants import mode_to_str
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.contexts import KeyContext
from Vintageous.vi.registers import Registers
from Vintageous.vi.settings import SettingsManager
from Vintageous.vi.settings import SublimeSettings
from Vintageous.vi.settings import VintageSettings


def _init_vintageous(view):
    # Operate only on actual views.
    if (not getattr(view, 'settings') or
            view.settings().get('is_widget')):
        return

    state = VintageState(view)
    if state.mode in (MODE_VISUAL, MODE_VISUAL_LINE):
        view.run_command('enter_normal_mode')
    elif state.mode in (MODE_INSERT, MODE_REPLACE):
        view.run_command('vi_enter_normal_mode_from_insert_mode')
    elif state.mode == MODE_NORMAL_INSERT:
        view.run_command('vi_run_normal_insert_mode_actions')
    else:
        # XXX: When is this run? Only at startup?
        state.enter_normal_mode()

    state.reset()

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
    context = KeyContext()

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

        if self.view.overwrite_status():
            self.view.set_overwrite_status(False)

        self.view.run_command('glue_marked_undo_groups')

    def enter_visual_line_mode(self):
        self.mode = MODE_VISUAL_LINE

    def enter_insert_mode(self):
        self.settings.view['command_mode'] = False
        self.settings.view['inverse_caret_state'] = False
        self.mode = MODE_INSERT
        self.view.run_command('mark_undo_groups_for_gluing')

    def enter_visual_mode(self):
        self.mode = MODE_VISUAL

    def enter_normal_insert_mode(self):
        self.mode = MODE_NORMAL_INSERT
        self.settings.view['command_mode'] = False
        self.settings.view['inverse_caret_state'] = False

    def enter_replace_mode(self):
        self.mode = MODE_REPLACE
        self.settings.view['command_mode'] = False
        self.settings.view['inverse_caret_state'] = False
        self.view.set_overwrite_status(True)

    @property
    def mode(self):
        return self.settings.vi['mode']

    @mode.setter
    def mode(self, value):
        self.settings.vi['mode'] = value

    @property
    def cancel_action(self):
        # If we can't find a suitable action, we should cancel.
        return self.settings.vi['cancel_action']

    @cancel_action.setter
    def cancel_action(self, value):
        self.settings.vi['cancel_action'] = value

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
            # The chord is invalid, so notify that we need to cancel the command in .run().
            self.cancel_action = True
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
        """Computes and returns the final count, defaulting to 1 if the user
           didn't provide one.
        """
        motion_count = self.motion_digits and int(''.join(self.motion_digits)) or 1
        action_count = self.action_digits and int(''.join(self.action_digits)) or 1

        return (motion_count * action_count)

    @property
    def user_provided_count(self):
        """Returns the actual count provided by the user, which may be `None`.
        """
        if not (self.motion_digits or self.action_digits):
            return None

        return self.count

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
        vi_cmd_data = CmdData(self)

        # This should happen only at initialization.
        # XXX: This is effectively zeroing xpos. Shouldn't we move this into new_vi_cmd_data()?
        if vi_cmd_data['xpos'] is None:
            xpos = 0
            if self.view.sel():
                xpos = self.view.rowcol(self.view.sel()[0].b)
            self.xpos = xpos
            vi_cmd_data['xpos'] = xpos

        # Make sure we run NORMAL mode actions taking motions in _MODE_INTERNAL_NORMAL mode.
        #
        # Note that for NORMALMODE actions not taking any motion (like J) the mode isn't changed.
        # These are resposible for setting the mode to whichever they need.
        # XXX: Can we improve this and unify mode handling for all types of actions?
        if ((self.mode in (MODE_VISUAL, MODE_VISUAL_LINE)) or
            (self.motion and self.action) or
            (self.action and self.mode == MODE_NORMAL)):
                if self.mode not in (MODE_VISUAL, MODE_VISUAL_LINE):
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
            # XXX: This check is pretty useless, because we abort early in .run() anyway.
            # Logically, it makes sense, however.
            not vi_cmd_data['is_digraph_start']):
                vi_cmd_data['motion_required'] = False

        return vi_cmd_data

    def run(self):
        """Examines the current state and decides whether to actually run the action/motion.
        """

        if self.cancel_action:
            # TODO: add a .parse() method that includes boths steps?
            vi_cmd_data = self.parse_motion()
            vi_cmd_data = self.parse_action(vi_cmd_data)
            if vi_cmd_data['must_blink_on_error']:
                utils.blink()
            self.reset(next_mode=vi_cmd_data['_exit_mode'])
            return

        # Action + motion, like in "3dj".
        if self.action and self.motion:
            vi_cmd_data = self.parse_motion()
            vi_cmd_data = self.parse_action(vi_cmd_data)

            if not vi_cmd_data['is_digraph_start']:
                self.view.run_command('vi_run', vi_cmd_data)
            else:
                # If we have a digraph start, the global data is in an invalid state because we
                # are still missing the complete digraph. Abort and clean up.
                if vi_cmd_data['_exit_mode'] == MODE_INSERT:
                    # We've been requested to change to this mode. For example, we're looking at
                    # CTRL+r,j in INSERTMODE, which is an invalid sequence.
                    # !!! This could be simplified using parameters in .reset(), but then it
                    # wouldn't be obvious what was going on. Don't refactor. !!!
                    utils.blink()
                    self.reset()
                    self.enter_insert_mode()
                elif self.mode != MODE_NORMAL:
                    # Normally we'd go back to normal mode.
                    self.enter_normal_mode()
                    self.reset()

        # Motion only, like in "3j".
        elif self.motion:
            self.view.run_command('vi_run', self.parse_motion())

        # Action only, like in "d" or "esc". Some actions can be executed without a motion.
        elif self.action:
            vi_cmd_data = self.parse_motion()
            vi_cmd_data = self.parse_action(vi_cmd_data)

            if vi_cmd_data['is_digraph_start']:
                if vi_cmd_data['_change_mode_to']:
                    if vi_cmd_data['_change_mode_to'] == MODE_NORMAL:
                        self.enter_normal_mode()
                # We know we are not ready.
                return

            # In cases like gg, we might receive the motion here, so check for that.
            if self.motion and not self.action:
                self.view.run_command('vi_run', self.parse_motion())
                self.update_status()
                return

            if not vi_cmd_data['motion_required']:
                self.view.run_command('vi_run', vi_cmd_data)

        self.update_status()

    def reset(self, next_mode=None):
        self.motion = None
        self.action = None

        self.register = None
        self.user_input = None
        self.expecting_register = False
        self.expecting_user_input = False
        self.cancel_action = False

        # In MODE_NORMAL_INSERT, we temporarily exit NORMAL mode, but when we get back to
        # it, we need to know the repeat digits, so keep them. An example command for this case
        # would be 5ifoobar\n<esc> starting in NORMAL mode.
        if self.mode == MODE_NORMAL_INSERT:
            return

        self.motion_digits = []
        self.action_digits = []

        if next_mode == MODE_INSERT:
            self.enter_insert_mode()
        elif next_mode is not None:
            # XXX: We don't know yet of any case where a different mode is required.
            pass

    def update_status(self):
        mode_name = mode_to_str(self.mode) or ""
        mode_name = "-- %s --" % mode_name if mode_name else ""
        sublime.status_message(mode_name)


class VintageStateTracker(sublime_plugin.EventListener):
    def on_load(self, view):
        _init_vintageous(view)

    def on_post_save(self, view):
        # Make sure that the carets are within valid bounds. This is for example a concern when
        # `trim_trailing_white_space_on_save` is set to true.
        state = VintageState(view)
        view.run_command('_vi_adjust_carets', {'mode': state.mode})

    def on_query_context(self, view, key, operator, operand, match_all):
        vintage_state = VintageState(view)
        return vintage_state.context.check(key, operator, operand, match_all)


class ViFocusRestorerEvent(sublime_plugin.EventListener):
    def __init__(self):
        self.timer = None

    def action(self):
        self.timer = None

    def on_activated(self, view):
        if self.timer:
            # Switching to a different view; enter normal mode.
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
