import threading

import sublime
import sublime_plugin

from Vintageous.vi.keys import cmd_defs
from Vintageous.vi.keys import cmds
from Vintageous.state import State
from Vintageous.state import _init_vintageous
from Vintageous.vi.utils import regions_transformer
from Vintageous.vi.utils import modes
from Vintageous.vi import utils
from Vintageous.vi.dot_file import DotFile


class _vi_slash_on_parser_done(sublime_plugin.WindowCommand):
    def run(self, key=None):
        state = State(self.window.active_view())
        state.motion = cmd_defs[state.mode][cmds.SLASH_IMPL]
        state.last_buffer_search = state.user_input or state.last_buffer_search
        # XXX: Is this right?
        if state.input_parsers:
            new_parsers = state.input_parsers
            new_parsers.pop()
            state.input_parsers = new_parsers


class _vi_question_mark_on_parser_done(sublime_plugin.WindowCommand):
    def run(self, key=None):
        state = State(self.window.active_view())
        state.motion = cmd_defs[state.mode][cmds.QUESTION_MARK_IMPL]
        state.last_buffer_search = state.user_input or state.last_buffer_search
        # XXX: Is this right?
        if state.input_parsers:
            new_parsers = state.input_parsers
            new_parsers.pop()
            state.input_parsers = new_parsers


class _vi_r_on_parser_done(sublime_plugin.WindowCommand):
    def run(self, key=None):
        state = State(self.window.active_view())
        if not state.user_input:
            state.user_input = utils.translate_char(key)


# TODO: Test me.
class VintageStateTracker(sublime_plugin.EventListener):
    def on_load(self, view):
        _init_vintageous(view)

    def on_post_save(self, view):
        # Ensure the carets are within valid bounds. For instance, this is a concern when
        # `trim_trailing_white_space_on_save` is set to true.
        state = State(view)
        view.run_command('_vi_adjust_carets', {'mode': state.mode})

    def on_query_context(self, view, key, operator, operand, match_all):
        vintage_state = State(view)
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


class _vi_adjust_carets(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode in (modes.NORMAL, modes.INTERNAL_NORMAL):
                if  ((view.substr(s.b) == '\n' or s.b == view.size())
                     and not view.line(s.b).empty()):
                        # print('adjusting carets')
                        return sublime.Region(s.b - 1)
            return s

        regions_transformer(self.view, f)


class Sequence(sublime_plugin.TextCommand):
    """Required so that mark_undo_groups_for_gluing and friends work.
    """
    def run(self, edit, commands):
        for cmd, args in commands:
            self.view.run_command(cmd, args)


class ResetVintageous(sublime_plugin.WindowCommand):
    def run(self):
        v = self.window.active_view()
        v.settings().erase('vintage')
        _init_vintageous(v)
        print("Package.Vintageous: State reset.")
        sublime.status_message("Vintageous: State reset")

class VintageousToggleCtrlKeys(sublime_plugin.WindowCommand):
    def run(self):
        prefs = sublime.load_settings('Preferences.sublime-settings')
        value = prefs.get('vintageous_use_ctrl_keys', False)
        prefs.set('vintageous_use_ctrl_keys', (not value))
        sublime.save_settings('Preferences.sublime-settings')
        status = 'enabled' if (not value) else 'disabled'
        print("Package.Vintageous: Use of Ctrl- keys {0}.".format(status))
        sublime.status_message("Vintageous: Use of Ctrl- keys {0}".format(status))

class ReloadVintageousSettings(sublime_plugin.TextCommand):
    def run(self, edit):
        DotFile.from_user().run()
