import sublime
import sublime_plugin

from Vintageous.ex.ex_command_parser import parse_command
from Vintageous.ex.ex_command_parser import EX_COMMANDS
from Vintageous.ex import ex_error


COMPLETIONS = sorted([x[0] for x in EX_COMMANDS.keys()])

EX_HISTORY_MAX_LENGTH = 20
EX_HISTORY = {
    'cmdline': [],
    'searches': []
}


def update_command_line_history(item, slot_name):
    if len(EX_HISTORY[slot_name]) >= EX_HISTORY_MAX_LENGTH:
        EX_HISTORY[slot_name] = EX_HISTORY[slot_name][1:]
    if item in EX_HISTORY[slot_name]:
        EX_HISTORY[slot_name].pop(EX_HISTORY[slot_name].index(item))
    EX_HISTORY[slot_name].append(item)


class ViColonInput(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return len(self.window.views()) > 0

    def __init__(self, window):
        sublime_plugin.WindowCommand.__init__(self, window)

    def run(self, initial_text=':', cmd_line=''):
        # non-interactive call
        if cmd_line:
            self.non_interactive = True
            self.on_done(cmd_line)
            return
        v = self.window.show_input_panel('', initial_text,
                                                    self.on_done, None, None)
        v.set_syntax_file('Packages/Vintageous/VintageousEx Cmdline.tmLanguage')
        v.settings().set('gutter', False)
        v.settings().set('rulers', [])

    def on_done(self, cmd_line):
        if not getattr(self, 'non_interactive', None):
            update_command_line_history(cmd_line, 'cmdline')
        else:
            self.non_interactive = False
        ex_cmd = parse_command(cmd_line)
        print(ex_cmd)

        if ex_cmd and ex_cmd.parse_errors:
            ex_error.display_error(ex_cmd.parse_errors[0])
            return
        if ex_cmd and ex_cmd.name:
            if ex_cmd.can_have_range:
                ex_cmd.args["line_range"] = ex_cmd.line_range
            if ex_cmd.forced:
                ex_cmd.args['forced'] = ex_cmd.forced
            self.window.run_command(ex_cmd.command, ex_cmd.args)
        else:
            ex_error.display_error(ex_error.ERR_UNKNOWN_COMMAND, cmd_line)


class ViColonRepeatLast(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return (len(self.window.views()) > 0) and (len(EX_HISTORY['cmdline']) > 0)

    def run(self):
        self.window.run_command('vi_colon_input', {'cmd_line': EX_HISTORY['cmdline'][-1]})


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

        compls = [x for x in COMPLETIONS if x.startswith(prefix) and x != prefix]
        self.CACHED_COMPLETION_PREFIXES = [prefix] + compls
        # S3 can only handle lists, not iterables.
        self.CACHED_COMPLETIONS = list(zip([prefix] + compls, compls + [prefix]))

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
