import sublime
import sublime_plugin

import threading

from Vintageous.vi import actions
from Vintageous.vi import constants
from Vintageous.vi import inputs
from Vintageous.vi import motions
from Vintageous.vi import registers
from Vintageous.vi import utils
from Vintageous.vi.cmd_data import CmdData
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import ACTION_OR_MOTION
from Vintageous.vi.constants import ACTIONS_EXITING_TO_INSERT_MODE
from Vintageous.vi.constants import DIGRAPH_MOTION
from Vintageous.vi.constants import digraphs
from Vintageous.vi.constants import INCOMPLETE_ACTIONS
from Vintageous.vi.constants import INPUT_AFTER_MOTION
from Vintageous.vi.constants import INPUT_FOR_ACTIONS
from Vintageous.vi.constants import INPUT_FOR_MOTIONS
from Vintageous.vi.constants import INPUT_IMMEDIATE
from Vintageous.vi.constants import MODE_INSERT
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_NORMAL_INSERT
from Vintageous.vi.constants import MODE_REPLACE
from Vintageous.vi.constants import MODE_SELECT
from Vintageous.vi.constants import mode_to_str
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.constants import MODE_VISUAL_BLOCK
from Vintageous.vi.constants import MOTION_TRANSLATION_TABLE
from Vintageous.vi.constants import STASH
from Vintageous.vi.contexts import KeyContext
from Vintageous.vi.extend import PluginManager
from Vintageous.vi.marks import Marks
from Vintageous.vi.registers import Registers
from Vintageous.vi.settings import SettingsManager
from Vintageous.vi.settings import SublimeSettings
from Vintageous.vi.settings import VintageSettings


# Some commands gather user input through input panels. An input panel is just a view, so when it
# closes, the previous view gets activated and, consequently, Vintageous init code runs. However,
# if we're exiting from an input panel, we most likely want the global state to remain unchanged.
# This variable helps to signal this. For example, see the 'ViBufferSearch' command.
#
# XXX: Make this a class-level attribute of VintageState (had some trouble with it last time I tried).
# XXX Is there anything weird with ST and using class-level attributes from different modules?
_dont_reset_during_init = False


def _init_vintageous(view):
    """Initialize global data. Runs at startup and every time a view gets activated.
    """
    global _dont_reset_during_init

    # Abort if we didn't get a real view.
    if (not getattr(view, 'settings', None) or
        view.settings().get('is_widget')):
            return

    if _dont_reset_during_init:
        # We are probably coming from an input panel, like when using '/'. We don't want to reset
        # the global state, as it main contain data needed to complete the command that's being
        # built.
        _dont_reset_during_init = False
        return

    state = VintageState(view)

    # Non-standard user setting.
    reset = state.settings.view['vintageous_reset_mode_when_switching_tabs']
    # XXX: If the view was already in normal mode, we still need to run the init code. I believe
    # this is due to Sublime Text (intentionally) not serializing the inverted caret state and
    # the command_mode setting when first loading a file.
    if not reset and state.mode and (state.mode != MODE_NORMAL):
        return

    # TODO: make this a table in constants.py?
    if state.mode in (MODE_VISUAL, MODE_VISUAL_LINE):
        view.run_command('enter_normal_mode')
    elif state.mode in (MODE_INSERT, MODE_REPLACE):
        view.run_command('vi_enter_normal_mode_from_insert_mode')
    elif state.mode == MODE_NORMAL_INSERT:
        view.run_command('vi_run_normal_insert_mode_actions')
    else:
        # This may be run when we're coming from cmdline mode.
        state.enter_normal_mode()

    state.reset()


plugin_manager = None

# TODO: Test me.
def plugin_loaded():
    global plugin_manager
    plugin_manager = PluginManager()
    view = sublime.active_window().active_view()
    _init_vintageous(view)


# TODO: Test me.
def unload_handler():
    for w in sublime.windows():
        for v in w.views():
            v.settings().set('command_mode', False)
            v.settings().set('inverse_caret_state', False)
            v.settings().set('vintage', {})


