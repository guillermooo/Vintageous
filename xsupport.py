"""Assorted commands.
"""

import os
import threading

import sublime
import sublime_plugin

from Vintageous.state import _init_vintageous
from Vintageous.state import State
from Vintageous.vi import settings
from Vintageous.vi import cmd_defs
from Vintageous.vi.dot_file import DotFile
from Vintageous.vi.utils import modes
from Vintageous.vi.utils import regions_transformer


class _vi_slash_on_parser_done(sublime_plugin.WindowCommand):

    def run(self, key=None):
        state = State(self.window.active_view())
        state.motion = cmd_defs.ViSearchForwardImpl()
        state.last_buffer_search = (state.motion._inp or
            state.last_buffer_search)


class _vi_question_mark_on_parser_done(sublime_plugin.WindowCommand):

    def run(self, key=None):
        state = State(self.window.active_view())
        state.motion = cmd_defs.ViSearchBackwardImpl()
        state.last_buffer_search = (state.motion._inp or
            state.last_buffer_search)


# TODO: Test me.
class VintageStateTracker(sublime_plugin.EventListener):

    def on_post_save(self, view):
        # Ensure the carets are within valid bounds. For instance, this is a
        # concern when `trim_trailing_white_space_on_save` is set to true.
        state = State(view)
        view.run_command('_vi_adjust_carets', {'mode': state.mode})

    def on_query_context(self, view, key, operator, operand, match_all):
        vintage_state = State(view)
        return vintage_state.context.check(key, operator, operand, match_all)

    def on_close(self, view):
        settings.destroy(view)


class ViMouseTracker(sublime_plugin.EventListener):

    def on_text_command(self, view, command, args):
        if command == 'drag_select':
            state = State(view)

            if state.mode in (modes.VISUAL, modes.VISUAL_LINE,
                              modes.VISUAL_BLOCK):
                if (args.get('extend') or (args.get('by') == 'words') or
                    args.get('additive')):
                        return

                elif not args.get('extend'):
                    return ('sequence', {'commands': [
                        ['drag_select', args], ['_enter_normal_mode', {
                            'mode': state.mode}]
                    ]})

            elif state.mode == modes.NORMAL:
                # TODO(guillermooo): Dragging the mouse does not seem to
                # fire a different event than simply clicking. This makes it
                # hard to update the xpos.
                if args.get('extend') or (args.get('by') == 'words'):
                    return ('sequence', {'commands': [
                        ['drag_select', args], ['_enter_visual_mode', {
                            'mode': state.mode}]
                    ]})


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

    def on_deactivated(self, view):
        self.timer = threading.Timer(0.25, self.action)
        self.timer.start()


class _vi_adjust_carets(sublime_plugin.TextCommand):

    def run(self, edit, mode=None):
        def f(view, s):
            if mode in (modes.NORMAL, modes.INTERNAL_NORMAL):
                if  ((view.substr(s.b) == '\n' or s.b == view.size())
                     and not view.line(s.b).empty()):
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
        DotFile.from_user().run()
        print("Package.Vintageous: State reset.")
        sublime.status_message("Vintageous: State reset")


class ForceExitFromCommandMode(sublime_plugin.WindowCommand):
    """
    A sort of a panic button.
    """
    def run(self):
        v = self.window.active_view()
        v.settings().erase('vintage')
        # XXX: What happens exactly when the user presses Esc again now? Which
        #      more are we in?

        v.settings().set('command_mode', False)
        v.settings().set('inverse_caret_state', False)

        print("Vintageous: Exiting from command mode.")
        sublime.status_message("Vintageous: Exiting from command mode.")


class VintageousToggleCtrlKeys(sublime_plugin.WindowCommand):

    def run(self):
        prefs = sublime.load_settings('Preferences.sublime-settings')
        value = prefs.get('vintageous_use_ctrl_keys', False)
        prefs.set('vintageous_use_ctrl_keys', (not value))
        sublime.save_settings('Preferences.sublime-settings')
        status = 'enabled' if (not value) else 'disabled'
        print("Package.Vintageous: Use of Ctrl- keys {0}.".format(status))
        sublime.status_message("Vintageous: Use of Ctrl- keys {0}"
                               .format(status))


class ReloadVintageousSettings(sublime_plugin.TextCommand):

    def run(self, edit):
        DotFile.from_user().run()


class VintageousOpenConfigFile(sublime_plugin.WindowCommand):
    """Opens or creates $packages/User/.vintageousrc.
    """

    def run(self):
        path = os.path.realpath(os.path.join(sublime.packages_path(),
                                'User/.vintageousrc'))
        if os.path.exists(path):
            self.window.open_file(path)
        else:
            with open(path, 'w'):
                pass

            self.window.open_file(path)
