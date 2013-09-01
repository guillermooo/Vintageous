import sublime
import sublime_plugin

import os
import re
import subprocess
import sys

from Vintageous.ex import ex_error
from Vintageous.ex import ex_range
from Vintageous.ex import parsers
from Vintageous.ex import shell
from Vintageous.ex.plat.windows import get_oem_cp
from Vintageous.ex.plat.windows import get_startup_info
from Vintageous.ex_main import FsCompletion
from Vintageous.state import IrreversibleTextCommand
from Vintageous.state import VintageState
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.sublime import has_dirty_buffers
from Vintageous.vi.settings import set_local
from Vintageous.vi.settings import set_global


GLOBAL_RANGES = []
CURRENT_LINE_RANGE = {'left_ref': '.', 'left_offset': 0,
                      'left_search_offsets': [], 'right_ref': None,
                      'right_offset': 0, 'right_search_offsets': []}


def changing_cd(f, *args, **kwargs):
    def inner(*args, **kwargs):
        try:
            state = VintageState(args[0].view)
        except AttributeError:
            state = VintageState(args[0].window.active_view())

        old = os.getcwd()
        try:
            # FIXME: Under some circumstances, like when switching projects to
            # a file whose _cmdline_cd has not been set, _cmdline_cd might
            # return 'None'. In such cases, change to the actual current
            # directory as a last measure. (We should probably fix this anyway).
            os.chdir(state.settings.vi['_cmdline_cd'] or old)
            f(*args, **kwargs)
        finally:
            os.chdir(old)
    return inner


def gather_buffer_info(v):
    """gathers data to be displayed by :ls or :buffers
    """
    path = v.file_name()
    if path:
        parent, leaf = os.path.split(path)
        parent = os.path.basename(parent)
        path = os.path.join(parent, leaf)
    else:
        path = v.name() or str(v.buffer_id())
        leaf = v.name() or 'untitled'

    status = []
    if not v.file_name():
        status.append("t")
    if v.is_dirty():
        status.append("*")
    if v.is_read_only():
        status.append("r")

    if status:
        leaf += ' (%s)' % ', '.join(status)
    return [leaf, path]


def get_region_by_range(view, line_range=None, as_lines=False):
    # If GLOBAL_RANGES exists, the ExGlobal command has been run right before
    # the current command, and we know we must process these lines.
    global GLOBAL_RANGES
    if GLOBAL_RANGES:
        rv = GLOBAL_RANGES[:]
        GLOBAL_RANGES = []
        return rv

    if line_range:
        vim_range = ex_range.VimRange(view, line_range)
        if as_lines:
            return vim_range.lines()
        else:
            return vim_range.blocks()


