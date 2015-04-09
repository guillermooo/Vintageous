import sublime
import sublime_plugin

import os

from Vintageous.ex import ex_error
from Vintageous.ex import command_names
from Vintageous.ex.completions import iter_paths
from Vintageous.ex.completions import parse
from Vintageous.ex.completions import parse_for_setting
from Vintageous.ex.completions import wants_fs_completions
from Vintageous.ex.completions import wants_setting_completions
from Vintageous.ex.ex_error import display_error2
from Vintageous.ex.ex_error import VimError
from Vintageous.ex.parsers.new.parser import parse_ex_command
from Vintageous.ex.parsers.new.scanner_command_goto import TokenCommandGoto
from Vintageous.state import State
from Vintageous.vi.settings import iter_settings
from Vintageous.vi.sublime import show_ipanel
from Vintageous.vi.utils import mark_as_widget
from Vintageous.vi.utils import modes


def plugin_loaded():
    v = sublime.active_window().active_view()
    state = State(v)
    d = os.path.dirname(v.file_name()) if v.file_name() else os.getcwd()
    state.settings.vi['_cmdline_cd'] = d


COMPLETIONS = sorted([x[0] for x in command_names])

EX_HISTORY_MAX_LENGTH = 20
EX_HISTORY = {
    'cmdline': [],
    'searches': []
}


def update_command_line_history(slot_name, item):
    if len(EX_HISTORY[slot_name]) >= EX_HISTORY_MAX_LENGTH:
        EX_HISTORY[slot_name] = EX_HISTORY[slot_name][1:]
    if item in EX_HISTORY[slot_name]:
        EX_HISTORY[slot_name].pop(EX_HISTORY[slot_name].index(item))
    EX_HISTORY[slot_name].append(item)


class ViColonInput(sublime_plugin.WindowCommand):
    # Indicates whether the user issued the call.
    interactive_call = True
    def is_enabled(self):
        return bool(self.window.active_view())

    def __init__(self, window):
        sublime_plugin.WindowCommand.__init__(self, window)

    def adjust_initial_text(self, text):
        state = State(self.window.active_view())
        if state.mode in (modes.VISUAL, modes.VISUAL_LINE):
            text = ":'<,'>" + text[1:]
        return text

    def run(self, initial_text=':', cmd_line=''):
        if cmd_line:
            # The caller has provided a command, to we're not in interactive
            # mode -- just run the command.
            ViColonInput.interactive_call = False
            self.on_done(cmd_line)
            return
        else:
            ViColonInput.interactive_call = True

        FsCompletion.invalidate()

        v = mark_as_widget(show_ipanel(self.window,
               initial_text=self.adjust_initial_text(initial_text),
               on_done=self.on_done,
               on_change=self.on_change))

        v.set_syntax_file('Packages/Vintageous/VintageousEx Cmdline.tmLanguage')
        v.settings().set('gutter', False)
        v.settings().set('rulers', [])

        state = State(self.window.active_view())
        state.reset_during_init = False

    def on_change(self, s):
        if ViColonInput.interactive_call:
            cmd, prefix, only_dirs = parse(s)
            if cmd:
                FsCompletion.prefix = prefix
                FsCompletion.is_stale = True
            cmd, prefix, _ = parse_for_setting(s)
            if cmd:
                ViSettingCompletion.prefix = prefix
                ViSettingCompletion.is_stale = True

            if not cmd:
                return
        ViColonInput.interactive_call = True

    def on_done(self, cmd_line):
        if ViColonInput.interactive_call:
            update_command_line_history('cmdline', cmd_line)

        try:
            # Use new parser for some commands.
            parsed_new = parse_ex_command(cmd_line[1:])

            if not parsed_new.command:
                parsed_new.command = TokenCommandGoto()

            self.window.run_command(parsed_new.command.target_command, {'command_line': cmd_line[1:]})
            return
        except VimError as ve:
            # only new code emits VimErrors, so handle it.
            display_error2(ve)
            return
        except Exception as e:
            # let the old ex code take care of this
            print ('DEBUG::Vintageous:', e, '(', cmd_line, ')')
            return

class ViColonRepeatLast(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return ((len(self.window.views()) > 0) and
                (len(EX_HISTORY['cmdline']) > 0))

    def run(self):
        self.window.run_command('vi_colon_input',
                                {'cmd_line': EX_HISTORY['cmdline'][-1]})


class ExCompletionsProvider(sublime_plugin.EventListener):
    CACHED_COMPLETIONS = []
    CACHED_COMPLETION_PREFIXES = []

    def on_query_completions(self, view, prefix, locations):
        if view.score_selector(0, 'text.excmdline') == 0:
            return []

        if len(prefix) + 1 != view.size():
            return []

        if prefix and prefix in self.CACHED_COMPLETION_PREFIXES:
            return self.CACHED_COMPLETIONS

        compls = [x for x in COMPLETIONS if x.startswith(prefix) and
                                            x != prefix]
        self.CACHED_COMPLETION_PREFIXES = [prefix] + compls
        # S3 can only handle lists, not iterables.
        self.CACHED_COMPLETIONS = list(zip([prefix] + compls,
                                           compls + [prefix]))

        return self.CACHED_COMPLETIONS


class CycleCmdlineHistory(sublime_plugin.TextCommand):
    HISTORY_INDEX = None
    def run(self, edit, backwards=False):
        if CycleCmdlineHistory.HISTORY_INDEX is None:
            CycleCmdlineHistory.HISTORY_INDEX = -1 if backwards else 0
        else:
            CycleCmdlineHistory.HISTORY_INDEX += -1 if backwards else 1

        if CycleCmdlineHistory.HISTORY_INDEX == len(EX_HISTORY['cmdline']) or \
            CycleCmdlineHistory.HISTORY_INDEX < -len(EX_HISTORY['cmdline']):
                CycleCmdlineHistory.HISTORY_INDEX = -1 if backwards else 0

        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, \
                EX_HISTORY['cmdline'][CycleCmdlineHistory.HISTORY_INDEX])