class VintageState(object):
    """ Stores per-view state using View.Settings() for storage.
    """

    registers = Registers()
    context = KeyContext()
    marks = Marks()
    macros = {}
    # We maintain a stack of parsers for user input.
    user_input_parsers = []

    # Let's imitate Sublime Text's .command_history() 'null' value.
    _latest_repeat_command = ('', None, 0)

    # Stores the latest register name used for macro recording. It's a volatile value that never
    # gets reset during command execution.
    _latest_macro_name = None
    _is_recording = False
    _cancel_macro = False

    def __init__(self, view):
        self.view = view
        # We have two types of settings: vi-specific (settings.vi) and regular ST view settings
        # (settings.view).
        self.settings = SettingsManager(self.view)

    def enter_normal_mode(self):
        self.settings.view['command_mode'] = True
        self.settings.view['inverse_caret_state'] = True
        # Xpos must be updated every time we return to normal mode, because it doesn't get
        # updated while in insert mode.
        self.xpos = None if not self.view.sel() else self.view.rowcol(self.view.sel()[0].b)[1]

        if self.view.overwrite_status():
            self.view.set_overwrite_status(False)

        # Clear regions outlined by buffer search commands.
        self.view.erase_regions('vi_search')

        if not self.buffer_was_changed_in_visual_mode():
            # We've been in some visual mode, but we haven't modified the buffer at all.
            self.view.run_command('unmark_undo_groups_for_gluing')
        else:
            # Either we haven't been in any visual mode or we've modified the buffer while in
            # any visual mode.
            #
            # However, there might be cases where we have a clean buffer. For example, we might
            # have undone our changes, or saved via standard commands. Assume Sublime Text knows
            # better than us.
            #
            # NOTE: There's an issue in S3 where 'glue_marked_undo_groups' will mark the buffer as
            # dirty even if there are no intervening changes between the 'mark_groups_for_gluing'
            # and 'glue_marked_undo_groups' calls. That's why we need to explicitly unmark groups
            # here if the view reports back as clean.
            if not self.view.is_dirty():
                self.view.run_command('unmark_undo_groups_for_gluing')
            else:
                self.view.run_command('glue_marked_undo_groups')

        self.mode = MODE_NORMAL

    def enter_visual_line_mode(self):
        self.mode = MODE_VISUAL_LINE

    def enter_select_mode(self):
        self.mode = MODE_SELECT

    def enter_insert_mode(self):
        self.settings.view['command_mode'] = False
        self.settings.view['inverse_caret_state'] = False
        self.mode = MODE_INSERT

    def enter_visual_mode(self):
        self.mode = MODE_VISUAL

    def enter_visual_block_mode(self):
        self.mode = MODE_VISUAL_BLOCK

    def enter_normal_insert_mode(self):
        # This is the mode we enter when we give i a count, as in 5ifoobar<CR><ESC>.
        self.mode = MODE_NORMAL_INSERT
        self.settings.view['command_mode'] = False
        self.settings.view['inverse_caret_state'] = False

    def enter_replace_mode(self):
        self.mode = MODE_REPLACE
        self.settings.view['command_mode'] = False
        self.settings.view['inverse_caret_state'] = False
        self.view.set_overwrite_status(True)

    def store_visual_selections(self):
        self.view.add_regions('vi_visual_selections', list(self.view.sel()))

    def buffer_was_changed_in_visual_mode(self):
        """Returns `True` if we've changed the buffer while in visual mode.
        """
        # XXX: What if we used view.is_dirty() instead? That should be simpler?
        # XXX: If we can be sure that every modifying command will leave the buffer in a dirty
        # state, we could go for this solution.

        # 'maybe_mark_undo_groups_for_gluing' and 'glue_marked_undo_groups' seem to add an entry
        # to the undo stack regardless of whether intervening modifying-commands have been
        # issued.
        #
        # Example:
        #   1) We enter visual mode by pressing 'v'.
        #   2) We exit visual mode by pressing 'v' again.
        #
        # Since before the first 'v' and after the second we've called the aforementioned commands,
        # respectively, we'd now have a new (useless) entry in the undo stack, and the redo stack
        # would be empty. This would be undesirable, so we need to find out whether marked groups
        # in visual mode actually need to be glued or not and act based on that information.

        # FIXME: Design issue. This method won't work always. We have actions like yy that
        # will make this method return true, while it should return False (since yy isn't a
        # modifying command). However, yy signals in its own way that it's a non-modifying command.
        # I don't think this redundancy will cause any bug, but we need to unify nevetheless.

        if self.mode == MODE_VISUAL:
            visual_cmd = 'vi_enter_visual_mode'
        elif self.mode == MODE_VISUAL_LINE:
            visual_cmd = 'vi_enter_visual_line_mode'
        else:
            return True

        cmds = []
        # Set an upper limit to look-ups in the undo stack.
        for i in range(0, -249, -1):
            cmd_name, args, _ = self.view.command_history(i)
            if (cmd_name == 'vi_run' and args['action'] and
                args['action']['command'] == visual_cmd):
                    break

            # Sublime Text returns ('', None, 0) when we hit the undo stack's bottom.
            if not cmd_name:
                break

            cmds.append((cmd_name, args))

        # If we have an action between v..v calls (or visual line), we have modified the buffer
        # (most of the time, anyway, there are exceptions that we're not covering here).
        # TODO: Cover exceptions too, like yy (non-modifying command, though has the shape of a
        # modifying command).
        was_modifed = [name for (name, data) in cmds
                                        if data and data.get('action')]

        return bool(was_modifed)

    @property
    def mode(self):
        """The current mode.
        """
        return self.settings.vi['mode']

    @mode.setter
    def mode(self, value):
        self.settings.vi['mode'] = value

    @property
    def cancel_macro(self):
        """Signals whether a running macro should be cancel if, for instance, a motion failed.
        """
        return VintageState._cancel_macro

    # Should only be called from _vi_run_macro.
    @cancel_macro.setter
    def cancel_macro(self, value):
        VintageState._cancel_macro = value

    @property
    def cancel_action(self):
        """Returns `True` if the current action must be cancelled.
        """
        # If we can't find a suitable action, we should cancel.
        return self.settings.vi['cancel_action']

    @cancel_action.setter
    def cancel_action(self, value):
        self.settings.vi['cancel_action'] = value

    # TODO: Test me.
    @property
    def stashed_action(self):
        return self.settings.vi['stashed_action']

    # TODO: Test me.
    @stashed_action.setter
    def stashed_action(self, name):
        self.settings.vi['stashed_action'] = name

    @property
    def action(self):
        """Command's action; must be the name of a function in the `actions` module.
        """
        return self.settings.vi['action']

    # TODO: Test me.
    @action.setter
    def action(self, action):
        stored_action = self.settings.vi['action']
        target = 'action'

        # Sometimes we'll receive an incomplete command that may be an action or a motion, like g
        # or dg, both leading up to gg and dgg, respectively. When there's already a complete
        # action, though, we already know it must be a motion (as in dg and dgg).
        # Similarly, if there is an action and a motion, the motion must handle the new name just
        # received. This would be the case when we have dg and we receive another 'g' (or
        # anything else, for that matter).
        if (self.action and INCOMPLETE_ACTIONS.get(action) == ACTION_OR_MOTION or
            self.motion):
            # The .motion should handle this.
            self.motion = action
            return

        # Check for digraphs like cc, dd, yy.
        final_action = action
        if stored_action and action:
            final_action, type_ = digraphs.get((stored_action, action), ('', None))
            # We didn't find a built-in action; let's try with the plugins.
            if final_action == '':
                final_action, type_ = plugin_manager.composite_commands.get((stored_action, action), ('', None))

            # Check for multigraphs like g~g~, g~~.
            # This sequence would get us here:
            #   * vi_g_action
            #   * vi_tilde
            #   * vi_g_action => vi_g_tilde, STASH
            #   * vi_tilde => vi_g_tilde_vi_g_tilde, DIGRAPH_ACTION
            if self.stashed_action:
                final_action, type_ = digraphs.get((self.stashed_action, final_action),
                                                 ('', None))

            # Some motion digraphs are captured as actions, but need to be stored as motions
            # instead so that the vi command is evaluated correctly.
            # Ex: gg (vi_g_action, vi_gg)
            if type_ == DIGRAPH_MOTION:
                target = 'motion'

                # TODO: Encapsulate this in a method.
                input_type, input_parser = INPUT_FOR_MOTIONS.get(final_action, (None, None))
                if input_parser:
                    self.user_input_parsers.append(input_parser)
                if input_type == INPUT_IMMEDIATE:
                    self.expecting_user_input = True

                self.settings.vi['action'] = None
            # We are still in an intermediary step, so do some bookkeeping...
            elif type_ == STASH:
                # In this case we need to overwrite the current action differently.
                self.stashed_action = final_action
                self.settings.vi['action'] = action
                self.display_partial_command()
                return

        # Avoid recursion. The .reset() method will try to set this property to None, not ''.
        if final_action == '':
            # The chord is invalid, so notify that we need to cancel the command in .eval().
            self.cancel_action = True
            return

        if target == 'action':
            input_type, input_parser = INPUT_FOR_ACTIONS.get(final_action, (None, None))
            if input_parser:
                self.user_input_parsers.append(input_parser)
            if input_type == INPUT_IMMEDIATE:
                self.expecting_user_input = True

        self.settings.vi[target] = final_action
        self.display_partial_command()

    @property
    def motion(self):
        """Command's motion; must be the name of a function in the `motions` module.
        """
        return self.settings.vi['motion']

    # TODO: Test me.
    @motion.setter
    def motion(self, name):
        if self.action in INCOMPLETE_ACTIONS:
            # The .action should handle this.
            self.action = name
            return

        # HACK: Translate vi_enter to \n if we're expecting user input.
        # This enables r\n, for instance.
        # XXX: I don't understand why the enter key is captured as a motion in this case, though;
        # the catch-all key binding for user input should have intercepted it.
        if self.expecting_user_input and name == 'vi_enter':
            self.view.run_command('collect_user_input', {'character': '\n'})
            return

        # Check for digraphs like gg in dgg.
        stored_motion = self.motion
        if stored_motion and name:
            name, type_ = digraphs.get((stored_motion, name), (None, None))
            if type_ != DIGRAPH_MOTION:
                # We know there's an action because we only check for digraphs  when there is one.
                self.cancel_action = True
                return

        motion_name = MOTION_TRANSLATION_TABLE.get((self.action, name), name)

        input_type, input_parser = INPUT_FOR_MOTIONS.get(motion_name, (None, None))
        if input_type == INPUT_IMMEDIATE:
            self.expecting_user_input = True
            self.user_input_parsers.append(input_parser)

        if not input_type and self.user_input_parsers:
            self.expecting_user_input = True

        self.settings.vi['motion'] = motion_name
        self.display_partial_command()

    @property
    def motion_digits(self):
        """Count for the motion, like in 3k.
        """
        return self.settings.vi['motion_digits'] or []

    @motion_digits.setter
    def motion_digits(self, value):
        self.settings.vi['motion_digits'] = value
        self.display_partial_command()

    def push_motion_digit(self, value):
        digits = self.settings.vi['motion_digits']
        if not digits:
            self.settings.vi['motion_digits'] = [value]
            self.display_partial_command()
            return
        digits.append(value)
        self.settings.vi['motion_digits'] = digits
        self.display_partial_command()

    @property
    def action_digits(self):
        """Count for the action, as in 3dd.
        """
        return self.settings.vi['action_digits'] or []

    @action_digits.setter
    def action_digits(self, value):
        self.settings.vi['action_digits'] = value
        self.display_partial_command()

    def push_action_digit(self, value):
        digits = self.settings.vi['action_digits']
        if not digits:
            self.settings.vi['action_digits'] = [value]
            self.display_partial_command()
            return
        digits.append(value)
        self.settings.vi['action_digits'] = digits
        self.display_partial_command()

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
    def expecting_register(self):
        """Signals that we need more input from the user before evaluating the global data.
        """
        return self.settings.vi['expecting_register']

    @expecting_register.setter
    def expecting_register(self, value):
        self.settings.vi['expecting_register'] = value

    @property
    def register(self):
        """Name of the register provided by the user, as in "ayy.
        """
        return self.settings.vi['register'] or None

    @register.setter
    def register(self, name):
        # TODO: Check for valid register name.
        self.settings.vi['register'] = name
        self.expecting_register = False

    @property
    def expecting_user_input(self):
        """Signals that we need more input from the user before evaluating the global data.
        """
        return self.settings.vi['expecting_user_input']

    @expecting_user_input.setter
    def expecting_user_input(self, value):
        self.settings.vi['expecting_user_input'] = value

    @property
    def user_input(self):
        """Additional data provided by the user, as 'a' in @a.
        """
        return self.settings.vi['user_input'] or ''

    @user_input.setter
    def user_input(self, value):
        self.settings.vi['user_input'] = value
        # FIXME: Sometimes we set the following property in other places too.
        self.validate_user_input()
        # self.expecting_user_input = False
        self.display_partial_command()

    def validate_user_input(self):
        name = ''
        if len(self.user_input_parsers) == 2:
            # We have two parsers: one for the motion, one for the action.
            # Evaluate first the motion's.
            name = self.motion
            validator = self.user_input_parsers[-1]
        elif self.motion and INPUT_FOR_ACTIONS.get(self.action, (None, None))[0] == INPUT_AFTER_MOTION:
            assert len(self.user_input_parsers) == 1
            name = self.action
            validator = self.user_input_parsers[-1]
        elif self.motion and self.action:
            name = self.motion
            validator = self.user_input_parsers[-1]
        elif self.action:
            name = self.action
            validator = self.user_input_parsers[-1]
        elif self.motion:
            name = self.motion
            validator = self.user_input_parsers[-1]

        assert validator, "Validator must exist if expecting user input."
        if validator(self.user_input):
            if name == self.motion:
                self.settings.vi['user_motion_input'] = self.user_input
                self.settings.vi['user_input'] = None
            elif name == self.action:
                self.settings.vi['user_action_input'] = self.user_input
                self.settings.vi['user_input'] = None

            self.user_input_parsers.pop()
            if len(self.user_input_parsers) == 0:
                self.expecting_user_input = False

    def clear_user_input_buffers(self):
        self.settings.vi['user_action_input'] = None
        self.settings.vi['user_motion_input'] = None
        self.settings.vi['user_input'] = None

    @property
    def last_buffer_search(self):
        """Returns the latest buffer search string or `None`. Used by the n and N commands.
        """
        return self.settings.vi['last_buffer_search'] or None

    @last_buffer_search.setter
    def last_buffer_search(self, value):
        self.settings.vi['last_buffer_search'] = value

    @property
    def last_character_search(self):
        """Returns the latest character search or `None`. Used by the , and ; commands.
        """
        return self.settings.vi['last_character_search'] or None

    @property
    def last_character_search_forward(self):
        """Returns True, False or `None`. Used by the , and ; commands.
        """
        return self.settings.vi['last_character_search_forward'] or None

    @last_character_search_forward.setter
    def last_character_search_forward(self, value):
        # TODO: Should this piece of data be global instead of local to each buffer?
        self.settings.vi['last_character_search_forward'] = value

    @last_character_search.setter
    def last_character_search(self, value):
        # TODO: Should this piece of data be global instead of local to each buffer?
        self.settings.vi['last_character_search'] = value

    @property
    def xpos(self):
        """Maintains the current column for the caret in normal and visual mode.
        """
        xpos = self.settings.vi['xpos']
        return xpos if isinstance(xpos, int) else None

    @xpos.setter
    def xpos(self, value):
        self.settings.vi['xpos'] = value

    @property
    def next_mode(self):
        """Mode to transition to after the command has been run. For example, ce needs to change
           to insert mode after it's run.
        """
        next_mode = self.settings.vi['next_mode'] or MODE_NORMAL
        return next_mode

    @next_mode.setter
    def next_mode(self, value):
        self.settings.vi['next_mode'] = value

    @property
    def next_mode_command(self):
        """Command to make the transitioning to the next mode.
        """
        next_mode_command = self.settings.vi['next_mode_command']
        return next_mode_command

    @next_mode_command.setter
    def next_mode_command(self, value):
        self.settings.vi['next_mode_command'] = value

    @property
    def repeat_command(self):
        """Latest modifying command performed. Accessed via '.'.
        """
        # This property is volatile. It won't be persisted between sessions.
        return VintageState._latest_repeat_command

    @repeat_command.setter
    def repeat_command(self, value):
        VintageState._latest_repeat_command = value

    @property
    def is_recording(self):
        """Signals that we're recording a macro.
        """
        return VintageState._is_recording

    @is_recording.setter
    def is_recording(self, value):
        VintageState._is_recording = value

    @property
    def latest_macro_name(self):
        """Latest macro recorded. Accessed via @@.
        """
        return VintageState._latest_macro_name

    @latest_macro_name.setter
    def latest_macro_name(self, value):
        VintageState._latest_macro_name = value


    def parse_motion(self):
        """Returns a CmdData instance with parsed motion data.
        """
        vi_cmd_data = CmdData(self)

        # This should happen only at initialization.
        # XXX: This is effectively zeroing xpos. Shouldn't we move this into new_vi_cmd_data()?
        # XXX: REFACTOR
        if vi_cmd_data['xpos'] is None:
            xpos = 0
            if self.view.sel():
                xpos = self.view.rowcol(self.view.sel()[0].b)
            self.xpos = xpos
            vi_cmd_data['xpos'] = xpos

        # Actions originating in normal mode are run in a pseudomode that helps to distiguish
        # between visual mode and this case (both use selections, either implicitly or
        # explicitly).
        if self.action and (self.mode == MODE_NORMAL):
            vi_cmd_data['mode'] = _MODE_INTERNAL_NORMAL

        motion = self.motion
        motion_func = None
        if motion:
            try:
                motion_func = getattr(motions, self.motion)
            except AttributeError:
                raise AttributeError("Vintageous: Unknown motion: '{0}'".format(self.motion))

        if motion_func:
            vi_cmd_data = motion_func(vi_cmd_data)

        return vi_cmd_data

    def parse_action(self, vi_cmd_data):
        """Updates and returns the passed-in CmdData instance using parsed data about the action.
        """
        try:
            action_func = getattr(actions, self.action)
        except AttributeError:
            try:
                # We didn't find the built-in function; let's try our luck with plugins.
                action_func = plugin_manager.actions[self.action]
            except KeyError:
                raise AttributeError("Vintageous: Unknown action: '{0}'".format(self.action))
        except TypeError:
            raise TypeError("Vintageous: parse_action requires an action be specified.")

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

    def eval_cancel_action(self):
        """Cancels the whole run of the command.
        """
        # TODO: add a .parse() method that includes boths steps?
        vi_cmd_data = self.parse_motion()
        vi_cmd_data = self.parse_action(vi_cmd_data)
        if vi_cmd_data['must_blink_on_error']:
            utils.blink()
        # Modify the data that determines the mode we'll end up in when the command finishes.
        self.next_mode = vi_cmd_data['_exit_mode']
        # Since we are exiting early, ensure we leave the selections as the commands wants them.
        if vi_cmd_data['_exit_mode_command']:
            self.view.run_command(vi_cmd_data['_exit_mode_command'])

    def eval_full_command(self):
        """Evaluates a command like 3dj, where there is an action as well as a motion.
        """
        vi_cmd_data = self.parse_motion()

        # Sometimes we'll have an incomplete motion, like in dg leading up to dgg. In this case,
        # we don't want the vi command evaluated just yet.
        if vi_cmd_data['is_digraph_start']:
            return

        vi_cmd_data = self.parse_action(vi_cmd_data)

        if not vi_cmd_data['is_digraph_start']:
            # We are about to run an action, so let Sublime Text know we want all editing
            # steps folded into a single sequence. "All editing steps" means slightly different
            # things depending on the mode we are in.
            if vi_cmd_data['_mark_groups_for_gluing']:
                self.view.run_command('maybe_mark_undo_groups_for_gluing')
            self.view.run_command('vi_run', vi_cmd_data)
            self.reset()
        else:
            # If we have a digraph start, the global data is in an invalid state because we
            # are still missing the complete digraph. Abort and clean up.
            if vi_cmd_data['_exit_mode'] == MODE_INSERT:
                # We've been requested to change to this mode. For example, we're looking at
                # CTRL+r,j in INSERTMODE, which is an invalid sequence.
                utils.blink()
                self.reset()
                self.enter_insert_mode()
            # We have an invalid command which consists in an action and a motion, like gl. Abort.
            elif (self.mode == MODE_NORMAL) and self.motion:
                utils.blink()
                self.reset()
            elif self.mode != MODE_NORMAL:
                # Normally we'd go back to normal mode.
                self.enter_normal_mode()
                self.reset()

    def eval_lone_action(self):
        """Evaluate lone action like in 'd' or 'esc'. Some actions can be run without a motion.
        """
        vi_cmd_data = self.parse_motion()
        vi_cmd_data = self.parse_action(vi_cmd_data)

        if vi_cmd_data['is_digraph_start']:
            # XXX: When does this happen? Why are we only interested in MODE_NORMAL?
            # XXX In response to the above, this must be due to Ctrl+r.
            if vi_cmd_data['_change_mode_to'] == MODE_NORMAL:
                self.enter_normal_mode()
            # We know we are not ready.
            return

        if not vi_cmd_data['motion_required']:
            # We are about to run an action, so let Sublime Text know we want all editing
            # steps folded into a single sequence. "All editing steps" means slightly different
            # things depending on the mode we are in.
            if vi_cmd_data['_mark_groups_for_gluing']:
                self.view.run_command('maybe_mark_undo_groups_for_gluing')
            self.view.run_command('vi_run', vi_cmd_data)
            self.reset()


    # TODO: Test me.
    def eval(self):
        """Examines the current state and decides whether to actually run the action/motion.
        """

        if self.cancel_action:
            self.eval_cancel_action()
            self.reset()
            utils.blink()

        elif self.expecting_user_input:
            return

        # Action + motion, like in '3dj'.
        elif self.action and self.motion:
            self.eval_full_command()

        # Motion only, like in '3j'.
        elif self.motion:
            vi_cmd_data = self.parse_motion()
            self.view.run_command('vi_run', vi_cmd_data)
            self.reset()

        # Action only, like in 'd' or 'esc'. Some actions can be executed without a motion.
        elif self.action:
            self.eval_lone_action()

    def reset(self):
        """Reset global state.
        """
        had_action = self.action

        self.motion = None
        self.action = None
        self.stashed_action = None

        self.register = None
        self.clear_user_input_buffers()
        self.user_input_parsers.clear()
        self.expecting_register = False
        self.expecting_user_input = False
        self.cancel_action = False

        sublime.set_timeout(lambda: self.view.erase_regions('vi_training_wheels'), 300)

        # In MODE_NORMAL_INSERT, we temporarily exit NORMAL mode, but when we get back to
        # it, we need to know the repeat digits, so keep them. An example command for this case
        # would be 5ifoobar\n<esc> starting in NORMAL mode.
        if self.mode == MODE_NORMAL_INSERT:
            return

        self.motion_digits = []
        self.action_digits = []

        if self.next_mode in (MODE_NORMAL, MODE_INSERT):
            if self.next_mode_command:
                self.view.run_command(self.next_mode_command)

        # Sometimes we'll reach this point after performing motions. If we have a stored repeat
        # command in view A, we switch to view B and do a motion, we don't want .update_repeat_command()
        # to inspect view B's undo stack and grab its latest modifying command; we want to keep
        # view A's instead, which is what's stored in _latest_repeat_command. We only want to
        # update this when there is a new action.
        # FIXME: Even that will fail when we perform an action that does not modify the buffer,
        # like splitting the window. The current view's latest modifying command will overwrite
        # the genuine _latest_repeat_command. The correct solution seems to be to tag every single
        # modifying command with a 'must_update_repeat_command' attribute.
        if had_action:
            self.update_repeat_command()

        self.next_mode = MODE_NORMAL
        self.next_mode_command = None

    def update_repeat_command(self):
        """Vintageous manages the repeat command on its own. Vim stores away the latest modifying
           command as the repeat command, and does not wipe it when undoing. On the contrary,
           Sublime Text will update the repeat command as soon as you undo past the current one.
           The then previous latest modifying command becomes the new repeat command, and so on.
        """
        cmd, args, times = self.view.command_history(0, True)

        if not cmd:
            return
        elif cmd == 'vi_run' and args.get('action'):
            self.repeat_command = cmd, args, times
        elif cmd == 'sequence':
            # XXX: We are assuming every 'sequence' command is a modifying command, which seems
            # to be reasonable, but I dunno.
            self.repeat_command = cmd, args, times
        elif cmd != 'vi_run':
            # XXX: We are assuming every 'native' command is a modifying commmand, but it doesn't
            # feel right...
            self.repeat_command = cmd, args, times

    def update_xpos(self):
        xpos = 0

        try:
            first_sel = self.view.sel()[0]
        except IndexError:
            # XXX: Perhaps it's better to leave the xpos untouched?
            self.xpos = xpos
            return

        if self.mode == MODE_VISUAL:
            if first_sel.a < first_sel.b:
                xpos = self.view.rowcol(first_sel.b - 1)[1]
            elif first_sel.a > first_sel.b:
                xpos = self.view.rowcol(first_sel.b)[1]

        elif self.mode == MODE_NORMAL:
            xpos = self.view.rowcol(first_sel.b)[1]

        self.xpos = xpos

    def display_partial_command(self):
        mode_name = mode_to_str(self.mode) or ""
        mode_name = "-- %s --" % mode_name if mode_name else ""
        msg = "{0} {1} {2} {3} {4} {5}"
        action_count = ''.join(self.action_digits) or ''
        action = self.stashed_action or self.action or ''
        motion_count = ''.join(self.motion_digits) or ''
        motion = self.motion or ''
        motion_input = self.settings.vi['user_motion_input'] or ''
        action_input = self.user_input or ''
        if (action and motion) or motion:
            msg = msg.format(action_count, action, motion_count, motion, motion_input, action_input)
        elif action:
            msg = msg.format(motion_count, action, action_count, motion, motion_input, action_input)
        else:
            msg = msg.format(action_count, action, motion_count, motion, motion_input, action_input)
        sublime.status_message(mode_name + ' ' + msg)