class ExTextCommandBase(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def line_range_to_text(self, line_range):
        line_block = get_region_by_range(self.view, line_range=line_range)
        line_block = [self.view.substr(r) for r in line_block]
        return '\n'.join(line_block) + '\n'

    def serialize_sel(self):
        sels = [(r.a, r.b) for r in list(self.view.sel())]
        self.view.settings().set('ex_data', {'prev_sel': sels})

    def deserialize_sel(self, name='next_sel'):
        return self.view.settings().get('ex_data')[name] or []

    def set_sel(self):
        sel = self.deserialize_sel()
        self.view.sel().clear()
        self.view.sel().add_all([sublime.Region(b) for (a, b) in sel])

    def set_next_sel(self, data):
        self.view.settings().set('ex_data', {'next_sel': data})

    def set_mode(self):
        state = VintageState(self.view)
        state.enter_normal_mode()
        self.view.run_command('vi_enter_normal_mode')

    def run(self, edit, *args, **kwargs):
        self.serialize_sel()
        self.run_ex_command(edit, *args, **kwargs)
        self.set_sel()
        self.set_mode()


class ExAddressableCommandMixin(object):
    def get_address(self, address):
        # FIXME: We must fix the parser.
        if address == '0':
            return 0
        address_parser = parsers.cmd_line.AddressParser(address)
        parsed_address = address_parser.parse()
        address = ex_range.calculate_address(self.view, parsed_address)
        return address


class ExGoto(sublime_plugin.TextCommand):
    def run(self, edit, line_range=None):
        if not line_range['text_range']:
            # No-op: user issued ":".
            return
        ranges, _ = ex_range.new_calculate_range(self.view, line_range)
        a, b = ranges[0]
        # FIXME: This should be handled by the parser.
        # FIXME: In Vim, 0 seems to equal 1 in ranges.
        b = b if line_range['text_range'] != '0' else 1
        state = VintageState(self.view)
        # FIXME: In Visual mode, goto line does some weird stuff.
        if state.mode == MODE_NORMAL:
            # TODO: push all this code down to ViGoToLine?
            self.view.window().run_command('vi_add_to_jump_list')
            self.view.run_command('vi_go_to_line', {'line': b, 'mode': MODE_NORMAL})
            self.view.window().run_command('vi_add_to_jump_list')
            self.view.show(self.view.sel()[0])
        elif state.mode in (MODE_VISUAL, MODE_VISUAL_LINE) and line_range['right_offset']:
            # TODO: push all this code down to ViGoToLine?
            self.view.run_command('vi_enter_normal_mode')
            self.view.window().run_command('vi_add_to_jump_list')
            # FIXME: The parser fails with '<,'>100. 100 is not the right_offset, but an argument.
            b = self.view.rowcol(self.view.sel()[0].b - 1)[0] + line_range['right_offset'] + 1
            self.view.run_command('vi_go_to_line', {'line': b, 'mode': MODE_NORMAL})
            self.view.window().run_command('vi_add_to_jump_list')
            self.view.show(self.view.sel()[0])
            state.display_partial_command()


class ExShellOut(sublime_plugin.TextCommand):
    """Ex command(s): :!cmd, :'<,>'!cmd

    Run cmd in a system's shell or filter selected regions through external
    command.
    """

    @changing_cd
    def run(self, edit, line_range=None, shell_cmd=''):
        try:
            if line_range['text_range']:
                shell.filter_thru_shell(
                                view=self.view,
                                edit=edit,
                                regions=get_region_by_range(self.view, line_range=line_range),
                                cmd=shell_cmd)
            else:
                # TODO: Read output into output panel.
                # shell.run_and_wait(self.view, shell_cmd)
                out = shell.run_and_read(self.view, shell_cmd)

                output_view = self.view.window().create_output_panel('vi_out')
                output_view.settings().set("line_numbers", False)
                output_view.settings().set("gutter", False)
                output_view.settings().set("scroll_past_end", False)
                output_view = self.view.window().create_output_panel('vi_out')
                output_view.run_command('append', {'characters': out,
                                                   'force': True,
                                                   'scroll_to_end': True})
                self.view.window().run_command("show_panel", {"panel": "output.vi_out"})
        except NotImplementedError:
            ex_error.handle_not_implemented()


class ExShell(IrreversibleTextCommand):
    """Ex command(s): :shell

    Opens a shell at the current view's directory. Sublime Text keeps a virtual
    current directory that most of the time will be out of sync with the actual
    current directory. The virtual current directory is always set to the
    current view's directory, but it isn't accessible through the API.
    """
    def open_shell(self, command):
        return subprocess.Popen(command, cwd=os.getcwd())

    @changing_cd
    def run(self):
        if sublime.platform() == 'linux':
            term = self.view.settings().get('VintageousEx_linux_terminal')
            term = term or os.environ.get('COLORTERM') or os.environ.get("TERM")
            if not term:
                sublime.status_message("Vintageous: Not terminal name found.")
                return
            try:
                self.open_shell([term, '-e', 'bash']).wait()
            except Exception as e:
                print(e)
                sublime.status_message("Vintageous: Error while executing command through shell.")
                return
        elif sublime.platform() == 'osx':
            term = self.view.settings().get('VintageousEx_osx_terminal')
            term = term or os.environ.get('COLORTERM') or os.environ.get("TERM")
            if not term:
                sublime.status_message("Vintageous: Not terminal name found.")
                return
            try:
                self.open_shell([term, '-e', 'bash']).wait()
            except Exception as e:
                print(e)
                sublime.status_message("Vintageous: Error while executing command through shell.")
                return
        elif sublime.platform() == 'windows':
            self.open_shell(['cmd.exe', '/k']).wait()
        else:
            # XXX OSX (make check explicit)
            ex_error.handle_not_implemented()


class ExReadShellOut(sublime_plugin.TextCommand):
    @changing_cd
    def run(self, edit, line_range=None, name='', plusplus_args='', forced=False):
        target_line = self.view.line(self.view.sel()[0].begin())
        if line_range['text_range']:
            range = max(ex_range.calculate_range(self.view, line_range=line_range)[0])
            target_line = self.view.line(self.view.text_point(range, 0))
        target_point = min(target_line.b + 1, self.view.size())

        # Cheat a little bit to get the parsing right:
        #   - forced == True means we need to execute a command
        if forced:
            if sublime.platform() == 'linux':
                for s in self.view.sel():
                    # TODO: make shell command configurable.
                    the_shell = self.view.settings().get('linux_shell')
                    the_shell = the_shell or os.path.expandvars("$SHELL")
                    if not the_shell:
                        sublime.status_message("Vintageous: No shell name found.")
                        return
                    try:
                        p = subprocess.Popen([the_shell, '-c', name],
                                                            stdout=subprocess.PIPE)
                    except Exception as e:
                        print(e)
                        sublime.status_message("Vintageous: Error while executing command through shell.")
                        return
                    self.view.insert(edit, s.begin(), p.communicate()[0][:-1].decode('utf-8'))
            elif sublime.platform() == 'windows':
                for s in self.view.sel():
                    p = subprocess.Popen(['cmd.exe', '/C', name],
                                            stdout=subprocess.PIPE,
                                            startupinfo=get_startup_info()
                                            )
                    cp = 'cp' + get_oem_cp()
                    rv = p.communicate()[0].decode(cp)[:-2].strip()
                    self.view.insert(edit, s.begin(), rv)
            else:
                ex_error.handle_not_implemented()
        # Read a file into the current view.
        else:
            # According to Vim's help, :r should read the current file's content
            # if no file name is given, but Vim doesn't do that.
            # TODO: implement reading a file into the buffer.
            ex_error.handle_not_implemented()
            return


class ExPromptSelectOpenFile(sublime_plugin.TextCommand):
    """Ex command(s): :ls, :files

    Shows a quick panel listing the open files only. Provides concise
    information about the buffers's state: 'transient', 'unsaved'.
    """
    def run(self, edit):
        self.file_names = [gather_buffer_info(v)
                                        for v in self.view.window().views()]
        self.view.window().show_quick_panel(self.file_names, self.on_done)

    def on_done(self, idx):
        if idx == -1: return
        sought_fname = self.file_names[idx]
        for v in self.view.window().views():
            if v.file_name() and v.file_name().endswith(sought_fname[1]):
                self.view.window().focus_view(v)
            # XXX Base all checks on buffer id?
            elif sought_fname[1].isdigit() and \
                                        v.buffer_id() == int(sought_fname[1]):
                self.view.window().focus_view(v)


class ExMap(sublime_plugin.TextCommand):
    # do at least something moderately useful: open the user's .sublime-keymap
    # file
    def run(self, edit):
        if sublime.platform() == 'windows':
            platf = 'Windows'
        elif sublime.platform() == 'linux':
            platf = 'Linux'
        else:
            platf = 'OSX'
        self.view.window().run_command('open_file', {'file':
                                        '${packages}/User/Default (%s).sublime-keymap' % platf})


class ExAbbreviate(sublime_plugin.TextCommand):
    # for them moment, just open a completions file.
    def run(self, edit):
        abbs_file_name = 'Vintageous Abbreviations.sublime-completions'
        abbreviations = os.path.join(sublime.packages_path(),
                                     'User/' + abbs_file_name)
        if not os.path.exists(abbreviations):
            with open(abbreviations, 'w') as f:
                f.write('{\n\t"scope": "",\n\t"completions": [\n\t\n\t]\n}\n')

        self.view.window().run_command('open_file',
                                    {'file': "${packages}/User/%s" % abbs_file_name})


class ExPrintWorkingDir(IrreversibleTextCommand):
    @changing_cd
    def run(self):
        state = VintageState(self.view)
        sublime.status_message(os.getcwd())


class ExWriteFile(sublime_plugin.WindowCommand):
    @changing_cd
    def run(self,
            line_range=None,
            forced=False,
            file_name='',
            plusplus_args='',
            operator='',
            target_redirect='',
            subcmd=''):

        if file_name and target_redirect:
            sublime.status_message('Vintageous: Too many arguments.')
            return

        appending = operator == '>>'
        a_range = line_range['text_range']
        self.view = self.window.active_view()
        content = get_region_by_range(self.view, line_range=line_range) if a_range else \
                        [sublime.Region(0, self.view.size())]

        if target_redirect:
            target = self.window.new_file()
            target.set_name(target_redirect)
        elif file_name:

            def report_error(msg):
                sublime.status_message('Vintageous: %s' % msg)

            file_path = os.path.abspath(os.path.expanduser(file_name))

            if os.path.exists(file_path) and (file_path != self.view.file_name()):
                # TODO add w! flag
                # TODO: Hook this up with ex error handling (ex/errors.py).
                msg = "File '{0}' already exists.".format(file_path)
                report_error(msg)
                return

            if not os.path.exists(os.path.dirname(file_path)):
                msg = "Directory '{0}' does not exist.".format(os.path.dirname(file_path))
                report_error(msg)
                return

            try:
                # FIXME: We need to do some work with encodings here, don't we?
                with open(file_path, 'w+') as temp_file:
                    for frag in reversed(content):
                        temp_file.write(self.view.substr(frag))
                    temp_file.close()
                    sublime.status_message("Vintageous: Saved {0}".format(file_path))

                    row, col = self.view.rowcol(self.view.sel()[0].b)
                    encoded_fn = "{0}:{1}:{2}".format(file_path, row + 1, col + 1)
                    self.view.set_scratch(True)
                    w = self.window
                    w.run_command('close')
                    w.open_file(encoded_fn, sublime.ENCODED_POSITION)
                    return
            except IOError as e:
                report_error( "Failed to create file '%s'." % file_name )
                return

            window = self.window
            window.open_file(file_path)
            return
        else:
            target = self.view

        start = 0 if not appending else target.size()
        prefix = '\n' if appending and target.size() > 0 else ''

        if appending or target_redirect:
            for frag in reversed(content):
                target.run_command('append', {'characters': prefix + self.view.substr(frag) + '\n'})
        elif a_range:
            start_deleting = 0
            text = ''
            for frag in content:
                text += self.view.substr(frag) + '\n'
            start_deleting = len(text)
            self.view.run_command('ex_replace_file', {'start': 0, 'end': 0, 'with_what': text})
        else:
            dirname = os.path.dirname(self.view.file_name())
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            self.window.run_command('save')

        state = VintageState(self.window.active_view())
        state.enter_normal_mode()
        self.window.run_command('vi_enter_normal_mode')


class ExReplaceFile(sublime_plugin.TextCommand):
    def run(self, edit, start, end, with_what):
        self.view.replace(edit, sublime.Region(0, self.view.size()), with_what)


class ExWriteAll(sublime_plugin.WindowCommand):
    @changing_cd
    def run(self, forced=False):
        for v in self.window.views():
            v.run_command('save')


class ExNewFile(sublime_plugin.WindowCommand):
    @changing_cd
    def run(self, forced=False):
        self.window.run_command('new_file')


class ExFile(sublime_plugin.TextCommand):
    def run(self, edit, forced=False):
        # XXX figure out what the right params are. vim's help seems to be
        # wrong
        if self.view.file_name():
            fname = self.view.file_name()
        else:
            fname = 'untitled'

        attrs = ''
        if self.view.is_read_only():
            attrs = 'readonly'

        if self.view.is_dirty():
            attrs = 'modified'

        lines = 'no lines in the buffer'
        if self.view.rowcol(self.view.size())[0]:
            lines = self.view.rowcol(self.view.size())[0] + 1

        # fixme: doesn't calculate the buffer's % correctly
        if not isinstance(lines, str):
            vr = self.view.visible_region()
            start_row, end_row = self.view.rowcol(vr.begin())[0], \
                                              self.view.rowcol(vr.end())[0]
            mid = (start_row + end_row + 2) / 2
            percent = float(mid) / lines * 100.0

        msg = fname
        if attrs:
            msg += " [%s]" % attrs
        if isinstance(lines, str):
            msg += " -- %s --"  % lines
        else:
            msg += " %d line(s) --%d%%--" % (lines, int(percent))

        sublime.status_message('Vintageous: %s' % msg)


class ExMove(ExTextCommandBase, ExAddressableCommandMixin):
    def run_ex_command(self, edit, line_range=CURRENT_LINE_RANGE, forced=False, address=''):
        # make sure we have a default range
        if ('text_range' not in line_range) or not line_range['text_range']:
            line_range['text_range'] = '.'

        address = self.get_address(address)
        if address is None:
            ex_error.display_error(ex_error.ERR_INVALID_ADDRESS)
            return

        if address != 0:
            dest = self.view.line(self.view.text_point(address, 0)).end() + 1
        else:
            dest = 0

        # Don't move lines onto themselves.
        for sel in self.view.sel():
            if sel.contains(dest):
                ex_error.display_error(ex_error.ERR_CANT_MOVE_LINES_ONTO_THEMSELVES)
                return

        text = self.line_range_to_text(line_range)
        if dest > self.view.size():
            dest = self.view.size()
            text = '\n' + text[:-1]
        self.view.insert(edit, dest, text)

        for r in reversed(get_region_by_range(self.view, line_range)):
            self.view.erase(edit, self.view.full_line(r))

        new_address = address
        if address < self.view.rowcol(self.view.sel()[0].b)[0]:
            new_pt = self.view.text_point(new_address + 1, 0)
            new_address = self.view.rowcol(new_pt + len(text) - 1)[0]
        next_sel = self.view.text_point(new_address, 0)
        self.set_next_sel([(next_sel, next_sel)])


class ExCopy(ExTextCommandBase, ExAddressableCommandMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_ex_command(self, edit, line_range=CURRENT_LINE_RANGE,
                       forced=False, address=''):
        address = self.get_address(address)
        if address is None:
            ex_error.display_error(ex_error.ERR_INVALID_ADDRESS)
            return

        if address != 0:
            dest = self.view.line(self.view.text_point(address, 0)).end() + 1
        else:
            dest = address

        text = self.line_range_to_text(line_range)
        if dest > self.view.size():
            dest = self.view.size()
            text = '\n' + text[:-1]

        self.view.insert(edit, dest, text)

        cursor_dest = self.view.line(dest + len(text) - 1).begin()
        self.set_next_sel([(cursor_dest, cursor_dest)])


class ExOnly(sublime_plugin.TextCommand):
    """ Command: :only
    """
    def run(self, edit, forced=False):
        if not forced:
            if has_dirty_buffers(self.view.window()):
                ex_error.display_error(ex_error.ERR_OTHER_BUFFER_HAS_CHANGES)
                return

        w = self.view.window()
        current_id = self.view.id()
        for v in w.views():
            if v.id() != current_id:
                if forced and v.is_dirty():
                    v.set_scratch(True)
                w.focus_view(v)
                w.run_command('close')


class ExDoubleAmpersand(sublime_plugin.TextCommand):
    """ Command :&&
    """
    def run(self, edit, line_range=None, flags='', count=''):
        self.view.run_command('ex_substitute', {'line_range': line_range,
                                                'pattern': flags + count})


class ExSubstitute(sublime_plugin.TextCommand):
    most_recent_pat = None
    most_recent_flags = ''
    most_recent_replacement = ''

    def run(self, edit, line_range=None, pattern=''):

        # :s
        if not pattern:
            pattern = ExSubstitute.most_recent_pat
            replacement = ExSubstitute.most_recent_replacement
            flags = ''
            count = 0
        # :s g 100 | :s/ | :s// | s:/foo/bar/g 100 | etc.
        else:
            try:
                parts = parsers.s_cmd.split(pattern)
            except SyntaxError as e:
                sublime.status_message("Vintageous: (substitute) %s" % e)
                print("Vintageous: (substitute) %s" % e)
                return
            else:
                if len(parts) == 4:
                    # This is a full command in the form :s/foo/bar/g 100 or a
                    # partial version of it.
                    (pattern, replacement, flags, count) = parts
                else:
                    # This is a short command in the form :s g 100 or a partial
                    # version of it.
                    (flags, count) = parts
                    pattern = ExSubstitute.most_recent_pat
                    replacement = ExSubstitute.most_recent_replacement

        if not pattern:
            pattern = ExSubstitute.most_recent_pat
        else:
            ExSubstitute.most_recent_pat = pattern
            ExSubstitute.most_recent_replacement = replacement
            ExSubstitute.most_recent_flags = flags

        computed_flags = 0
        computed_flags |= re.IGNORECASE if (flags and 'i' in flags) else 0
        try:
            pattern = re.compile(pattern, flags=computed_flags)
        except Exception as e:
            sublime.status_message("Vintageous [regex error]: %s ... in pattern '%s'" % (e.message, pattern))
            print("Vintageous [regex error]: %s ... in pattern '%s'" % (e.message, pattern))
            return

        replace_count = 0 if (flags and 'g' in flags) else 1

        target_region = get_region_by_range(self.view, line_range=line_range, as_lines=True)
        for r in reversed(target_region):
            line_text = self.view.substr(self.view.line(r))
            rv = re.sub(pattern, replacement, line_text, count=replace_count)
            self.view.replace(edit, self.view.line(r), rv)


class ExDelete(ExTextCommandBase):
    def select(self, regions, register):
        self.view.sel().clear()
        to_store = []
        for r in regions:
            self.view.sel().add(r)
            if register:
                to_store.append(self.view.substr(self.view.full_line(r)))

        if register:
            text = ''.join(to_store)
            if not text.endswith('\n'):
                text = text + '\n'

            state = VintageState(self.view)
            state.registers[register] = [text]

    def run_ex_command(self, edit, line_range=None, register='', count=''):
        # XXX somewhat different to vim's behavior
        line_range = line_range if line_range else CURRENT_LINE_RANGE
        if line_range['text_range'] == '0':
            # FIXME: This seems to be a bug in the parser or get_region_by_range.
            # We should be settings 'left_ref', not 'left_offset'.
            line_range['left_offset'] = 1
            line_range['text_range'] = '1'
        rs = get_region_by_range(self.view, line_range=line_range)

        self.select(rs, register)

        self.view.run_command('split_selection_into_lines')
        self.view.run_command(
                    'run_macro_file',
                    {'file': 'Packages/Default/Delete Line.sublime-macro'})

        self.set_next_sel([(rs[0].a, rs[0].a)])


class ExGlobal(sublime_plugin.TextCommand):
    """Ex command(s): :global

    :global filters lines where a pattern matches and then applies the supplied
    action to all those lines.

    Examples:
        :10,20g/FOO/delete

        This command deletes all lines between line 10 and line 20 where 'FOO'
        matches.

        :g:XXX:s!old!NEW!g

        This command replaces all instances of 'old' with 'NEW' in every line
        where 'XXX' matches.

    By default, :global searches all lines in the buffer.

    If you want to filter lines where a pattern does NOT match, add an
    exclamation point:

        :g!/DON'T TOUCH THIS/delete
    """
    most_recent_pat = None
    def run(self, edit, line_range=None, forced=False, pattern=''):

        if not line_range['text_range']:
            line_range['text_range'] = '%'
            line_range['left_ref'] = '%'
        try:
            global_pattern, subcmd = parsers.g_cmd.split(pattern)
        except ValueError:
            msg = "Vintageous: Bad :global pattern. (%s)" % pattern
            sublime.status_message(msg)
            print(msg)
            return

        if global_pattern:
            ExGlobal.most_recent_pat = global_pattern
        else:
            global_pattern = ExGlobal.most_recent_pat

        # Make sure we always have a subcommand to exectute. This is what
        # Vim does too.
        subcmd = subcmd or 'print'

        rs = get_region_by_range(self.view, line_range=line_range, as_lines=True)

        for r in rs:
            try:
                match = re.search(global_pattern, self.view.substr(r))
            except Exception as e:
                msg = "Vintageous (global): %s ... in pattern '%s'" % (str(e), global_pattern)
                sublime.status_message(msg)
                print(msg)
                return
            if (match and not forced) or (not match and forced):
                GLOBAL_RANGES.append(r)

        # don't do anything if we didn't found any target ranges
        if not GLOBAL_RANGES:
            return
        self.view.window().run_command('vi_colon_input',
                              {'cmd_line': ':' +
                                    str(self.view.rowcol(r.a)[0] + 1) +
                                    subcmd})


class ExPrint(sublime_plugin.TextCommand):
    def run(self, edit, line_range=None, count='1', flags=''):
        if not count.isdigit():
            flags, count = count, ''
        rs = get_region_by_range(self.view, line_range=line_range)
        to_display = []
        for r in rs:
            for line in self.view.lines(r):
                text = self.view.substr(line)
                if '#' in flags:
                    row = self.view.rowcol(line.begin())[0] + 1
                else:
                    row = ''
                to_display.append((text, row))

        v = self.view.window().new_file()
        v.set_scratch(True)
        if 'l' in flags:
            v.settings().set('draw_white_space', 'all')
        for t, r in to_display:
            v.insert(edit, v.size(), (str(r) + ' ' + t + '\n').lstrip())


class ExQuitCommand(sublime_plugin.WindowCommand):
    """Ex command(s): :quit
    Closes the window.

        * Don't close the window if there are dirty buffers
          TODO:
          (Doesn't make too much sense if hot_exit is on, though.)
          Although ST's window command 'exit' would take care of this, it
          displays a modal dialog, so spare ourselves that.
    """
    def run(self, forced=False, count=1, flags=''):
        v = self.window.active_view()
        if forced:
            v.set_scratch(True)
        if v.is_dirty():
            sublime.status_message("There are unsaved changes!")
            return

        self.window.run_command('close')
        if len(self.window.views()) == 0:
            self.window.run_command('close')
            return

        # Close the current group if there aren't any views left in it.
        if not self.window.views_in_group(self.window.active_group()):
            self.window.run_command('ex_unvsplit')


class ExQuitAllCommand(sublime_plugin.WindowCommand):
    """Ex command(s): :qall
    Close all windows and then exit Sublime Text.

    If there are dirty buffers, exit only if :qall!.
    """
    def run(self, forced=False):
        if forced:
            for v in self.window.views():
                if v.is_dirty():
                    v.set_scratch(True)
        elif has_dirty_buffers(self.window):
            sublime.status_message("There are unsaved changes!")
            return

        self.window.run_command('close_all')
        self.window.run_command('exit')


class ExWriteAndQuitCommand(sublime_plugin.TextCommand):
    """Ex command(s): :wq

    Write and then close the active buffer.
    """
    def run(self, edit, line_range=None, forced=False):
        # TODO: implement this
        if forced:
            ex_error.handle_not_implemented()
            return
        if self.view.is_read_only():
            sublime.status_message("Can't write a read-only buffer.")
            return
        if not self.view.file_name():
            sublime.status_message("Can't save a file without name.")
            return

        self.view.run_command('save')
        self.view.window().run_command('ex_quit')


class ExBrowse(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().run_command('prompt_open_file')


class ExEdit(IrreversibleTextCommand):
    """Ex command(s): :e <file_name>

    Reverts unsaved changes to the buffer.

    If there's a <file_name>, open it for editing.
    """
    @changing_cd
    def run(self, forced=False, file_name=None):
        if file_name:
            file_name = os.path.expanduser(os.path.expandvars(file_name))
            if self.view.is_dirty() and not forced:
                ex_error.display_error(ex_error.ERR_UNSAVED_CHANGES)
                return
            file_name = os.path.expanduser(file_name)
            if os.path.isdir(file_name):
                sublime.status_message('Vintageous: "{0}" is a directory'.format(file_name))
                return
            message = ''
            if not os.path.exists(file_name):
                message = '[New File]'
                path = os.path.dirname(file_name)
                if path and not os.path.exists(path):
                    message = '[New DIRECTORY]'
                self.view.window().open_file(file_name)

                # TODO: Collect message and show at the end of the command.
                def show_message():
                    sublime.status_message('Vintageous: "{0}" {1}'.format((file_name, message)))
                sublime.set_timeout(show_message, 250)
                return
        else:
            if forced or not self.view.is_dirty():
                self.view.run_command('revert')
                return
            elif not file_name and self.view.is_dirty():
                ex_error.display_error(ex_error.ERR_UNSAVED_CHANGES)
                return

        if forced or not self.view.is_dirty():
            self.view.window().open_file(file_name)
            return
        ex_error.display_error(ex_error.ERR_UNSAVED_CHANGES)


class ExCquit(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().run_command('exit')


class ExExit(sublime_plugin.TextCommand):
    """Ex command(s): :x[it], :exi[t]

    Like :wq, but write only when changes have been made.

    TODO: Support ranges, like :w.
    """
    def run(self, edit, line_range=None):
        w = self.view.window()

        if w.active_view().is_dirty():
            w.run_command('save')

        w.run_command('close')

        if len(w.views()) == 0:
            w.run_command('exit')


class ExListRegisters(sublime_plugin.TextCommand):
    """Lists registers in quick panel and saves selected to `"` register.

       In Vintageous, registers store lists of values (due to multiple selections).
    """

    def run(self, edit):
        def show_lines(line_count):
            lines_display = '... [+{0}]'.format(line_count - 1)
            return lines_display if line_count > 1 else ''

        state = VintageState(self.view)
        pairs = [(k, v) for (k, v) in state.registers.to_dict().items() if v]
        pairs = [(k, repr(v[0]), len(v)) for (k, v) in pairs]
        pairs = ['"{0}\t{1}\t{2}'.format(k, v, show_lines(lines)) for (k, v, lines) in pairs]

        self.view.window().show_quick_panel(pairs, self.on_done, flags=sublime.MONOSPACE_FONT)

    def on_done(self, idx):
        """Save selected value to `"` register."""
        if idx == -1:
            return

        state = VintageState(self.view)
        value = list(state.registers.to_dict().values())[idx]
        state.registers['"'] = value


class ExNew(sublime_plugin.TextCommand):
    """Ex command(s): :new

    Create a new buffer.

    TODO: Create new buffer by splitting the screen.
    """
    @changing_cd
    def run(self, edit, line_range=None):
        self.view.window().run_command('new_file')


class ExYank(sublime_plugin.TextCommand):
    """Ex command(s): :y[ank]
    """

    def run(self, edit, line_range, register=None, count=None):
        if not register:
            register = '"'

        regs = get_region_by_range(self.view, line_range)
        text = '\n'.join([self.view.substr(line) for line in regs]) + '\n'

        state = VintageState(self.view)
        state.registers[register] = [text]
        if register == '"':
            state.registers['0'] = [text]



class TabControlCommand(sublime_plugin.WindowCommand):
    def run(self, command, file_name=None, forced=False):
        window = self.window
        selfview = window.active_view()
        max_index = len(window.views())
        (group, index) = window.get_view_index(selfview)
        if (command == "open"):
            if file_name is None:  # TODO: file completion
                window.run_command("show_overlay", {"overlay": "goto", "show_files": True, })
            else:
                cur_dir = os.path.dirname(selfview.file_name())
                window.open_file(os.path.join(cur_dir, file_name))
        elif command == "next":
            window.run_command("select_by_index", {"index": (index + 1) % max_index}, )
        elif command == "prev":
            window.run_command("select_by_index", {"index": (index + max_index - 1) % max_index, })
        elif command == "last":
            window.run_command("select_by_index", {"index": max_index - 1, })
        elif command == "first":
            window.run_command("select_by_index", {"index": 0, })
        elif command == "only":
            for view in window.views_in_group(group):
                if view.id() != selfview.id():
                    window.focus_view(view)
                    window.run_command("ex_quit", {"forced": forced})
            window.focus_view(selfview)
        else:
            sublime.status_message("Unknown TabControl Command")


class ExTabOpenCommand(sublime_plugin.WindowCommand):
    def run(self, file_name=None):
        self.window.run_command("tab_control", {"command": "open", "file_name": file_name}, )


class ExTabNextCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("tab_control", {"command": "next"}, )


class ExTabPrevCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("tab_control", {"command": "prev"}, )


class ExTabLastCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("tab_control", {"command": "last"}, )


class ExTabFirstCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("tab_control", {"command": "first"}, )


class ExTabOnlyCommand(sublime_plugin.WindowCommand):
    def run(self, forced=False):
        self.window.run_command("tab_control", {"command": "only", "forced": forced, }, )


class ExCdCommand(IrreversibleTextCommand):
    """Ex command(s): :cd [<path>|%:h]

    Print or change the current directory.

    :cd without an argument behaves as in Unix for all platforms.
    """
    @changing_cd
    def run(self, path=None, forced=False):
        if self.view.is_dirty() and not forced:
            ex_error.display_error(ex_error.ERR_UNSAVED_CHANGES)
            return

        state = VintageState(self.view)

        if not path:
            state.settings.vi['_cmdline_cd'] = os.path.expanduser("~")
            self.view.run_command('ex_print_working_dir')
            return

        # TODO: It seems there a few symbols that are always substituted when they represent a
        # filename. We should have a global method of substiting them.
        if path == '%:h':
            fname = self.view.file_name()
            if fname:
                state.settings.vi['_cmdline_cd'] = os.path.dirname(fname)
                self.view.run_command('ex_print_working_dir')
            return

        path = os.path.realpath(os.path.expandvars(os.path.expanduser(path)))
        if not os.path.exists(path):
            # TODO: Add error number in ex_error.py.
            ex_error.display_error(ex_error.ERR_CANT_FIND_DIR_IN_CDPATH)
            return

        state.settings.vi['_cmdline_cd'] = path
        self.view.run_command('ex_print_working_dir')


class ExCddCommand(IrreversibleTextCommand):
    """Ex command(s) [non-standard]: :cdd

    Non-standard command to change the current directory to the active
    view's path.:

    In Sublime Text, the current directory doesn't follow the active view, so
    it's convenient to be able to align both easily.

    (This command may be removed at any time.)
    """
    def run(self, forced=False):
        if self.view.is_dirty() and not forced:
            ex_error.display_error(ex_error.ERR_UNSAVED_CHANGES)
            return
        path = os.path.dirname(self.view.file_name())
        state = VintageState(self.view)
        try:
            state.settings.vi['_cmdline_cd'] = path
            self.view.run_command('ex_print_working_dir')
        except IOError:
            ex_error.display_error(ex_error.ERR_CANT_FIND_DIR_IN_CDPATH)


class ExVsplit(sublime_plugin.WindowCommand):
    MAX_SPLITS = 4
    LAYOUT_DATA = {
        1: {"cells": [[0,0, 1, 1]], "rows": [0.0, 1.0], "cols": [0.0, 1.0]},
        2: {"cells": [[0,0, 1, 1], [1, 0, 2, 1]], "rows": [0.0, 1.0], "cols": [0.0, 0.5, 1.0]},
        3: {"cells": [[0,0, 1, 1], [1, 0, 2, 1], [2, 0, 3, 1]], "rows": [0.0, 1.0], "cols": [0.0, 0.33, 0.66, 1.0]},
        4: {"cells": [[0,0, 1, 1], [1, 0, 2, 1], [2, 0, 3, 1], [3,0, 4, 1]], "rows": [0.0, 1.0], "cols": [0.0, 0.25, 0.50, 0.75, 1.0]},
    }
    def run(self, file_name=None):
        groups = self.window.num_groups()
        if groups >= ExVsplit.MAX_SPLITS:
            sublime.status_message("Vintageous: Can't create more groups.")
            return

        old_view = self.window.active_view()
        pos = ":{0}:{1}".format(*old_view.rowcol(old_view.sel()[0].b))
        current_file_name = old_view.file_name() + pos
        self.window.run_command('set_layout', ExVsplit.LAYOUT_DATA[groups + 1])

        # TODO: rename this param.
        if file_name:
            existing = self.window.find_open_file(file_name)
            pos = ''
            if existing:
                pos = ":{0}:{1}".format(*existing.rowcol(existing.sel()[0].b))
            self.open_file(file_name + pos)
            return

        # No file name provided; clone current view into new group.
        self.open_file(current_file_name)

    def open_file(self, file_name):
        flags = (sublime.FORCE_GROUP | sublime.ENCODED_POSITION)
        self.window.open_file(file_name, group=(self.window.num_groups() - 1),
                              flags=flags)


class ExUnvsplit(sublime_plugin.WindowCommand):
    def run(self):
        groups = self.window.num_groups()
        if groups == 1:
            sublime.status_message("Vintageous: Can't delete more groups.")
            return

        # If we don't do this, cloned views will be moved to the previous group and kept around.
        # We want to close them instead.
        self.window.run_command('close')
        self.window.run_command('set_layout', ExVsplit.LAYOUT_DATA[groups - 1])


class ExSetLocal(IrreversibleTextCommand):
    def run(self, option=None, operator=None, value=None):
        if option.endswith('?'):
            ex_error.handle_not_implemented()
            return
        try:
            set_local(self.view, option, value)
        except KeyError:
            sublime.status_message("Vintageuos: No such option.")
        except ValueError:
            sublime.status_message("Vintageous: Invalid value for option.")


class ExSet(IrreversibleTextCommand):
    def run(self, option=None, operator=None, value=None):
        if option.endswith('?'):
            ex_error.handle_not_implemented()
            return
        try:
            set_global(self.view, option, value)
        except KeyError:
            sublime.status_message("Vintageuos: No such option.")
        except ValueError:
            sublime.status_message("Vintageous: Invalid value for option.")
