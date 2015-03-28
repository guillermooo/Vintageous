import sublime
import sublime_plugin

import os
import re
import stat
import subprocess

from Vintageous.ex import ex_error
from Vintageous.ex import ex_range
from Vintageous.ex import parsers
from Vintageous.ex import shell
from Vintageous.ex.ex_error import display_error2
from Vintageous.ex.ex_error import display_message
from Vintageous.ex.ex_error import DISPLAY_STATUS
from Vintageous.ex.ex_error import DISPLAY_ALL
from Vintageous.ex.ex_error import ERR_CANT_WRITE_FILE
from Vintageous.ex.ex_error import ERR_FILE_EXISTS
from Vintageous.ex.ex_error import ERR_NO_FILE_NAME
from Vintageous.ex.ex_error import ERR_OTHER_BUFFER_HAS_CHANGES
from Vintageous.ex.ex_error import ERR_READONLY_FILE
from Vintageous.ex.ex_error import handle_not_implemented
from Vintageous.ex.ex_error import VimError
from Vintageous.ex.parsers.new.parser import parse_ex_command
from Vintageous.ex.plat.windows import get_oem_cp
from Vintageous.ex.plat.windows import get_startup_info
from Vintageous.state import State
from Vintageous.vi import abbrev
from Vintageous.vi import utils
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.core import ViWindowCommandBase
from Vintageous.vi.mappings import Mappings
from Vintageous.vi.settings import set_global
from Vintageous.vi.settings import set_local
from Vintageous.vi.sublime import has_dirty_buffers
from Vintageous.vi.utils import first_sel
from Vintageous.vi.utils import IrreversibleTextCommand
from Vintageous.vi.utils import modes
from Vintageous.vi.utils import R
from Vintageous.vi.utils import resolve_insertion_point_at_b
from Vintageous.vi.utils import row_at


GLOBAL_RANGES = []
CURRENT_LINE_RANGE = {'left_ref': '.', 'left_offset': 0,
                      'left_search_offsets': [], 'right_ref': None,
                      'right_offset': 0, 'right_search_offsets': []}


def changing_cd(f, *args, **kwargs):
    def inner(*args, **kwargs):
        try:
            state = State(args[0].view)
        except AttributeError:
            state = State(args[0].window.active_view())

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


def get_view_info(v):
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
        state = State(self.view)
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


class ExGoto(ViWindowCommandBase):
    def run(self, command_line):
        if not command_line:
            # No-op: user issues ':'.
            return

        parsed = parse_ex_command(command_line)

        r = parsed.line_range.resolve(self._view)
        line_nr = row_at(self._view, r.a) + 1

        # TODO: .enter_normal_mode has access to self.state.mode
        self.enter_normal_mode(mode=self.state.mode)
        self.state.enter_normal_mode()

        self.window.run_command('_vi_add_to_jump_list')
        self.window.run_command('_vi_go_to_line', {'line': line_nr, 'mode': self.state.mode})
        self.window.run_command('_vi_add_to_jump_list')
        self._view.show(self._view.sel()[0])


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


class ExPromptSelectOpenFile(ViWindowCommandBase):
    '''
    Command: :ls[!]
             :buffers[!]
             :files[!]

    http://vimdoc.sourceforge.net/htmldoc/windows.html#:ls
    '''

    def run(self):
        self.file_names = [get_view_info(view) for view in self.window.views()]
        self.view_ids = [view.id() for view in self.window.views()]
        self.window.show_quick_panel(self.file_names, self.on_done)

    def on_done(self, index):
        if index == -1:
            return

        sought_id = self.view_ids[index]
        for view in self.window.views():
            # TODO: Start looking in current group.
            if view.id() == sought_id:
                self.window.focus_view(view)


