import sublime
import sublime_plugin

from Vintageous.state import VintageState
from Vintageous.state import IrreversibleTextCommand
from Vintageous.vi import utils
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import regions_transformer


class ViEditAtEol(sublime_plugin.TextCommand):
    def run(self, edit, extend=False):
        state = VintageState(self.view)
        state.enter_insert_mode()

        self.view.run_command('collapse_to_direction')

        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            hard_eol = self.view.line(s.b).end()
            new_sels.append(sublime.Region(hard_eol, hard_eol))

        for s in new_sels:
            self.view.sel().add(s)


class ViEditAfterCaret(sublime_plugin.TextCommand):
    def run(self, edit, extend=False):
        state = VintageState(self.view)
        state.enter_insert_mode()

        visual = self.view.has_non_empty_selection_region()

        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if visual:
                new_sels.append(sublime.Region(s.end(), s.end()))
            else:
                if not utils.is_at_eol(self.view, s):
                    new_sels.append(sublime.Region(s.end() + 1, s.end() + 1))
                else:
                    new_sels.append(sublime.Region(s.end(), s.end()))

        for s in new_sels:
            self.view.sel().add(s)


class _vi_big_i(sublime_plugin.TextCommand):
    def run(self, edit, extend=False):
        def f(view, s):
            line = view.line(s.b)
            pt = utils.next_non_white_space_char(view, line.a)
            return sublime.Region(pt, pt)

        state = VintageState(self.view)
        state.enter_insert_mode()

        regions_transformer(self.view, f)

class ViPaste(sublime_plugin.TextCommand):
    def run(self, edit, register=None, count=1):
        state = VintageState(self.view)

        if register:
            fragments = state.registers[register]
        else:
            # TODO: There should be a simpler way of getting the unnamed register's content.
            fragments = state.registers['"']

        sels = list(self.view.sel())

        if len(sels) == len(fragments):
            sel_frag = zip(sels, fragments)
        else:
            sel_frag = zip(sels, [fragments[0],] * len(sels)) 

        offset = 0
        for s, text in sel_frag:
            text = self.prepare_fragment(text)
            if text.startswith('\n'):
                if utils.is_at_eol(self.view, s) or utils.is_at_bol(self.view, s):
                    self.paste_all(edit, self.view.line(s.b).b, text, count)
                else:
                    self.paste_all(edit, self.view.line(s.b - 1).b, text, count)
            else:
                self.paste_all(edit, s.b + offset + 1, text, count)
                offset += len(text) * count

    def prepare_fragment(self, text):
        if text.endswith('\n') and text != '\n':
            text = '\n' + text[0:-1]
        return text

    def paste_all(self, edit, at, text, count):
        for x in range(count):
            self.view.insert(edit, at, text)


class ViPasteBefore(sublime_plugin.TextCommand):
    def run(self, edit, register=None, count=1):
        state = VintageState(self.view)

        if register:
            fragments = state.registers[register]
        else:
            # TODO: There should be a simpler way of getting the unnamed register's content.
            fragments = state.registers['"']

        sels = list(self.view.sel())

        if len(sels) == len(fragments):
            sel_frag = zip(sels, fragments)
        else:
            sel_frag = zip(sels, [fragments[0],] * len(sels)) 

        offset = 0
        for s, text in sel_frag:
            if text.endswith('\n'):
                if utils.is_at_eol(self.view, s) or utils.is_at_bol(self.view, s):
                    self.paste_all(edit, self.view.line(s.b).a, text, count)
                else:
                    self.paste_all(edit, self.view.line(s.b - 1).a, text, count)
            else:
                self.paste_all(edit, s.b + offset, text, count)
                offset += len(text) * count

    def paste_all(self, edit, at, text, count):
        for x in range(count):
            self.view.insert(edit, at, text)


class ViEnterNormalMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        self.view.run_command('collapse_to_direction')
        self.view.run_command('dont_stay_on_eol_backward')
        state.reset()
        state.enter_normal_mode()


class ViEnterNormalModeFromInsertMode(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if s.a <= s.b:
                if (self.view.line(s.a).a != s.a):
                    new_sels.append(sublime.Region(s.a - 1, s.a - 1))
                else:
                    new_sels.append(sublime.Region(s.a, s.a))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)

        state = VintageState(self.view)
        state.enter_normal_mode()


class ViEnterInsertMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        state.enter_insert_mode()
        self.view.run_command('collapse_to_direction')


class ViEnterVisualMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        state.enter_visual_mode()
        self.view.run_command('extend_to_minimal_width')


class ViEnterVisualLineMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        state.enter_visual_line_mode()


class SetAction(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, action):
        state = VintageState(self.view)
        state.action = action
        state.run()


class SetMotion(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, motion):
        state = VintageState(self.view)
        state.motion = motion
        state.run()


class SetComposite(sublime_plugin.TextCommand):
    def run(self, edit, motion, action):
        state = VintageState(self.view)
        state.motion = motion
        state.action = action
        state.run()


class ViPushDigit(sublime_plugin.TextCommand):
    def run(self, edit, digit):
        state = VintageState(self.view)
        if not (state.action or state.motion):
            state.push_motion_digit(digit)
        elif state.action:
            state.push_action_digit(digit)


class ViReverseCaret(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            new_sels.append(sublime.Region(s.b, s.a))

        for s in new_sels:
            self.view.sel().add(s)


class ViEnterNormalInsertMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        state.enter_normal_insert_mode()

        self.view.run_command('toggle_record_macro')
        # ...User types text...


class ViRunNormalInsertModeActions(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        # We've recorded what the user has typed into the buffer. Turn macro recording off.
        self.view.run_command('toggle_record_macro')

        for i in range(state.count - 1):
            self.view.run_command('run_macro')

        # Ensure the count will be deleted.
        state.mode = MODE_NORMAL
        # Delete the count now.
        state.reset()

        self.view.run_command('vi_enter_normal_mode_from_insert_mode')


class SetRegister(sublime_plugin.TextCommand):
    def run(self, edit, character=None):
        state = VintageState(self.view)
        if character is None:
            state.expecting_register = True
        else:
            state.register = character
            state.expecting_register = False


class ViF(sublime_plugin.TextCommand):
    def run(self, edit, character=None):
        state = VintageState(self.view)
        if character is None:
            state.motion = 'vi_f'
            state.expecting_user_input = True
        else:
            state.user_input = character
            state.expecting_user_input= False
            state.run()


class ViT(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, character=None):
        state = VintageState(self.view)
        if character is None:
            state.motion = 'vi_t'
            # XXX: Maybe we should simply use ["t", "<character>"] in the key map and be done
            # with this.
            state.expecting_user_input = True
        else:
            state.user_input = character
            state.expecting_user_input= False
            state.run()


class ViBigT(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    # XXX: Delete argument when it isn't needed any more.
    def run(self, character=None):
        state = VintageState(self.view)
        if character is None:
            state.motion = 'vi_big_t'
            # XXX: Maybe we should simply use ["t", "<character>"] in the key map and be done
            # with this.
            state.expecting_user_input = True
        else:
            state.user_input = character
            state.expecting_user_input= False
            state.run()


class ViBigF(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    # XXX: Delete argument when it isn't needed any more.
    def run(self):
        state = VintageState(self.view)
        state.motion = 'vi_big_f'
        state.expecting_user_input = True

class ViI(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self):
        state = VintageState(self.view)
        state.motion = 'vi_i'
        state.expecting_user_input = True


class CollectUserInput(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, character=None):
        state = VintageState(self.view)
        state.user_input = character
        state.expecting_user_input= False
        state.run()


class _repeat_command(IrreversibleTextCommand):
    """Repeats a Sublime Text command.
    """
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, command=None, command_args={}, times=0):
        if command == None:
            return

        for i in range(times):
            self.view.run_command(command, command_args)


class _vi_z_enter(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self):
        first_sel = self.view.sel()[0]
        current_row = self.view.rowcol(first_sel.b)[0] - 1

        topmost_visible_row, _ = self.view.rowcol(self.view.visible_region().a)

        self.view.run_command('scroll_lines', {'amount': (topmost_visible_row - current_row)})
        
class _vi_z_minus(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self):
        first_sel = self.view.sel()[0]
        current_row = self.view.rowcol(first_sel.b)[0]

        bottommost_visible_row, _ = self.view.rowcol(self.view.visible_region().b)

        self.view.run_command('scroll_lines', {'amount': (bottommost_visible_row - current_row)})


class _vi_zz(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self):
        first_sel = self.view.sel()[0]
        current_row = self.view.rowcol(first_sel.b)[0]

        topmost_visible_row, _ = self.view.rowcol(self.view.visible_region().a)
        bottommost_visible_row, _ = self.view.rowcol(self.view.visible_region().b)

        middle_row = (topmost_visible_row + bottommost_visible_row) / 2

        self.view.run_command('scroll_lines', {'amount': (middle_row - current_row)})
               