from collections import Counter

import sublime

from Vintageous import PluginLogger
from Vintageous import NullPluginLogger
from Vintageous.vi import cmd_base
from Vintageous.vi import cmd_defs
from Vintageous.vi import settings
from Vintageous.vi import utils
from Vintageous.vi.contexts import KeyContext
from Vintageous.vi.dot_file import DotFile
from Vintageous.vi.macros import MacroRegisters
from Vintageous.vi.marks import Marks
from Vintageous.vi.registers import Registers
from Vintageous.vi.settings import SettingsManager
from Vintageous.vi.utils import directions
from Vintageous.vi.utils import first_sel
from Vintageous.vi.utils import input_types
from Vintageous.vi.utils import is_ignored
from Vintageous.vi.utils import is_ignored_but_command_mode
from Vintageous.vi.utils import is_view
from Vintageous.vi.utils import modes
from Vintageous.vi.variables import Variables

# !! Avoid error due to sublime_plugin.py:45 expectations.
from Vintageous.plugins import plugins as user_plugins


_logger = PluginLogger(__name__)


def _init_vintageous(view, new_session=False):
    """
    Initializes global data. Runs at startup and every time a view gets
    activated, loaded, etc.

    @new_session
      Whether we're starting up Sublime Text. If so, volatile data must be
      wiped.
    """

    _logger.debug("running init for view %d", view.id())

    if not is_view(view):
        # Abort if we got a widget, panel...
        _logger.info(
            '[_init_vintageous] ignoring view: {0}'.format(
                view.name() or view.file_name() or '<???>'))
        try:
            # XXX: All this seems to be necessary here.
            if not is_ignored_but_command_mode(view):
                view.settings().set('command_mode', False)
                view.settings().set('inverse_caret_state', False)
            view.settings().erase('vintage')
            if is_ignored(view):
                # Someone has intentionally disabled Vintageous, so let the user know.
                sublime.status_message(
                    'Vintageous: Vim emulation disabled for the current view')
        except AttributeError:
            _logger.info(
                '[_init_vintageous] probably received the console view')
        except Exception:
            _logger.error('[_init_vintageous] error initializing view')
        finally:
            return

    state = State(view)

    if not state.reset_during_init:
        # Probably exiting from an input panel, like when using '/'. Don't
        # reset the global state, as it may contain data needed to complete
        # the command that's being built.
        state.reset_during_init = True
        return

    # Non-standard user setting.
    reset = state.settings.view['vintageous_reset_mode_when_switching_tabs']
    # XXX: If the view was already in normal mode, we still need to run the
    # init code. I believe this is due to Sublime Text (intentionally) not
    # serializing the inverted caret state and the command_mode setting when
    # first loading a file.
    # If the mode is unknown, it might be a new file. Let normal mode setup
    # continue.
    if not reset and (state.mode not in (modes.NORMAL, modes.UNKNOWN)):
        return

    # If we have no selections, add one.
    if len(state.view.sel()) == 0:
        state.view.sel().add(sublime.Region(0))

    state.logger.info('[_init_vintageous] running init')

    if state.mode in (modes.VISUAL, modes.VISUAL_LINE):
        # TODO: Don't we need to pass a mode here?
        view.window().run_command('_enter_normal_mode', {'from_init': True})

    elif state.mode in (modes.INSERT, modes.REPLACE):
        # TODO: Don't we need to pass a mode here?
        view.window().run_command('_enter_normal_mode', {'from_init': True})

    elif (view.has_non_empty_selection_region() and
          state.mode != modes.VISUAL):
            # Runs, for example, when we've performed a search via ST3 search
            # panel and we've pressed 'Find All'. In this case, we want to
            # ensure a consistent state for multiple selections.
            # TODO: We could end up with multiple selections in other ways
            #       that bypass _init_vintageous.
            state.mode = modes.VISUAL

    else:
        # This may be run when we're coming from cmdline mode.
        pseudo_visual = view.has_non_empty_selection_region()
        mode = modes.VISUAL if pseudo_visual else state.mode
        # TODO: Maybe the above should be handled by State?
        state.enter_normal_mode()
        view.window().run_command('_enter_normal_mode', {'mode': mode,
                                                         'from_init': True})

    state.reset_command_data()
    if new_session:
        state.reset_volatile_data()

        # Load settings.
        DotFile.from_user().run()


