"""Sublime Text commands performing vim actions.

   If you are implementing a new action command, stick it here.

   Action parsers belong instead in Vintageous/vi/actions.py.
"""

import sublime
import sublime_plugin

from Vintageous.state import IrreversibleTextCommand
from Vintageous.state import VintageState
from Vintageous.vi import utils
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.constants import MODE_SELECT
from Vintageous.vi.constants import MODE_VISUAL_BLOCK
from Vintageous.vi.constants import regions_transformer
from Vintageous.vi.constants import regions_transformer_reversed
from Vintageous.vi.registers import REG_EXPRESSION

import re
import os
import stat


class _vi_modify_numbers(sublime_plugin.TextCommand):
    """
    Base class for Ctrl-x and Ctrl-a.
    """
    DIGIT_PAT = re.compile('(\D+?)?(-)?(\d+)(\D+)?')
    NUM_PAT = re.compile('\d')

    def get_editable_data(self, pt):
        sign = -1 if (self.view.substr(pt - 1) == '-') else 1
        end = pt
        while self.view.substr(end).isdigit():
            end += 1
        return (sign, int(self.view.substr(sublime.Region(pt, end))),
                sublime.Region(end, self.view.line(pt).b))


    def find_next_num(self, regions):
        # Modify selections that are inside a number already.
        for i, r in enumerate(regions):
            a = r.b
            if self.view.substr(r.b).isdigit():
                while self.view.substr(a).isdigit():
                    a -=1
                regions[i] = sublime.Region(a)

        lines = [self.view.substr(sublime.Region(r.b, self.view.line(r.b).b)) for r in regions]
        matches = [_vi_modify_numbers.NUM_PAT.search(text) for text in lines]
        if all(matches):
            return [(reg.b + ma.start()) for (reg, ma) in zip(regions, matches)]
        return []

    def run(self, edit, count=1, mode=None, subtract=False):
        if mode != _MODE_INTERNAL_NORMAL:
            return

        # TODO: Deal with octal, hex notations.
        # TODO: Improve detection of numbers.
        regs = list(self.view.sel())

        pts = self.find_next_num(regs)
        if not pts:
            utils.blink()
            return

        count = count if not subtract else -count
        end_sels = []
        for pt in reversed(pts):
            sign, num, tail = self.get_editable_data(pt)

            num_as_text = str((sign * num) + count)
            new_text = num_as_text + self.view.substr(tail)

            offset = 0
            if sign == -1:
                offset = -1
                self.view.replace(edit, sublime.Region(pt - 1, tail.b), new_text)
            else:
                self.view.replace(edit, sublime.Region(pt, tail.b), new_text)

            rowcol = self.view.rowcol(pt + len(num_as_text) - 1 + offset)
            end_sels.append(rowcol)

        self.view.sel().clear()
        for (row, col) in end_sels:
            self.view.sel().add(sublime.Region(self.view.text_point(row, col)))


class _vi_big_a(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, mode=None):
        def f(view, s):
            if mode == MODE_VISUAL_BLOCK:
                if self.view.substr(s.b - 1) == '\n':
                    return sublime.Region(s.end() - 1)
                return sublime.Region(s.end())
            elif mode == MODE_VISUAL:
                pt = s.b
                if self.view.substr(s.b - 1) == '\n':
                    pt -= 1
                if s.a > s.b:
                    pt = view.line(s.a).a
                return sublime.Region(pt)
            elif mode != _MODE_INTERNAL_NORMAL:
                return s
            hard_eol = self.view.line(s.b).end()
            return sublime.Region(hard_eol, hard_eol)

        regions_transformer(self.view, f)

        state = VintageState(self.view)
        state.enter_insert_mode()


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
    def run(self, edit, extend=False, mode=None):
        def f(view, s):
            if mode == MODE_VISUAL_BLOCK:
                return sublime.Region(s.begin())
            elif mode == MODE_VISUAL:
                pt = view.line(s.a).a
                if s.a > s.b:
                    pt = s.b
                return sublime.Region(pt)
            elif mode == MODE_VISUAL_LINE:
                line = view.line(s.a)
                pt = utils.next_non_white_space_char(view, line.a)
                return sublime.Region(pt)
            elif mode != _MODE_INTERNAL_NORMAL:
                return s
            line = view.line(s.b)
            pt = utils.next_non_white_space_char(view, line.a)
            return sublime.Region(pt, pt)

        state = VintageState(self.view)
        # TODO: Use next_mode in the command parser instead?
        state.enter_insert_mode()

        regions_transformer(self.view, f)