class ExMap(sublime_plugin.TextCommand):
    """
    Remaps keys.
    """
    def run(self, edit, mode=None, count=None, cmd=''):
        try:
            # TODO(guillermooo): Instead of parsing this here, add parsers
            # to ex command defs and reuse them here.
            keys, command = cmd.lstrip().split(' ', 1)
        except ValueError:
            sublime.status_message('Vintageous: Bad mapping format')
            return
        else:
            mappings = Mappings(State(self.view))
            mappings.add(modes.NORMAL, keys, command)
            mappings.add(modes.OPERATOR_PENDING, keys, command)
            mappings.add(modes.VISUAL, keys, command)


class ExUnmap(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=None, cmd=''):
        mappings = Mappings(State(self.view))
        try:
            mappings.remove(modes.NORMAL, cmd)
            mappings.remove(modes.OPERATOR_PENDING, cmd)
            mappings.remove(modes.VISUAL, cmd)
        except KeyError:
            sublime.status_message('Vintageous: Mapping not found.')


class ExNmap(sublime_plugin.TextCommand):
    """
    Remaps keys.
    """
    def run(self, edit, mode=None, count=None, cmd=''):
        keys, command = cmd.lstrip().split(' ', 1)
        mappings = Mappings(State(self.view))
        mappings.add(modes.NORMAL, keys, command)


class ExNunmap(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=None, cmd=''):
        mappings = Mappings(State(self.view))
        try:
            mappings.remove(modes.NORMAL, cmd)
        except KeyError:
            sublime.status_message('Vintageous: Mapping not found.')


class ExOmap(sublime_plugin.TextCommand):
    """
    Remaps keys.
    """
    def run(self, edit, mode=None, count=None, cmd=''):
        keys, command = cmd.lstrip().split(' ', 1)
        mappings = Mappings(State(self.view))
        mappings.add(modes.OPERATOR_PENDING, keys, command)


class ExOunmap(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=None, cmd=''):
        mappings = Mappings(State(self.view))
        try:
            mappings.remove(modes.OPERATOR_PENDING, cmd)
        except KeyError:
            sublime.status_message('Vintageous: Mapping not found.')


class ExVmap(sublime_plugin.TextCommand):
    """
    Remaps keys.
    """
    def run(self, edit, mode=None, count=None, cmd=''):
        keys, command = cmd.lstrip().split(' ', 1)
        mappings = Mappings(State(self.view))
        mappings.add(modes.VISUAL, keys, command)
        mappings.add(modes.VISUAL_LINE, keys, command)
        mappings.add(modes.VISUAL_BLOCK, keys, command)


class ExVunmap(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=None, cmd=''):
        mappings = Mappings(State(self.view))
        try:
            mappings.remove(modes.VISUAL, cmd)
            mappings.remove(modes.VISUAL_LINE, cmd)
            mappings.remove(modes.VISUAL_BLOCK, cmd)
        except KeyError:
            sublime.status_message('Vintageous: Mapping  not found.')


class ExAbbreviate(ViWindowCommandBase):
    '''
    Command: :ab[breviate]

    http://vimdoc.sourceforge.net/htmldoc/map.html#:abbreviate
    '''

    def run(self, command_line=''):
        if not command_line:
            self.show_abbreviations()
            return

        parsed = parse_ex_command(command_line)

        if not (parsed.command.short and parsed.command.full):
            handle_not_implemented(':abbreviate not fully implemented')
            return

        abbrev.Store().set(parsed.command.short, parsed.command.full)

    def show_abbreviations(self):
        abbrevs = ['{0} --> {1}'.format(item['trigger'], item['contents'])
                                                    for item in
                                                    abbrev.Store().get_all()]

        self.window.show_quick_panel(abbrevs,
                                     None, # Simply show the list.
                                     flags=sublime.MONOSPACE_FONT)


class ExUnabbreviate(sublime_plugin.TextCommand):
    def run(self, edit, short):
        if not short:
            return

        abbrev.Store().erase(short)


class ExPrintWorkingDir(IrreversibleTextCommand):
    @changing_cd
    def run(self):
        state = State(self.view)
        sublime.status_message(os.getcwd())