class HistoryIndexRestorer(sublime_plugin.EventListener):
    def on_deactivated(self, view):
        # Because views load asynchronously, do not restore history index
        # .on_activated(), but here instead. Otherwise, the .score_selector()
        # call won't yield the desired results.
        if view.score_selector(0, 'text.excmdline') > 0:
            CycleCmdlineHistory.HISTORY_INDEX = None


class WriteFsCompletion(sublime_plugin.TextCommand):
    def run(self, edit, cmd, completion):
        if self.view.score_selector(0, 'text.excmdline') == 0:
            return

        ViColonInput.interactive_call = False
        self.view.sel().clear()
        self.view.replace(edit, sublime.Region(0, self.view.size()),
                          cmd + ' ' + completion)
        self.view.sel().add(sublime.Region(self.view.size()))


class FsCompletion(sublime_plugin.TextCommand):
    # Last user-provided path string.
    prefix = ''
    frozen_dir = ''
    is_stale = False
    items = None

    @staticmethod
    def invalidate():
        FsCompletion.prefix = ''
        FsCompletion.frozen_dir = ''
        FsCompletion.is_stale = True
        FsCompletion.items = None


    def run(self, edit):
        if self.view.score_selector(0, 'text.excmdline') == 0:
            return

        state = State(self.view)
        FsCompletion.frozen_dir = (FsCompletion.frozen_dir or
                                   (state.settings.vi['_cmdline_cd'] + '/'))

        cmd, prefix, only_dirs = parse(self.view.substr(self.view.line(0)))
        if not cmd:
            return

        if not (FsCompletion.prefix or FsCompletion.items) and prefix:
            FsCompletion.prefix = prefix
            FsCompletion.is_stale = True

        if prefix == '..':
            FsCompletion.prefix = '../'
            self.view.run_command('write_fs_completion', {
                                                    'cmd': cmd,
                                                    'completion': '../'})

        if prefix == '~':
            path = os.path.expanduser(prefix) + '/'
            FsCompletion.prefix = path
            self.view.run_command('write_fs_completion', {
                                                    'cmd': cmd,
                                                    'completion': path})
            return

        if (not FsCompletion.items) or FsCompletion.is_stale:
            FsCompletion.items = iter_paths(from_dir=FsCompletion.frozen_dir,
                                            prefix=FsCompletion.prefix,
                                            only_dirs=only_dirs)
            FsCompletion.is_stale = False

        try:
            self.view.run_command('write_fs_completion', {
                                    'cmd': cmd,
                                    'completion': next(FsCompletion.items)
                                 })
        except StopIteration:
            FsCompletion.items = iter_paths(prefix=FsCompletion.prefix,
                                            from_dir=FsCompletion.frozen_dir,
                                            only_dirs=only_dirs)
            self.view.run_command('write_fs_completion', {
                                    'cmd': cmd,
                                    'completion': FsCompletion.prefix
                                  })


class ViSettingCompletion(sublime_plugin.TextCommand):
    # Last user-provided path string.
    prefix = ''
    is_stale = False
    items = None

    @staticmethod
    def invalidate():
        ViSettingCompletion.prefix = ''
        is_stale = True
        items = None

    def run(self, edit):
        if self.view.score_selector(0, 'text.excmdline') == 0:
            return

        cmd, prefix, _ = parse_for_setting(self.view.substr(self.view.line(0)))
        if not cmd:
            return
        if (ViSettingCompletion.prefix is None) and prefix:
            ViSettingCompletion.prefix = prefix
            ViSettingCompletion.is_stale = True
        elif ViSettingCompletion.prefix is None:
            ViSettingCompletion.items = iter_settings('')
            ViSettingCompletion.is_stale = False

        if not ViSettingCompletion.items or ViSettingCompletion.is_stale:
            ViSettingCompletion.items = iter_settings(ViSettingCompletion.prefix)
            ViSettingCompletion.is_stale = False

        try:
            self.view.run_command('write_fs_completion',
                                  {'cmd': cmd,
                                   'completion': next(ViSettingCompletion.items)})
        except StopIteration:
            try:
                ViSettingCompletion.items = iter_settings(ViSettingCompletion.prefix)
                self.view.run_command('write_fs_completion',
                                      {'cmd': cmd,
                                       'completion': next(ViSettingCompletion.items)})
            except StopIteration:
                return

class CmdlineContextProvider(sublime_plugin.EventListener):
    """
    Provides contexts for the cmdline input panel.
    """
    def on_query_context(self, view, key, operator, operand, match_all):
        if view.score_selector(0, 'text.excmdline') == 0:
            return

        if key == 'vi_cmdline_at_fs_completion':
            value = wants_fs_completions(view.substr(view.line(0)))
            value = value and view.sel()[0].b == view.size()
            if operator == sublime.OP_EQUAL:
                if operand == True:
                    return value
                elif operand == False:
                    return not value

        if key == 'vi_cmdline_at_setting_completion':
            value = wants_setting_completions(view.substr(view.line(0)))
            value = value and view.sel()[0].b == view.size()
            if operator == sublime.OP_EQUAL:
                if operand == True:
                    return value
                elif operand == False:
                    return not value