class _vi_p(sublime_plugin.TextCommand):
    def run(self, edit, register=None, count=1):
        state = VintageState(self.view)
        register = register or '"'
        fragments = state.registers[register]
        if not fragments:
            print("Vintageous: Nothing in register \".")
            return

        if state.mode == MODE_VISUAL:
            # force register population. We have to do it here
            vi_cmd_data = {
                "synthetize_new_line_at_eof": True,
                "yanks_linewise": False,
            }
            prev_text = state.registers.get_selected_text(vi_cmd_data)
            state.registers['"'] = prev_text

        sels = list(self.view.sel())
        # If we have the same number of pastes and selections, map 1:1. Otherwise paste paste[0]
        # to all target selections.
        if len(sels) == len(fragments):
            sel_to_frag_mapped = zip(sels, fragments)
        else:
            sel_to_frag_mapped = zip(sels, [fragments[0],] * len(sels))

        # FIXME: Fix this mess. Separate linewise from charwise pasting.
        pasting_linewise = True
        offset = 0
        paste_locations = []
        for selection, fragment in reversed(list(sel_to_frag_mapped)):
            fragment = self.prepare_fragment(fragment)
            if fragment.startswith('\n'):
                # Pasting linewise...
                # If pasting at EOL or BOL, make sure we paste before the newline character.
                if (utils.is_at_eol(self.view, selection) or
                    utils.is_at_bol(self.view, selection)):
                    l = self.paste_all(edit, selection,
                                       self.view.line(selection.b).b,
                                       fragment,
                                       count)
                    paste_locations.append(l)
                else:
                    l = self.paste_all(edit, selection,
                                   self.view.line(selection.b - 1).b,
                                   fragment,
                                   count)
                    paste_locations.append(l)
            else:
                pasting_linewise = False
                # Pasting charwise...
                # If pasting at EOL, make sure we don't paste after the newline character.
                if self.view.substr(selection.b) == '\n':
                    l = self.paste_all(edit, selection, selection.b + offset,
                                   fragment, count)
                    paste_locations.append(l)
                else:
                    l = self.paste_all(edit, selection, selection.b + offset + 1,
                                   fragment, count)
                    paste_locations.append(l)
                offset += len(fragment) * count

        if pasting_linewise:
            self.reset_carets_linewise()
        else:
            self.reset_carets_charwise(paste_locations, len(fragment))

    def reset_carets_charwise(self, paste_locations, paste_len):
        # FIXME: Won't work for multiple jagged pastes...
        b_pts = [s.b for s in list(self.view.sel())]
        if len(b_pts) > 1:
            self.view.sel().clear()
            self.view.sel().add_all([sublime.Region(ploc + paste_len - 1,
                                                    ploc + paste_len - 1)
                                            for ploc in paste_locations])
        else:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(paste_locations[0] + paste_len - 1,
                                               paste_locations[0] + paste_len - 1))

    def reset_carets_linewise(self):
        # FIXME: Won't work well for visual selections...
        # FIXME: This might not work for cmdline paste command (the target row isn't necessarily
        #        the next one.
        state = VintageState(self.view)
        if state.mode == MODE_VISUAL_LINE:
            self.view.run_command('collapse_to_a')
        else:
            # After pasting linewise, we should move the caret one line down.
            b_pts = [s.b for s in list(self.view.sel())]
            new_rows = [self.view.rowcol(b)[0] + 1 for b in b_pts]
            row_starts = [self.view.text_point(r, 0) for r in new_rows]
            self.view.sel().clear()
            self.view.sel().add_all([sublime.Region(pt, pt) for pt in row_starts])

    def prepare_fragment(self, text):
        if text.endswith('\n') and text != '\n':
            text = '\n' + text[0:-1]
        return text

    # TODO: Improve this signature.
    def paste_all(self, edit, sel, at, text, count):
        state = VintageState(self.view)
        if state.mode not in (MODE_VISUAL, MODE_VISUAL_LINE):
            # TODO: generate string first, then insert?
            # Make sure we can paste at EOF.
            at = at if at <= self.view.size() else self.view.size()
            for x in range(count):
                self.view.insert(edit, at, text)
                # Return position at which we have just pasted.
            return at
        else:
            if text.startswith('\n'):
                text = text * count
                if not text.endswith('\n'):
                    text = text + '\n'
            else:
                text = text * count

            if state.mode == MODE_VISUAL_LINE:
                if text.startswith('\n'):
                    text = text[1:]

            self.view.replace(edit, sel, text)
            # Return position at which we have just pasted.
            return sel.a