class ExWriteFile(ViWindowCommandBase):
    '''
    Command :w[rite] [++opt]
            :w[rite]! [++opt]
            :[range]w[rite][!] [++opt]
            :[range]w[rite] [++opt] {file}
            :[range]w[rite]! [++opt] {file}
            :[range]w[rite][!] [++opt] >>
            :[range]w[rite][!] [++opt] >> {file}
            :[range]w[rite] [++opt] {!cmd}

    http://vimdoc.sourceforge.net/htmldoc/editing.html#:write
    '''

    def check_is_readonly(self, fname):
        if not fname:
            return

        try:
            mode = os.stat(fname)
            read_only = (stat.S_IMODE(mode.st_mode) & stat.S_IWUSR != stat.S_IWUSR)
        except FileNotFoundError:
            return

        return read_only

    @changing_cd
    def run(self, command_line=''):
        if not command_line:
            raise ValueError('empty command line; that seems to be an error')

        parsed = parse_ex_command(command_line)

        if parsed.command.options:
            handle_not_implemented("++opt isn't implemented for :write")
            return

        if not self._view:
            return

        if parsed.command.appends:
            self.do_append(parsed)
            return

        if parsed.command.command:
            handle_not_implemented("!cmd isn't implemented for :write")
            return

        if parsed.command.target_file:
            self.do_write(parsed)
            return

        if not self._view.file_name():
            display_error2(VimError(ERR_NO_FILE_NAME))
            return

        read_only = (self.check_is_readonly(self._view.file_name())
                     or self._view.is_read_only())

        if read_only and not parsed.command.forced:
            utils.blink()
            display_error2(VimError(ERR_READONLY_FILE))
            return

        self.window.run_command('save')

    def do_append(self, parsed_command):
        if parsed_command.command.target_file:
            self.do_append_to_file(parsed_command)
            return

        r = None
        if parsed_command.line_range.is_empty:
            # If the user didn't provide any range data, Vim appends whe whole buffer.
            r = R(0, self._view.size())
        else:
            r = parsed_command.line_range.resolve(self._view)

        text = self._view.substr(r)
        text = text if text.startswith('\n') else '\n' + text

        location = resolve_insertion_point_at_b(first_sel(self._view))

        self._view.run_command('append', {'characters': text})

        utils.replace_sel(self._view, R(self._view.line(location).a))

        self.enter_normal_mode(mode=self.state.mode)
        self.state.enter_normal_mode()

    def do_append_to_file(self, parsed_command):
        r = None
        if parsed_command.line_range.is_empty:
            # If the user didn't provide any range data, Vim writes whe whole buffer.
            r = R(0, self._view.size())
        else:
            r = parsed_command.line_range.resolve(self._view)

        fname = parsed_command.command.target_file

        if not parsed_command.command.forced and not os.path.exists(fname):
            display_error2(VimError(ERR_CANT_WRITE_FILE))
            return

        try:
            with open(fname, 'at') as f:
                text = self._view.substr(r)
                f.write(text)
            # TODO: make this `show_info` instead.
            display_message('Appended to ' + os.path.abspath(fname),
                    devices=DISPLAY_STATUS)
            return
        except IOError as e:
            print('Vintageous: could not write file')
            print('Vintageous ============')
            print(e)
            print('=======================')
            return

    def do_write(self, parsed_command):
        fname = parsed_command.command.target_file

        if not parsed_command.command.forced:
            if os.path.exists(fname):
                utils.blink()
                display_error2(VimError(ERR_FILE_EXISTS))
                return

            if self.check_is_readonly(fname):
                utils.blink()
                display_error2(VimError(ERR_READONLY_FILE))
                return

        r = None
        if parsed_command.line_range.is_empty:
            # If the user didn't provide any range data, Vim writes whe whole buffer.
            r = R(0, self._view.size())
        else:
            r = parsed_command.line_range.resolve(self._view)

        assert r is not None, "range cannot be None"

        try:
            # FIXME: we should write in the current dir, but I don't think we're doing that.
            with open(fname, 'wt') as f:
                text = self._view.substr(r)
                f.write(text)
            display_message('Saved ' + os.path.abspath(fname),
                    devices=DISPLAY_STATUS)
        except IOError as e:
            # TODO: Add logging.
            display_error2(VimError(ERR_CANT_WRITE_FILE))
            print('Vintageous =======')
            print (e)
            print('==================')


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
    '''
    Command: :[range]co[py] {address}

    http://vimdoc.sourceforge.net/htmldoc/change.html#:copy
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_ex_command(self, edit, command_line=''):
        assert command_line, 'expected non-empty command line'

        parsed = parse_ex_command(command_line)

        unresolved = parsed.command.calculate_address()

        if unresolved is None:
            display_error2(VimError(ex_error.ERR_INVALID_ADDRESS))
            return

        # TODO: how do we signal row 0?
        target_region = unresolved.resolve(self.view)

        address = None
        if target_region == R(-1, -1):
            address = 0
        else:
            row = utils.row_at(self.view, target_region.begin()) + 1
            address = self.view.text_point(row, 0)

        source = parsed.line_range.resolve(self.view)
        text = self.view.substr(source)

        if address >= self.view.size():
            address = self.view.size()
            text = '\n' + text[:-1]

        self.view.insert(edit, address, text)

        cursor_dest = self.view.line(address + len(text) - 1).begin()
        self.set_next_sel([(cursor_dest, cursor_dest)])


class ExOnly(ViWindowCommandBase):
    """
    Command: :on[ly][!]

    http://vimdoc.sourceforge.net/htmldoc/windows.html#:only
    """

    def run(self, command_line=''):

        if not command_line:
            raise ValueError('empty command line; that seems wrong')

        parsed = parse_ex_command(command_line)

        if not parsed.command.forced and has_dirty_buffers(self.window):
                display_error2(VimError(ERR_OTHER_BUFFER_HAS_CHANGES))
                return

        current_id = self._view.id()

        for view in self.window.views():
            if view.id() == current_id:
                continue

            if view.is_dirty():
                view.set_scratch(True)

            view.close()


class ExDoubleAmpersand(ViWindowCommandBase):
    '''
    Command: :[range]&[&][flags] [count]

    http://vimdoc.sourceforge.net/htmldoc/change.html#:&
    '''

    def run(self, command_line=''):
        assert command_line, 'expected non-empty command line'

        parsed = parse_ex_command(command_line)

        new_command_line = '{0}substitute///{1} {2}'.format(
                str(parsed.line_range),
                ''.join(parsed.command.params['flags']),
                parsed.command.params['count'],
                )

        self.window.run_command('ex_substitute', {
            'command_line': new_command_line.strip()
            })


class ExSubstitute(sublime_plugin.TextCommand):
    '''
    Command :s[ubstitute]

    http://vimdoc.sourceforge.net/htmldoc/change.html#:substitute
    '''

    last_pattern = None
    last_flags = []
    last_replacement = ''

    def run(self, edit, command_line=''):

        if not command_line:
            raise ValueError('no command line passed; that seems wrong')

        # ST commands only accept Json-encoded parameters.
        # We parse the command line again because the alternative is to
        # serialize the parsed command line before calling this command.
        # Parsing twice seems simpler.
        parsed = parse_ex_command(command_line)
        pattern = parsed.command.pattern
        replacement = parsed.command.replacement
        count = parsed.command.count
        flags = parsed.command.flags

        # :s
        if not pattern:
            pattern = ExSubstitute.last_pattern
            replacement = ExSubstitute.last_replacement
            # TODO: Don't we have to reuse the previous flags?
            flags = []
            count = 0

        if not pattern:
            sublime.status_message("Vintageous: no previous pattern available")
            print("Vintageous: no previous pattern available")
            return

        ExSubstitute.last_pattern = pattern
        ExSubstitute.last_replacement = replacement
        ExSubstitute.last_flags = flags

        computed_flags = 0
        computed_flags |= re.IGNORECASE if ('i' in flags) else 0

        try:
            compiled_rx = re.compile(pattern, flags=computed_flags)
        except Exception as e:
            sublime.status_message(
                "Vintageous: bad pattern '%s'" % (e.message, pattern))
            print("Vintageous [regex error]: %s ... in pattern '%s'"
                % (e.message, pattern))
            return

        # TODO: Implement 'count'
        replace_count = 0 if (flags and 'g' in flags) else 1

        target_region = parsed.line_range.resolve(self.view)
        line_text = self.view.substr(target_region)
        new_text = re.sub(compiled_rx, replacement, line_text, count=replace_count)
        self.view.replace(edit, target_region, new_text)


class ExDelete(ExTextCommandBase):
    '''
    Command: :[range]d[elete] [x]
             :[range]d[elete] [x] {count}

    http://vimdoc.sourceforge.net/htmldoc/change.html#:delete
    '''

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

            state = State(self.view)
            state.registers[register] = [text]

    def run_ex_command(self, edit, command_line=''):
        assert command_line, 'expected non-empty command line'

        parsed = parse_ex_command(command_line)

        r = parsed.line_range.resolve(self.view)

        if r == R(-1, -1):
            r = self.view.full_line(0)

        self.select([r], parsed.command.params['register'])

        self.view.erase(edit, r)

        self.set_next_sel([(r.a, r.a)])


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


class ExBrowse(ViWindowCommandBase):
    '''
    :bro[wse] {command}

    http://vimdoc.sourceforge.net/htmldoc/editing.html#:browse
    '''

    def run(self, command_line):
        assert command_line, 'expected a non-empty command line'

        self.window.run_command('prompt_open_file')


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

            if not os.path.isabs(file_name):
                file_name = os.path.join(
                                State(self.view).settings.vi['_cmdline_cd'],
                                file_name)

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


class ExCquit(ViWindowCommandBase):
    '''
    Command: :cq[uit][!]

    http://vimdoc.sourceforge.net/htmldoc/quickfix.html#:cquit
    '''
    def run(self, command_line=''):
        assert command_line, 'expected non-empty command_line'

        self.window.run_command('exit')


class ExExit(sublime_plugin.TextCommand):
    """Ex command(s): :x[it], :exi[t]

    Like :wq, but write only when changes have been made.

    TODO: Support ranges, like :w.
    """
    def run(self, edit, line_range=None, mode=None, count=1):
        w = self.view.window()

        if w.active_view().is_dirty():
            w.run_command('save')

        w.run_command('close')

        if len(w.views()) == 0:
            w.run_command('exit')


class ExListRegisters(ViWindowCommandBase):
    '''
    Command :reg[isters] {arg}

    Lists registers in quick panel and saves selected to `"` register.

    In Vintageous, registers store lists of values (due to multiple selections).

    http://vimdoc.sourceforge.net/htmldoc/change.html#:registers
    '''

    def run(self, command_line):
        def show_lines(line_count):
            lines_display = '... [+{0}]'.format(line_count - 1)
            return lines_display if line_count > 1 else ''

        parsed = parse_ex_command(command_line)

        # TODO: implement arguments.

        pairs = [(k, v) for (k, v) in self.state.registers.to_dict().items() if v]
        pairs = [(k, repr(v[0]), len(v)) for (k, v) in pairs]
        pairs = ['"{0}  {1}  {2}'.format(k, v, show_lines(lines)) for (k, v, lines) in pairs]

        self.window.show_quick_panel(pairs, self.on_done, flags=sublime.MONOSPACE_FONT)

    def on_done(self, idx):
        """Save selected value to `"` register."""
        if idx == -1:
            return

        value = list(self.state.registers.to_dict().values())[idx]
        self.state.registers['"'] = [value]


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

        state = State(self.view)
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


class ExCdCommand(ViWindowCommandBase):
    '''
    Command: :cd[!]
             :cd[!] {path}
             :cd[!] -

    Print or change the current directory.

    :cd without an argument behaves as in Unix for all platforms.

    http://vimdoc.sourceforge.net/htmldoc/editing.html#:cd
    '''

    @changing_cd
    def run(self, command_line=''):
        assert command_line, 'expected non-empty command line'

        parsed = parse_ex_command(command_line)

        if self._view.is_dirty() and not parsed.command.forced:
            display_error2(ex_error.ERR_UNSAVED_CHANGES)
            return

        if not parsed.command.path:
            self.state.settings.vi['_cmdline_cd'] = os.path.expanduser("~")
            self._view.run_command('ex_print_working_dir')
            return

        # TODO: It seems there a few symbols that are always substituted when they represent a
        # filename. We should have a global method of substiting them.
        if parsed.command.path == '%:h':
            fname = self._view.file_name()
            if fname:
                self.state.settings.vi['_cmdline_cd'] = os.path.dirname(fname)
                self._view.run_command('ex_print_working_dir')
            return

        path = os.path.realpath(os.path.expandvars(os.path.expanduser(parsed.command.path)))
        if not os.path.exists(path):
            # TODO: Add error number in ex_error.py.
            display_error2(VimError(ex_error.ERR_CANT_FIND_DIR_IN_CDPATH))
            return

        self.state.settings.vi['_cmdline_cd'] = path
        self._view.run_command('ex_print_working_dir')


class ExCddCommand(ViWindowCommandBase):
    """
    Command (non-standard): :cdd[!]

    Non-standard command to change the current directory to the active
    view's directory.

    In Sublime Text, the current directory doesn't follow the active view, so
    it's convenient to be able to align both easily.

    XXX: Is the above still true?

    (This command may be removed at any time.)
    """
    def run(self, command_line=''):
        assert command_line, 'expected non-empty command line'

        parsed = parse_ex_command(command_line)

        if self._view.is_dirty() and not parsed.command.forced:
            display_error2(VimError(ex_error.ERR_UNSAVED_CHANGES))
            return

        path = os.path.dirname(self._view.file_name())

        try:
            self.state.settings.vi['_cmdline_cd'] = path
            self._view.run_command('ex_print_working_dir')
        except IOError:
            ex_error.display_error(ex_error.ERR_CANT_FIND_DIR_IN_CDPATH)


class ExVsplit(ViWindowCommandBase):
    '''
    Command: :[N]vs[plit] [++opt] [+cmd] [file]

    http://vimdoc.sourceforge.net/htmldoc/windows.html#:vsplit
    '''

    MAX_SPLITS = 4
    LAYOUT_DATA = {
        1: {"cells": [[0,0, 1, 1]], "rows": [0.0, 1.0], "cols": [0.0, 1.0]},
        2: {"cells": [[0,0, 1, 1], [1, 0, 2, 1]], "rows": [0.0, 1.0], "cols": [0.0, 0.5, 1.0]},
        3: {"cells": [[0,0, 1, 1], [1, 0, 2, 1], [2, 0, 3, 1]], "rows": [0.0, 1.0], "cols": [0.0, 0.33, 0.66, 1.0]},
        4: {"cells": [[0,0, 1, 1], [1, 0, 2, 1], [2, 0, 3, 1], [3,0, 4, 1]], "rows": [0.0, 1.0], "cols": [0.0, 0.25, 0.50, 0.75, 1.0]},
    }

    def run(self, command_line=''):
        parsed = parse_ex_command(command_line)

        file_name = parsed.command.params['file_name']

        groups = self.window.num_groups()
        if groups >= ExVsplit.MAX_SPLITS:
            display_message("Can't create more groups.", devices=DISPLAY_ALL)
            return

        old_view = self._view
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


class ExLet(IrreversibleTextCommand):
    def run(self, name=None, operator='=', value=None):
        state = State(self.view)
        state.variables.set(name, value)