# TODO: Test me.
class VintageStateTracker(sublime_plugin.EventListener):
    def on_load(self, view):
        _init_vintageous(view)

    def on_post_save(self, view):
        # Ensure the carets are within valid bounds. For instance, this is a concern when
        # `trim_trailing_white_space_on_save` is set to true.
        state = VintageState(view)
        view.run_command('_vi_adjust_carets', {'mode': state.mode})

    def on_query_context(self, view, key, operator, operand, match_all):
        vintage_state = VintageState(view)
        return vintage_state.context.check(key, operator, operand, match_all)


# TODO: Test me.
class ViFocusRestorerEvent(sublime_plugin.EventListener):
    def __init__(self):
        self.timer = None

    def action(self):
        self.timer = None

    def on_activated(self, view):
        if self.timer:
            self.timer.cancel()
            # Switching to a different view; enter normal mode.
            _init_vintageous(view)
        else:
            # Switching back from another application. Ignore.
            pass

    def on_new(self, view):
        # Without this, on OS X Vintageous might not initialize correctly if the user leaves
        # the application in a windowless state and then creates a new buffer.
        if sublime.platform() == 'osx':
            _init_vintageous(view)

    def on_load(self, view):
        # Without this, on OS X Vintageous might not initialize correctly if the user leaves
        # the application in a windowless state and then creates a new buffer.
        if sublime.platform() == 'osx':
            _init_vintageous(view)

    def on_deactivated(self, view):
        self.timer = threading.Timer(0.25, self.action)
        self.timer.start()


# TODO: Test me.
class IrreversibleTextCommand(sublime_plugin.TextCommand):
    """ Base class.

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