class _vi_big_p(sublime_plugin.TextCommand):
    def run(self, edit, register=None, count=1):
        state = VintageState(self.view)

        if state.mode == MODE_VISUAL:
            # force register population. We have to do it here
            vi_cmd_data = {
                "synthetize_new_line_at_eof": True,
                "yanks_linewise": False,
            }
            prev_text = state.registers.get_selected_text(vi_cmd_data)

        if register:
            fragments = state.registers[register]
        else:
            # TODO: There should be a simpler way of getting the unnamed register's content.
            fragments = state.registers['"']

        if state.mode == MODE_VISUAL:
            # Populate registers with the text we're about to paste.
            state.registers['"'] = prev_text

        sels = list(self.view.sel())
        if len(sels) == len(fragments):
            sel_frag = zip(sels, fragments)
        else:
            sel_frag = zip(sels, [fragments[0],] * len(sels))

        pasting_linewise = True
        offset = 0
        paste_locations = []
        for s, text in sel_frag:
            row = self.view.rowcol(s.begin())[0]
            row = max(0, row - 1)
            if text.endswith('\n'):
                if utils.is_at_eol(self.view, s) or utils.is_at_bol(self.view, s):
                    l = self.paste_all(edit, s, self.view.line(s.b).a, text, count)
                    paste_locations.append(l)
                else:
                    l = self.paste_all(edit, s, self.view.line(s.b - 1).a, text, count)
                    paste_locations.append(l)
            else:
                pasting_linewise = False
                l = self.paste_all(edit, s, s.b + offset, text, count)
                paste_locations.append(l)
                offset += len(text) * count

        if pasting_linewise:
            self.reset_carets_linewise()
        else:
            self.reset_carets_charwise(paste_locations, len(text))

    def paste_all(self, edit, sel, at, text, count):
        # for x in range(count):
        #     self.view.insert(edit, at, text)
        state = VintageState(self.view)
        if state.mode not in (MODE_VISUAL, MODE_VISUAL_LINE):
            for x in range(count):
                self.view.insert(edit, at, text)
            return at + (len(text) * (count - 1))

        else:
            if text.endswith('\n'):
                text = text * count
                if not text.startswith('\n'):
                    text = '\n' + text
            else:
                text = text * count
            self.view.replace(edit, sel, text)
            return sel.begin()

    def reset_carets_charwise(self, paste_locations, paste_len):
        # FIXME: Won't work for multiple jagged pastes...
        b_pts = [s.b for s in list(self.view.sel())]
        if len(b_pts) > 1:
            self.view.sel().clear()
            self.view.sel().add_all([sublime.Region(ploc + paste_len - 1,
                                                    ploc + paste_len - 1)
                                            for ploc in paste_locations])
        else:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(paste_locations[0] + paste_len - 1,
                                               paste_locations[0] + paste_len - 1))

    def reset_carets_linewise(self):
        # FIXME: Won't work well for visual selections...
        # FIXME: This might not work for cmdline paste command (the target row isn't necessarily
        #        the next one.
        state = VintageState(self.view)
        if state.mode == MODE_VISUAL_LINE:
            self.view.run_command('collapse_to_a')
        else:
            # After pasting linewise, we should move the caret one line down.
            b_pts = [s.b for s in list(self.view.sel())]
            new_rows = [self.view.rowcol(b)[0] + 1 for b in b_pts]
            row_starts = [self.view.text_point(r, 0) for r in new_rows]
            self.view.sel().clear()
            self.view.sel().add_all([sublime.Region(pt, pt) for pt in row_starts])


class ViEnterNormalMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)

        if state.mode == MODE_VISUAL:
            state.store_visual_selections()

        # When returning to normal mode from select mode, we want to keep the non-Vintageous
        # selections just created unless it's the last one.
        if not (state.mode == MODE_SELECT and len(self.view.sel()) > 1):
            self.view.run_command('collapse_to_direction')
            self.view.run_command('dont_stay_on_eol_backward')
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
        self.view.window().run_command('hide_auto_complete')


class ViEnterInsertMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        state.enter_insert_mode()
        self.view.run_command('collapse_to_direction')

        # TODO: abstract this away into a function.
        read_only = False
        if self.view.file_name():
            mode = os.stat(self.view.file_name())
            read_only = (stat.S_IMODE(mode.st_mode) & stat.S_IWUSR !=
                                                                stat.S_IWUSR)
            if read_only or self.view.is_read_only():
                # FIXME: Won't be displayed.
                sublime.status_message("Vintageous: Warning: Attempting to change read-only file.")


class ViEnterVisualMode(sublime_plugin.TextCommand):
    def run(self, edit, count=None):
        def f(view, s):
            return sublime.Region(s.a, s.b + (count - 1))

        state = VintageState(self.view)
        state.enter_visual_mode()
        self.view.run_command('extend_to_minimal_width')

        if count > 1:
            regions_transformer(self.view, f)


class ViEnterVisualBlockMode(sublime_plugin.TextCommand):
    def run(self, edit):
        # Handling multiple visual blocks seems quite hard, so ensure we only have one.
        first = list(self.view.sel())[0]
        self.view.sel().clear()
        self.view.sel().add(first)

        state = VintageState(self.view)
        state.enter_visual_block_mode()
        self.view.run_command('extend_to_minimal_width')


class ViEnterSelectMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        state.enter_select_mode()


class ViEnterVisualLineMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        state.enter_visual_line_mode()