# TODO: Implement this
plugin_manager = None


# TODO: Test me.
def plugin_loaded():
    view = sublime.active_window().active_view()
    _init_vintageous(view, new_session=True)


# TODO: Test me.
def plugin_unloaded():
    view = sublime.active_window().active_view()
    try:
        view.settings().set('command_mode', False)
        view.settings().set('inverse_caret_state', False)
    except AttributeError:
        _logger.warn(
            'could not access sublime.active_window().active_view().settings '
            ' while unloading')


class State(object):
    """
    Manages global Vim state. Accumulates command data, etc.

    Usage:
      Always instantiate passing it the view that commands are going to
      target.

      Example:

          state = State(view)

    Notes:
      `State` internally uses view.settings() and window.settings()
      to persist data.
    """

    registers = Registers()
    macro_registers = MacroRegisters()
    marks = Marks()
    context = KeyContext()
    variables = Variables()
    macro_steps = []

    def __init__(self, view):
        self.view = view
        # We use several types of settings:
        #   - vi-specific (settings.vi),
        #   - regular ST view settings (settings.view) and
        #   - window settings (settings.window).
        self.settings = SettingsManager(self.view)

        _logger.debug(
            '[State] Is .view an ST/Vintageous widget? {0}/{1}'.format(
                bool(self.settings.view['is_widget']),
                bool(self.settings.view['is_vintageous_widget']))
            )

    @property
    def glue_until_normal_mode(self):
        """
        Indicates that editing commands should be grouped together in a single
        undo step after the user requested `_enter_normal_mode` next.

        This property is *VOLATILE*; it shouldn't be persisted between
        sessions.
        """
        return self.settings.vi['_vintageous_glue_until_normal_mode'] or False

    @glue_until_normal_mode.setter
    def glue_until_normal_mode(self, value):
        self.settings.vi['_vintageous_glue_until_normal_mode'] = value

    @property
    def processing_notation(self):
        """
        Indicates whether `ProcessNotation` is running a command and is
        grouping all edits in one single undo step. That is, we are running
        a non-interactive sequence of commands.

        This property is *VOLATILE*; it shouldn't be persisted between
        sessions.
        """
        # TODO(guillermooo): Rename self.settings.vi to self.settings.local
        return self.settings.vi['_vintageous_processing_notation'] or False

    @processing_notation.setter
    def processing_notation(self, value):
        self.settings.vi['_vintageous_processing_notation'] = value

    # FIXME: This property seems to do the same as processing_notation.
    @property
    def non_interactive(self):
        """
        Indicates whether `ProcessNotation` is running a command and no
        interactive prompts should be used (for example, by the '/' motion.)

        This property is *VOLATILE*; it shouldn't be persisted between
        sessions.
        """
        return self.settings.vi['_vintageous_non_interactive'] or False

    @non_interactive.setter
    def non_interactive(self, value):
        assert isinstance(value, bool), 'bool expected'
        self.settings.vi['_vintageous_non_interactive'] = value

    @property
    def last_character_search(self):
        """
        Last character used as input for 'f' or 't'.
        """
        return self.settings.window['_vintageous_last_character_search'] or ''

    @last_character_search.setter
    def last_character_search(self, value):
        assert isinstance(value, str), 'bad call'
        assert len(value) == 1, 'bad call'
        self.settings.window['_vintageous_last_character_search'] = value

    @property
    def last_char_search_command(self):
        """
        ',' and ';' change directions depending on which of 'f' or 't' was the
        previous command.

        Returns the name of the last character search command, namely:
        'vi_f', 'vi_t', 'vi_big_f' or 'vi_big_t'.
        """
        name = self.settings.window['_vintageous_last_char_search_command']
        return name or 'vi_f'

    @last_char_search_command.setter
    def last_char_search_command(self, value):
        self.settings.window['_vintageous_last_char_search_command'] = value

    @property
    def last_buffer_search_command(self):
        """
        'n' and 'N' change directions depending on which of '/' or '?' was the
        previous command.

        Returns the name of the last character search command, namely:
        'vi_slash', 'vi_question_mark', 'vi_star', 'vi_octothorp'
        """
        name = self.settings.window['_vintageous_last_buffer_search_command']
        return name or 'vi_slash'

    @last_buffer_search_command.setter
    def last_buffer_search_command(self, value):
        self.settings.window['_vintageous_last_buffer_search_command'] = value

    @property
    def must_capture_register_name(self):
        """
        Returns `True` if `State` is expecting a register name next.
        """
        return self.settings.vi['must_capture_register_name'] or False

    @must_capture_register_name.setter
    def must_capture_register_name(self, value):
        self.settings.vi['must_capture_register_name'] = value

    @property
    def last_buffer_search(self):
        """
        Returns the last string used by buffer search commands '/' or '?'.
        """
        return self.settings.window['_vintageous_last_buffer_search'] or ''

    @last_buffer_search.setter
    def last_buffer_search(self, value):
        self.settings.window['_vintageous_last_buffer_search'] = value

    @property
    def reset_during_init(self):
        # Some commands gather user input through input panels. An input panel
        # is just a view, so when it's closed, the previous view gets
        # activated and Vintageous init code runs. In this case, however, we
        # most likely want the global state to remain unchanged. This variable
        # helps to signal this.
        #
        # For an example, see the '_vi_slash' command.
        value = self.settings.window['_vintageous_reset_during_init']
        if not isinstance(value, bool):
            return True
        return value

    @reset_during_init.setter
    def reset_during_init(self, value):
        assert isinstance(value, bool), 'expected a bool'
        self.settings.window['_vintageous_reset_during_init'] = value

    # This property isn't reset automatically. _enter_normal_mode mode must
    # take care of that so it can repeat the commands issued while in
    # insert mode.
    @property
    def normal_insert_count(self):
        """
        Count issued to 'i' or 'a', etc. These commands enter insert mode.
        If passed a count, they must repeat the commands run while in insert
        mode.
        """
        return self.settings.vi['normal_insert_count'] or '1'

    @normal_insert_count.setter
    def normal_insert_count(self, value):
        self.settings.vi['normal_insert_count'] = value

    @property
    def sequence(self):
        """
        Sequence of keys provided by the user.
        """
        return self.settings.vi['sequence'] or ''

    @sequence.setter
    def sequence(self, value):
        self.settings.vi['sequence'] = value

    @property
    def partial_sequence(self):
        """
        Sometimes we need to store a partial sequence to obtain the commands'
        full name. Such is the case of `gD`, for example.
        """
        return self.settings.vi['partial_sequence'] or ''

    @partial_sequence.setter
    def partial_sequence(self, value):
        self.settings.vi['partial_sequence'] = value

    @property
    def mode(self):
        """
        Current mode. It isn't guaranteed that the underlying view's .sel()
        will be in a consistent state (for example, that it will at least
        have one non-empty region in visual mode.
        """
        return self.settings.vi['mode'] or modes.UNKNOWN

    @mode.setter
    def mode(self, value):
        self.settings.vi['mode'] = value

    @property
    def action(self):
        action = self.settings.vi['action'] or None
        if action:
            cls = getattr(cmd_defs, action['name'], None)
            if cls is None:
                cls = user_plugins.classes.get(action['name'], None)
            if cls is None:
                ValueError('unknown action: %s' % action)
            return cls.from_json(action['data'])

    @action.setter
    def action(self, value):
        serialized = value.serialize() if value else None
        self.settings.vi['action'] = serialized

    @property
    def motion(self):
        motion = self.settings.vi['motion'] or None
        if motion:
            cls = getattr(cmd_defs, motion['name'])
            return cls.from_json(motion['data'])

    @motion.setter
    def motion(self, value):
        serialized = value.serialize() if value else None
        self.settings.vi['motion'] = serialized

    @property
    def motion_count(self):
        return self.settings.vi['motion_count'] or ''

    @motion_count.setter
    def motion_count(self, value):
        assert value == '' or value.isdigit(), 'bad call'
        self.settings.vi['motion_count'] = value

    @property
    def action_count(self):
        return self.settings.vi['action_count'] or ''

    @action_count.setter
    def action_count(self, value):
        assert value == '' or value.isdigit(), 'bad call'
        self.settings.vi['action_count'] = value

    @property
    @settings.volatile
    def repeat_data(self):
        """
        Stores (type, cmd_name_or_key_seq, , mode) for '.' to use.

        `type` may be 'vi' or 'native'. `vi`-commands are executed via
        `ProcessNotation`, while `native`-commands are executed via .run_command().
        """
        return self.settings.vi['repeat_data'] or None

    @repeat_data.setter
    def repeat_data(self, value):
        assert isinstance(value, tuple) or isinstance(value, list), 'bad call'
        assert len(value) == 4, 'bad call'
        self.logger.info("setting repeat data {0}".format(value))
        self.settings.vi['repeat_data'] = value

    @property
    def count(self):
        """
        Calculates the actual count for the current command.
        """
        c = 1

        if self.action_count:
            c = int(self.action_count) or 1

        if self.motion_count:
            c *= (int(self.motion_count) or 1)

        if c < 1:
            raise ValueError('count must be positive')

        return c

    @property
    def xpos(self):
        """
        Stores the current xpos for carets.
        """
        return self.settings.vi['xpos'] or 0

    @xpos.setter
    def xpos(self, value):
        assert isinstance(value, int), '`value` must be an int'
        self.settings.vi['xpos'] = value

    @property
    def visual_block_direction(self):
        """
        Stores the visual block direction for the current selection.
        """
        return self.settings.vi['visual_block_direction'] or directions.DOWN

    @visual_block_direction.setter
    def visual_block_direction(self, value):
        assert isinstance(value, int), '`value` must be an int'
        self.settings.vi['visual_block_direction'] = value

    # FIXME(guillermooo): Remove this and use a global logger.
    @property
    def logger(self):
        global _logger
        return _logger

    @property
    def register(self):
        """
        Stores the current open register, as requested by the user.
        """
        return self.settings.vi['register'] or '"'

    @register.setter
    def register(self, value):
        assert len(str(value)) == 1, '`value` must be a character'
        self.logger.info('opening register {0}'.format(value))
        self.settings.vi['register'] = value
        self.must_capture_register_name = False

    @property
    def must_collect_input(self):
        """
        Returns `True` if state must collect input for the current motion or
        operator.
        """
        if self.motion and self.action:
            if self.motion.accept_input:
                return True

            return (self.action.accept_input and
                    self.action.input_parser.type == input_types.AFTER_MOTION)

        # Special case: `q` should stop the macro recorder if it's running and
        # not request further input from the user.
        if (isinstance(self.action, cmd_defs.ViToggleMacroRecorder) and
            self.is_recording):
                return False

        if (self.action and
            self.action.accept_input and
            self.action.input_parser.type == input_types.INMEDIATE):
                return True

        if self.motion:
            return (self.motion and self.motion.accept_input)

    @property
    def must_update_xpos(self):
        if self.motion and self.motion.updates_xpos:
            return True

        if self.action and self.action.updates_xpos:
            return True

    @property
    def is_recording(self):
        return self.settings.vi['recording'] or False

    @is_recording.setter
    def is_recording(self, value):
        assert isinstance(value, bool), 'bad call'
        self.settings.vi['recording'] = value

    def enter_normal_mode(self):
        self.mode = modes.NORMAL

    def enter_visual_mode(self):
        self.mode = modes.VISUAL

    def enter_visual_line_mode(self):
        self.mode = modes.VISUAL_LINE

    def enter_insert_mode(self):
        self.mode = modes.INSERT

    def enter_replace_mode(self):
        self.mode = modes.REPLACE

    def enter_select_mode(self):
        self.mode = modes.SELECT

    def enter_visual_block_mode(self):
        self.mode = modes.VISUAL_BLOCK

    def reset_sequence(self):
        # TODO(guillermooo): When is_recording, we could store the .sequence
        # and replay that, but we can't easily translate key presses in insert
        # mode to a Vintageous-friendly notation. A hybrid approach may work:
        # use a plain string for any command-mode-based mode, and native ST
        # commands for insert mode. That should make editing macros easier.
        self.sequence = ''

    def reset_partial_sequence(self):
        self.partial_sequence = ''

    def reset_register_data(self):
        self.register = '"'
        self.must_capture_register_name = False

    def reset_status(self):
        self.view.erase_status('vim-seq')
        if self.mode == modes.NORMAL:
            self.view.erase_status('vim-mode')

    def display_status(self):
        msg = "{0} {1}"
        mode_name = modes.to_friendly_name(self.mode)
        if mode_name:
            mode_name = '-- {0} --'.format(mode_name) if mode_name else ''
            self.view.set_status('vim-mode', mode_name)
        self.view.set_status('vim-seq', self.sequence)

    def must_scroll_into_view(self):
        return ((self.motion and self.motion.scroll_into_view) or
                (self.action and self.action.scroll_into_view))

    def scroll_into_view(self):
        v = sublime.active_window().active_view()
        # TODO(guillermooo): Maybe some commands should show their
        # surroundings too?
        # Make sure we show the first caret on the screen, but don't show
        # its surroundings.
        v.show(v.sel()[0], False)

    def reset(self):
        # TODO: Remove this when we've ported all commands. This is here for
        # retrocompatibility.
        self.reset_command_data()

    def reset_command_data(self):
        # Resets all temporary data needed to build a command or partial
        # command.
        self.update_xpos()
        if self.must_scroll_into_view():
            self.scroll_into_view()

        self.action and self.action.reset()
        self.action = None
        self.motion and self.motion.reset()
        self.motion = None
        self.action_count = ''
        self.motion_count = ''

        self.reset_sequence()
        self.reset_partial_sequence()
        self.reset_register_data()
        self.reset_status()

    def reset_volatile_data(self):
        """
        Resets window- or application-wide data to their default values when
        starting a new Vintageous session.
        """
        self.glue_until_normal_mode = False
        self.view.run_command('unmark_undo_groups_for_gluing')
        self.processing_notation = False
        self.non_interactive = False
        self.reset_during_init = True

    def update_xpos(self, force=False):
        if self.must_update_xpos or force:
            try:
                # TODO: we should check the current mode instead. ============
                sel = self.view.sel()[0]
                pos = sel.b
                if not sel.empty():
                    if sel.a < sel.b:
                        pos -= 1
                # ============================================================
                r = sublime.Region(self.view.line(pos).a, pos)
                counter = Counter(self.view.substr(r))
                tab_size = self.view.settings().get('tab_size')
                xpos = (self.view.rowcol(pos)[1] +
                        ((counter['\t'] * tab_size) - counter['\t']))
            except Exception as e:
                print(e)
                _logger.error(
                    'Vintageous: Error when setting xpos. Defaulting to 0.')
                self.xpos = 0
                return
            else:
                self.xpos = xpos

    def _set_parsers(self, command):
        """
        Returns `True` if we've had to run an immediate parser via an input
        panel.
        """
        if command.accept_input:
            return self._run_parser_via_panel(command)

    def _run_parser_via_panel(self, command):
        """
        Returns `True` if the current parser needs to be run via a panel.

        If needed, it runs the input-panel-based parser.
        """
        if command.input_parser.type == input_types.VIA_PANEL:
            if self.non_interactive:
                return False
            sublime.active_window().run_command(command.input_parser.command)
            return True
        return False

    def process_user_input2(self, key):
        assert self.must_collect_input, "call only if input is required"

        _logger.info('[State] processing input {0}'.format(key))

        if self.motion and self.motion.accept_input:
            motion = self.motion
            val = motion.accept(key)
            self.motion = motion
            return val

        action = self.action
        val = action.accept(key)
        self.action = action
        return val

    def set_command(self, command):
        """
        Sets the current command to @command.

        @command
          A command definition as found in `keys.py`.
        """
        assert isinstance(command, cmd_base.ViCommandDefBase), \
            'ViCommandDefBase expected, got {0}'.format(type(command))

        if isinstance(command, cmd_base.ViMotionDef):
            if self.runnable():
                # We already have a motion, so this looks like an error.
                raise ValueError('too many motions')
            self.motion = command

            if self.mode == modes.OPERATOR_PENDING:
                self.mode = modes.NORMAL

            if self._set_parsers(command):
                return

        elif isinstance(command, cmd_base.ViOperatorDef):
            if self.runnable():
                # We already have an action, so this looks like an error.
                raise ValueError('too many actions')
            self.action = command

            if (self.action.motion_required and
                not self.in_any_visual_mode()):
                    self.mode = modes.OPERATOR_PENDING

            if self._set_parsers(command):
                return

        else:
            self.logger.info("[State] command: {0}".format(command))
            raise ValueError('unexpected command type')

    def in_any_visual_mode(self):
        return (self.mode in (modes.VISUAL,
                              modes.VISUAL_LINE,
                              modes.VISUAL_BLOCK))

    def can_run_action(self):
        if (self.action and
                (not self.action['motion_required'] or
                 self.in_any_visual_mode())
                ):
                    return True

    def get_visual_repeat_data(self):
        """Returns the data needed to restore visual selections before
        repeating a visual mode command in normal mode.
        """
        if self.mode not in (modes.VISUAL, modes.VISUAL_LINE):
            return

        first = first_sel(self.view)
        lines = (utils.row_at(self.view, first.end()) -
                 utils.row_at(self.view, first.begin()))

        if lines > 0:
            chars = utils.col_at(self.view, first.end())
        else:
            chars = first.size()

        return (lines, chars, self.mode)

    def restore_visual_data(self, data):
        rows, chars, old_mode = data
        first = first_sel(self.view)

        if old_mode == modes.VISUAL:
            if rows > 0:
                end = self.view.text_point(utils.row_at(self.view, first.b) +
                                           rows, chars)
            else:
                end = first.b + chars

            self.view.sel().add(sublime.Region(first.b, end))
            self.mode = modes.VISUAL

        elif old_mode == modes.VISUAL_LINE:
            rows, _, old_mode = data
            begin = self.view.line(first.b).a
            end = self.view.text_point(utils.row_at(self.view, begin) +
                                       (rows - 1), 0)
            end = self.view.full_line(end).b
            self.view.sel().add(sublime.Region(begin, end))
            self.mode = modes.VISUAL_LINE

    def start_recording(self):
        self.is_recording = True
        State.macro_steps = []
        self.view.set_status('vim-recorder', 'Recording...')

    def stop_recording(self):
        self.is_recording = False
        self.view.erase_status('vim-recorder')

    def add_macro_step(self, cmd_name, args):
        if self.is_recording:
            if cmd_name == '_vi_q':
                # don't store the ending macro step
                return

            if self.runnable and not self.glue_until_normal_mode:
                State.macro_steps.append((cmd_name, args))

    def runnable(self):
        """
        Returns `True` if we can run the state data as it is.
        """
        if self.must_collect_input:
            return False

        if self.action and self.motion:
            if self.mode != modes.NORMAL:
                raise ValueError('wrong mode')
            return True

        if self.can_run_action():
            if self.mode == modes.OPERATOR_PENDING:
                raise ValueError('wrong mode')
            return True

        if self.motion:
            if self.mode == modes.OPERATOR_PENDING:
                raise ValueError('wrong mode')
            return True

        return False

    def eval(self):
        """
        Run data as a command if possible.
        """
        if not self.runnable():
            return

        if self.action and self.motion:
            action_cmd = self.action.translate(self)
            motion_cmd = self.motion.translate(self)
            self.logger.info(
                '[State] full command, switching to internal normal mode')
            self.mode = modes.INTERNAL_NORMAL

            # TODO: Make a requirement that motions and actions take a
            # 'mode' param.
            if 'mode' in action_cmd['action_args']:
                action_cmd['action_args']['mode'] = modes.INTERNAL_NORMAL

            if 'mode' in motion_cmd['motion_args']:
                motion_cmd['motion_args']['mode'] = modes.INTERNAL_NORMAL

            args = action_cmd['action_args']
            args['count'] = 1
            # let the action run the motion within its edit object so that
            # we don't need to worry about grouping edits to the buffer.
            args['motion'] = motion_cmd
            self.logger.info(
                '[Stage] motion in motion+action: {0}'.format(motion_cmd))

            if self.glue_until_normal_mode and not self.processing_notation:
                # We need to tell Sublime Text now that it should group
                # all the next edits until we enter normal mode again.
                sublime.active_window().run_command(
                    'mark_undo_groups_for_gluing')

            self.add_macro_step(action_cmd['action'], args)

            sublime.active_window().run_command(action_cmd['action'], args)
            if not self.non_interactive:
                if self.action.repeatable:
                    self.repeat_data = ('vi', str(self.sequence),
                                        self.mode, None)
            self.reset_command_data()
            return

        if self.motion:
            motion_cmd = self.motion.translate(self)
            self.logger.info(
                '[State] lone motion cmd: {0}'.format(motion_cmd))

            self.add_macro_step(motion_cmd['motion'],
                                motion_cmd['motion_args'])

            # We know that all motions are subclasses of ViTextCommandBase,
            # so it's safe to call them from the current view.
            self.view.run_command(motion_cmd['motion'],
                                  motion_cmd['motion_args'])

        if self.action:
            action_cmd = self.action.translate(self)
            self.logger.info('[Stage] lone action cmd '.format(action_cmd))
            if self.mode == modes.NORMAL:
                self.logger.info(
                    '[State] switching to internal normal mode')
                self.mode = modes.INTERNAL_NORMAL

                if 'mode' in action_cmd['action_args']:
                    action_cmd['action_args']['mode'] = \
                        modes.INTERNAL_NORMAL
            elif self.mode in (modes.VISUAL, modes.VISUAL_LINE):
                self.view.add_regions('visual_sel', list(self.view.sel()))

            # Some commands, like 'i' or 'a', open a series of edits that
            # need to be grouped together unless we are gluing a larger
            # sequence through ProcessNotation. For example, aFOOBAR<Esc> should
            # be grouped atomically, but not inside a sequence like
            # iXXX<Esc>llaYYY<Esc>, where we want to group the whole
            # sequence instead.
            if self.glue_until_normal_mode and not self.processing_notation:
                sublime.active_window().run_command(
                    'mark_undo_groups_for_gluing')

            seq = self.sequence
            visual_repeat_data = self.get_visual_repeat_data()
            action = self.action

            self.add_macro_step(action_cmd['action'],
                                action_cmd['action_args'])

            sublime.active_window().run_command(action_cmd['action'],
                                                action_cmd['action_args'])

            if not (self.processing_notation and self.glue_until_normal_mode):
                if action.repeatable:
                    self.repeat_data = ('vi', seq, self.mode,
                                        visual_repeat_data)

        self.logger.info(
            'running command: action: {0} motion: {1}'.format(self.action,
                                                              self.motion))

        if self.mode == modes.INTERNAL_NORMAL:
            self.enter_normal_mode()

        self.reset_command_data()