class ViEnterReplaceMode(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        state.enter_replace_mode()
        self.view.run_command('collapse_to_direction')
        state.reset()


class SetAction(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, action):
        state = VintageState(self.view)
        state.action = action
        state.eval()


class SetMotion(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, motion):
        state = VintageState(self.view)
        state.motion = motion
        state.eval()


class ViPushDigit(sublime_plugin.TextCommand):
    def run(self, edit, digit):
        state = VintageState(self.view)
        if not (state.action or state.motion):
            state.push_motion_digit(digit)
        elif state.action:
            state.push_action_digit(digit)


# TODO: Remove this.
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

        # FIXME: We can't repeat 5ifoo<esc>
        self.view.run_command('mark_undo_groups_for_gluing')
        # ...User types text...


class ViRunNormalInsertModeActions(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        # We've recorded what the user has typed into the buffer. Turn macro recording off.
        self.view.run_command('glue_marked_undo_groups')

        # FIXME: We can't repeat 5ifoo<esc> after we're done.
        for i in range(state.count - 1):
            self.view.run_command('repeat')

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
            if character not in (REG_EXPRESSION,):
                state.register = character
                state.expecting_register = False
            else:
                self.view.run_command('vi_expression_register')


class ViExpressionRegister(sublime_plugin.TextCommand):
    def run(self, edit, insert=False, next_mode=None):
        def on_done(s):
            state = VintageState(self.view)
            try:
                rv = [str(eval(s, None, None)),]
                if not insert:
                    # TODO: We need to sort out the values received and sent to registers. When pasting,
                    # we assume a list... This should be encapsulated in Registers.
                    state.registers[REG_EXPRESSION] = rv
                else:
                    self.view.run_command('insert_snippet', {'contents': str(rv[0])})
                    state.reset()
            except:
                sublime.status_message("Vintageous: Invalid expression.")
                on_cancel()

        def on_cancel():
            state = VintageState(self.view)
            state.reset()

        self.view.window().show_input_panel('', '', on_done, None, on_cancel)


class _vi_m(sublime_plugin.TextCommand):
    def run(self, edit, character=None):
        state = VintageState(self.view)
        state.marks.add(character, self.view)


class _vi_quote(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, character=None, extend=False):
        def f(view, s):
            if mode == MODE_VISUAL:
                if s.a <= s.b:
                    if address.b < s.b:
                        return sublime.Region(s.a + 1, address.b)
                    else:
                        return sublime.Region(s.a, address.b)
                else:
                    return sublime.Region(s.a + 1, address.b)
            elif mode == MODE_NORMAL:
                return address
            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, address.b)

            return s

        state = VintageState(self.view)
        address = state.marks.get_as_encoded_address(character)

        if address is None:
            return

        if isinstance(address, str):
            if not address.startswith('<command'):
                self.view.window().open_file(address, sublime.ENCODED_POSITION)
            else:
                # We get a command in this form: <command _vi_double_quote>
                self.view.run_command(address.split(' ')[1][:-1])
            return

        # This is a motion in a composite command.
        regions_transformer(self.view, f)


# TODO: Revise this text object... Can't we have a simpler approach without
# this intermediary step?
class ViI(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, inclusive=False):
        state = VintageState(self.view)
        if inclusive:
            state.motion = 'vi_inclusive_text_object'
        else:
            state.motion = 'vi_exclusive_text_object'


class CollectUserInput(IrreversibleTextCommand):
    def __init__(self, view):
        IrreversibleTextCommand.__init__(self, view)

    def run(self, character=None):
        state = VintageState(self.view)
        state.user_input += character
        # The .user_input setter handles resetting the following property.
        if not state.expecting_user_input:
            state.eval()


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

        number_of_lines = (bottommost_visible_row - current_row) - 1

        if number_of_lines > 1:
            self.view.run_command('scroll_lines', {'amount': number_of_lines})


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


class _vi_r(sublime_plugin.TextCommand):
    def run(self, edit, character=None, mode=None):
        def f(view, s):
            next_row = view.rowcol(s.b - 1)[0] + 1
            pt = view.text_point(next_row, 0)
            return sublime.Region(pt, pt)

        def ff(view, s):
            # no ending \n
            if view.substr(s.end() - 1) == '\n':
                s = sublime.Region(s.begin(), s.end() - 1)
            lines = view.split_by_newlines(s)
            for line in lines:
                view.replace(edit, line, character * line.size())
            return sublime.Region(s.begin(), s.begin())

        if mode == _MODE_INTERNAL_NORMAL:
            for s in self.view.sel():
                self.view.replace(edit, s, character * s.size())
        elif mode in (MODE_VISUAL, MODE_VISUAL_LINE):
            regions_transformer(self.view, ff)
            return

        if character == '\n':
            regions_transformer(self.view, f)



class _vi_undo(IrreversibleTextCommand):
    """Once the latest vi command has been undone, we might be left with non-empty selections.
    This is due to the fact that Vintageous defines selections in a separate step to the actual
    command running. For example, v,e,d,u would undo the deletion operation and restore the
    selection that v,e had created.

    Assuming that after an undo we're back in normal mode, we can take for granted that any leftover
    selections must be destroyed. I cannot think of any situation where Vim would have to restore
    selections after *u*, but it may well happen under certain circumstances I'm not aware of.

    Note 1: We are also relying on Sublime Text to restore the v or V selections existing at the
    time the edit command was run. This seems to be safe, but we're blindly relying on it.

    Note 2: Vim knows the position the caret was in before creating the visual selection. In
    Sublime Text we lose that information (at least it doesn't seem to be straightforward to
    obtain).
    """
    #  !!! This is a special command that does not go through the usual processing. !!!
    #  !!! It must skip the undo stack. !!!

    # TODO: It must be possible store or retrieve the actual position of the caret before the
    # visual selection performed by the user.
    def run(self):
        # We define our own transformer here because we want to handle undo as a special case.
        # TODO: I don't know if it needs to be an special case in reality.
        def f(view, s):
            # Compensates the move issued below.
            if s.a < s.b :
                return sublime.Region(s.a + 1, s.a + 1)
            else:
                return sublime.Region(s.a, s.a)

        state = VintageState(self.view)
        for i in range(state.count):
            self.view.run_command('undo')

        if self.view.has_non_empty_selection_region():
            regions_transformer(self.view, f)
            # !! HACK !! /////////////////////////////////////////////////////////
            # This is a hack to work around an issue in Sublime Text:
            # When undoing in normal mode, Sublime Text seems to prime a move by chars
            # forward that has never been requested by the user or Vintageous.
            # As far as I can tell, Vintageous isn't at fault here, but it seems weird
            # to think that Sublime Text is wrong.
            self.view.run_command('move', {'by': 'characters', 'forward': False})
            # ////////////////////////////////////////////////////////////////////

        state.update_xpos()
        # Ensure that we wipe the count, if any.
        state.reset()


class _vi_repeat(IrreversibleTextCommand):
    """Vintageous manages the repeat operation on its own to ensure that we always use the latest
       modifying command, instead of being tied to the undo stack (as Sublime Text is by default).
    """

    #  !!! This is a special command that does not go through the usual processing. !!!
    #  !!! It must skip the undo stack. !!!

    def run(self):
        state = VintageState(self.view)

        try:
            cmd, args, _ = state.repeat_command
        except TypeError:
            # Unreachable.
            return

        # Signal that we're not simply issuing an interactive command, but rather repeating one.
        # This is necessary, for example, to notify _vi_k that it should become _vi_j instead
        # if the former was run in visual mode.
        state.settings.vi['_is_repeating'] = True

        if not cmd:
            return
        elif cmd == 'vi_run':
            args['next_mode'] = MODE_NORMAL
            args['follow_up_mode'] = 'vi_enter_normal_mode'
            args['count'] = state.count * args['count']
            self.view.run_command(cmd, args)
        elif cmd == 'sequence':
            for i, _ in enumerate(args['commands']):
                # We can have either 'vi_run' commands or plain insert mode commands.
                if args['commands'][i][0] == 'vi_run':
                    # Access this shape: {"commands":[['vi_run', {"foo": 100}],...]}
                    args['commands'][i][1]['next_mode'] = MODE_NORMAL
                    args['commands'][i][1]['follow_up_mode'] = 'vi_enter_normal_mode'

            # TODO: Implement counts properly for 'sequence' command.
            for i in range(state.count):
                self.view.run_command(cmd, args)

        # Ensure we wipe count data if any.
        state.reset()
        # XXX: Needed here? Maybe enter_... type commands should be IrreversibleTextCommands so we
        # must/can call them whenever we need them withouth affecting the undo stack.
        self.view.run_command('vi_enter_normal_mode')
        state.settings.vi['_is_repeating'] = False


class _vi_redo(IrreversibleTextCommand):
    #  !!! This is a special command that does not go through the usual processing. !!!
    #  !!! It must skip the undo stack. !!!

    # TODO: It must be possible store or retrieve the actual position of the caret before the
    # visual selection performed by the user.
    def run(self):
        state = VintageState(self.view)
        for i in range(state.count):
            self.view.run_command('redo')

        state.update_xpos()
        # Ensure that we wipe the count, if any.
        state.reset()
        self.view.run_command('vi_enter_normal_mode')


class _vi_ctrl_w_v_action(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().run_command('ex_vsplit')


class Sequence(sublime_plugin.TextCommand):
    """Required so that mark_undo_groups_for_gluing and friends work.
    """
    def run(self, edit, commands):
        for cmd, args in commands:
            self.view.run_command(cmd, args)

        # XXX: Sequence is a special case in that it doesn't run through vi_run, so we need to
        # ensure the next mode is correct. Maybe we can improve this by making it more similar to
        # regular commands?
        state = VintageState(self.view)
        state.enter_normal_mode()


class _vi_big_j(sublime_plugin.TextCommand):
    WHITE_SPACE = ' \t'

    def row_at(self, pt):
        return self.view.rowcol(pt)[0]

    def get_separator(self, pt):
        # Get the line's last character.
        pt = self.view.line(pt).b - 1
        c = self.view.substr(pt)
        sep = c if c in _vi_big_j.WHITE_SPACE else ''
        return sep

    def run(self, edit, mode=None, separator=' ', count=1):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                end_pos = self.view.line(s.b).b
                sep = self.get_separator(s.a)
                start = end = s.b
                if count > 2:
                    end = self.view.text_point(self.row_at(s.b) + (count - 1), 0)
                    end = self.view.line(end).b
                else:
                    # Join current line and the next.
                    end = self.view.text_point(self.row_at(s.b) + 1, 0)
                    end = self.view.line(end).b
            elif mode == MODE_VISUAL:
                if s.a < s.b:
                    sep = self.get_separator(s.a)
                    end_pos = self.view.line(s.a).b
                    start = s.a
                    if self.row_at(s.b - 1) == self.row_at(s.a):
                        end = self.view.text_point(self.row_at(s.a) + 1, 0)
                    else:
                        end = self.view.text_point(self.row_at(s.b - 1), 0)
                    end = self.view.line(end).b
                else:
                    sep = self.get_separator(s.b)
                    end_pos = self.view.line(s.b).b
                    start = s.b
                    if self.row_at(s.b) == self.row_at(s.a - 1):
                        end = self.view.text_point(self.row_at(s.a - 1) + 1, 0)
                    else:
                        end = self.view.text_point(self.row_at(s.a - 1), 0)
                    end = self.view.line(end).b
            else:
                return s

            text_to_join = self.view.substr(sublime.Region(start, end))
            text_to_join = re.sub(r'\n+', r'\n', text_to_join)
            lines = text_to_join.split('\n')
            lines = [l.lstrip().rstrip() for l in lines]
            text_to_join = '\n'.join(lines)

            if separator:
                # J
                joined_text = text_to_join.replace('\n', sep or separator)
            else:
                # gJ
                joined_text = text_to_join.replace('\n', '')

            self.view.replace(edit, sublime.Region(start, end), joined_text)
            return sublime.Region(end_pos)

        regions_transformer(self.view, f)


class _vi_g_v(IrreversibleTextCommand):
    def run(self):
        # Assume normal mode.
        regs = (self.view.get_regions('vi_visual_selections') or
                list(self.view.sel()))

        self.view.sel().clear()
        for r in regs:
            self.view.sel().add(r)


class _vi_q(IrreversibleTextCommand):
    def run(self, name=None):
        state = VintageState(self.view)

        if name == None and not state.is_recording:
            return

        if not state.is_recording:
            self.view.run_command('unmark_undo_groups_for_gluing')
            state.latest_macro_name = name
            state.is_recording = True
            self.view.run_command('start_record_macro')
            return

        if state.is_recording:
            self.view.run_command('stop_record_macro')
            state.is_recording = False
            self.view.run_command('unmark_undo_groups_for_gluing')
            state.reset()

            # Store the macro away.
            state.macros[state.latest_macro_name] = sublime.get_macro()


class _vi_run_macro(IrreversibleTextCommand):
    def run(self, name=None):
        state = VintageState(self.view)
        state.cancel_macro = False
        if not (name and state.latest_macro_name):
            return

        if name == '@':
            # Run the macro recorded latest.
            commands = state.macros[state.latest_macro_name]
        else:
            try:
                commands = state.macros[name]
            except KeyError:
                # TODO: Add 'delayed message' support to VintageState.
                return

        for cmd in commands:
            if state.cancel_macro:
                utils.blink()
                break
            self.view.run_command(cmd['command'], cmd['args'])


class _vi_ctrl_w_q(IrreversibleTextCommand):
    def run(self):
        self.view.close()


class _vi_ctrl_w_l(IrreversibleTextCommand):
    # TODO: Should be a window command instead.
    # TODO: Should focus the group to the right only, not the 'next' group.
    def run(self):
        w = self.view.window()
        current_group = w.active_group()
        if w.num_groups() > 1:
            w.focus_group(current_group + 1)


class _vi_ctrl_w_big_l(IrreversibleTextCommand):
    def run(self):
        w = self.view.window()
        current_group = w.active_group()
        if w.num_groups() > 1:
            w.set_view_index(self.view, current_group + 1, 0)
            w.focus_group(current_group + 1)


class _vi_ctrl_w_h(IrreversibleTextCommand):
    # TODO: Should be a window command instead.
    # TODO: Should focus the group to the left only, not the 'previous' group.
    def run(self):
        w = self.view.window()
        current_group = w.active_group()
        if current_group > 0:
            w.focus_group(current_group - 1)


class _vi_ctrl_w_big_h(IrreversibleTextCommand):
    def run(self):
        w = self.view.window()
        current_group = w.active_group()
        if current_group > 0:
            w.set_view_index(self.view, current_group - 1, 0)
            w.focus_group(current_group - 1)


class _vi_g_tilde_g_tilde(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                line = view.line(s.b)
                if view.substr(line).isupper():
                    view.replace(edit, line, view.substr(line).lower())
                else:
                    view.replace(edit, line, view.substr(line).upper())
                return line
            return s

        regions_transformer(self.view, f)


class _vi_cc_action(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            # We've made a selection with _vi_cc_motion just before this.
            if mode == _MODE_INTERNAL_NORMAL:
                begin = self.view.text_point(self.view.rowcol(s.b)[0], 0)
                view.erase(edit, s)
                return sublime.Region(begin)
            return s

        def ff(view, s):
            # We've made a selection with _vi_cc_motion just before this.
            if mode == _MODE_INTERNAL_NORMAL:
                pt = utils.next_non_white_space_char(view, s.b, white_space=' \t')
                return sublime.Region(pt)
            return s

        prev_rows = [self.view.rowcol(s.a)[0] for s in list(self.view.sel())]
        regions_transformer_reversed(self.view, f)
        if mode == _MODE_INTERNAL_NORMAL:
            self.view.sel().clear()
            self.view.sel().add_all(list(sublime.Region(self.view.text_point(row, 0)) for row in prev_rows))
            self.view.run_command('reindent', {'force_indent': False})
        regions_transformer_reversed(self.view, ff)


# internal command
class _vi_int_reindent(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            # We've made a selection with _vi_cc_motion just before this.
            if mode == _MODE_INTERNAL_NORMAL:
                begin = self.view.text_point(self.view.rowcol(s.b)[0], 0)
                self.view.run_command('reindent', {'force_indent': False})
                return sublime.Region(begin)
            return s

        regions_transformer_reversed(self.view, f)


class _vi_dd_action(sublime_plugin.TextCommand):
    def row_at(self, pt):
        return self.view.rowcol(pt)[0]

    def run(self, edit, mode=None):
        def f(view, s):
            # We've made a selection with _vi_cc_motion just before this.
            if mode == _MODE_INTERNAL_NORMAL:
                view.erase(edit, s)
                if self.row_at(s.a) != self.row_at(self.view.size()):
                    pt = utils.next_non_white_space_char(view, s.a, white_space=' \t')
                else:
                    pt = utils.next_non_white_space_char(view,
                                                         self.view.line(s.a).a,
                                                         white_space=' \t')

                return sublime.Region(pt, pt)
            return s

        row = [self.view.rowcol(s.begin())[0] for s in self.view.sel()][0]
        regions_transformer_reversed(self.view, f)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(self.view.text_point(row, 0)))


class _vi_big_s_action(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            # We've made a selection with _vi_big_s_motion just before this.
            if mode == _MODE_INTERNAL_NORMAL:
                pt = utils.next_non_white_space_char(view, s.a, white_space=' \t')
                view.erase(edit, sublime.Region(pt, view.line(s.b).b))
                return sublime.Region(pt, pt)
            return s

        regions_transformer(self.view, f)


class ViSoftUndo(IrreversibleTextCommand):
    """Belongs to the non-standard selection mode of Vintageous (gh).
    """
    def run(self):
        # Don't deselect the last instance. If the user really wants to destroy the visual
        # selection, he can just press Esc or move the caret.
        if len(self.view.sel()) == 1:
            return

        self.view.run_command('soft_undo')


class _vi_ctrl_e(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        # TODO: Implement this motion properly; don't use built-in commands.
        # We're using an action because we don't care too much right now and we don't want the
        # motion to blink every time we issue it (it does because the selections don't change and
        # Vintageous rightfully thinks it has failed.)
        if mode == MODE_VISUAL_LINE:
            return
        extend = True if mode == MODE_VISUAL else False
        self.view.run_command('scroll_lines', {'amount': -1, 'extend': extend})


class _vi_ctrl_y(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        # TODO: Implement this motion properly; don't use built-in commands.
        # We're using an action because we don't care too much right now and we don't want the
        # motion to blink every time we issue it (it does because the selections don't change and
        # Vintageous rightfully thinks it has failed.)
        if mode == MODE_VISUAL_LINE:
            return
        extend = True if mode == MODE_VISUAL else False
        self.view.run_command('scroll_lines', {'amount': 1, 'extend': extend})


#  _ivi_... for 'insert vi...'
class _ivi_ctrl_u(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            return sublime.Region(s.b, view.line(s.b).a)

        regions_transformer(self.view, f)

        self.view.run_command('left_delete')
