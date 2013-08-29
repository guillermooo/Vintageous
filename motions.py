"""Sublime Text commands performing vim motions.

   If you are implementing a new motion command, stick it here.

   Motion parsers belong instead in Vintageous/vi/motions.py.
"""

# == NOTES ABOUT THE IMPLEMENTATION OF MOTION COMMANDS
#
# Keep motion commands decoupled from state.VintageState. Pass them all necessary state data as
# arguments (and only JSON values).
#
# For example, DON'T do this:
#
#   def run(self, ...):
#       ...
#       state = VintageState(self.view)
#       if state.mode == MODE_NORMAL:
#           ...
#
# But DO this instead:
#
#   def run(self, mode=None, ...):
#       ...
#       if mode == MODE_NORMAL:
#           ...
#
#  Sublime Text commands must base its operation on arguments so that macros, undo and repeat work
#  as expected. (There may be, however, exceptions.)
#
#  Also, motion commands should be as independent of each other as possible. This is why
#  keeping so many classes in the same file should not impair their comprehension.
#
# == MOTION COMMAND NAMING
#
# Motion names should follow this pattern: _vi_l, _vi_g_h, etc.
#
# == ANATOMY OF A MOTION COMMAND
#
# (Any motion command not conforming to the pattern described below must be updated or is an
# exception to the general rule.)
#
# Typically, motion commands follow the same pattern to deal with multiple modes and multiple
# selections.
#
# Some of the work to implement motions so that they play well with Sublime Text has been abstracted
# away, most notably in `regions_transformer`.
#
# Motions normally specify a transformer function nested within their .run() method. They might do
# some work in .run() too, if necessary. The transformer function is called `f` by convention.
# For each selection in the active view, it receives the `view` instance and a selection region.
# This way, you modify all selections in the view, one by one (in order).
#
# Inside `f`, you must proceed in different ways depending on the current mode. For instance, in
# visual mode, the `l` motion can move past the new line character, but not in normal mode.
# Branching out inside `f` you can accommodate this differences.
#
# `f` must always return a new sublime.Region instance to replace the corresponding one. As a safety
# measure, you should *always* return the passed in selection region again for unhandled cases. This
# ensures correct operation for unimplemented modes for the command or invalid modes for the command.
#
# A simple motion to check out for an implementation of this pattern is `_vi_g__`, which advances
# all carets to the end of the line, excluding the new line character.


import sublime
import sublime_plugin

from Vintageous.vi.constants import regions_transformer
from Vintageous.vi.constants import MODE_VISUAL, MODE_NORMAL, _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.state import VintageState, IrreversibleTextCommand
from Vintageous.vi import utils
from Vintageous.vi.search import reverse_search
from Vintageous.vi.search import reverse_search_by_pt
from Vintageous.vi.search import find_in_range
from Vintageous.vi.search import find_wrapping
from Vintageous.vi.search import reverse_find_wrapping
from Vintageous.vi.search import BufferSearchBase
from Vintageous.vi.search import ExactWordBufferSearchBase
from Vintageous.vi import units

import Vintageous.state

from itertools import chain
import re


class ViMoveToHardBol(sublime_plugin.TextCommand):
    def run(self, edit, extend=False):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            hard_bol = self.view.line(s.b).begin()
            if s.a < s.b and (self.view.line(s.a) != self.view.line(s.b)) and self.view.full_line(hard_bol - 1).b == hard_bol:
                hard_bol += 1
            a, b = (hard_bol, hard_bol) if not extend else (s.a, hard_bol)
            # Avoid ending up with a en empty selection while on visual mode.

            if extend and s.a == hard_bol:
                b = b + 1
            new_sels.append(sublime.Region(a, b))

        for s in new_sels:
            self.view.sel().add(s)

# FIXME: Only find exact char counts. Vim ignores the command when the count is larger than the
# number of instances of the sought character.
class ViFindInLineInclusive(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, character=None, mode=None, count=1, change_direction=True):
        def f(view, s):
            eol = view.line(s.b).end()
            if not s.empty():
                eol = view.line(s.b - 1).end()

            match = s
            for i in range(count):

                # Define search range as 'rest of the line to the right'.
                if state.mode != MODE_VISUAL:
                    search_range = sublime.Region(min(match.b + 1, eol), eol)
                else:
                    search_range = sublime.Region(min(match.b, eol), eol)

                match = find_in_range(view, character,
                                            search_range.a,
                                            search_range.b,
                                            sublime.LITERAL)

                # Count too high or simply no match; break.
                if match is None:
                    match = s
                    break

            if state.mode == MODE_VISUAL or mode == _MODE_INTERNAL_NORMAL:
                if match == s:
                    # FIXME: It won't blink because the current light can't be highlighted right
                    # now (we are in command mode and there is a selection on the screen. Perhaps
                    # we can make the gutter blink instead.)
                    utils.blink()
                return sublime.Region(s.a, match.b)

            if match == s:
                utils.blink()
            return sublime.Region(match.a, match.a)


        # TODO: Give feedback to the user that the search failed?
        if character is None:
            return
        else:
            state = VintageState(self.view)
            state.last_character_search = character
            # Change only if the command is f, F, t, T; not if it's ',' or ';'.
            if change_direction:
                state.last_character_search_forward = True

        regions_transformer(self.view, f)


# FIXME: Only find exact char counts. Vim ignores the command when the count is larger than the
# number of instances of the sought character.
class ViReverseFindInLineInclusive(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, character=None, mode=None, count=1, change_direction=True):
        def f(view, s):
            # TODO: Refactor this mess.
            line_text = view.substr(sublime.Region(view.line(s.b).a, s.b))
            offset = 0
            a, b = view.line(s.b).a, s.b
            final_offset = -1

            try:
                for i in range(count):
                    line_text = view.substr(sublime.Region(a, b))
                    match_in_line = line_text.rindex(character)

                    final_offset = match_in_line

                    b = view.line(s.a).a + final_offset
            except ValueError:
                pass

            if final_offset > -1:
                pt = view.line(s.b).a + final_offset

                state = VintageState(view)
                if mode == _MODE_INTERNAL_NORMAL:
                    if sublime.Region(s.b, pt) == s:
                        utils.blink()
                        return s
                    return sublime.Region(s.a, pt)
                elif mode == MODE_VISUAL:
                    if sublime.Region(s.b, pt) == s:
                        utils.blink()
                        return s
                    if s.a < s.b and pt < s.a:
                        return sublime.Region(s.a + 1, pt)
                    if pt >= s.a:
                        return sublime.Region(s.a, pt + 1)
                    return sublime.Region(s.a, pt)

                if pt == s.b:
                    utils.blink()
                    return s
                return sublime.Region(pt, pt)

            return s


        if character is None:
            return
        else:
            state = VintageState(self.view)
            state.last_character_search = character
            # Change only if the command is f, F, t, T; not if it's ',' or ';'.
            if change_direction:
                state.last_character_search_forward = False

        regions_transformer(self.view, f)


class ViFindInLineExclusive(sublime_plugin.TextCommand):
    """Contrary to *f*, *t* does not look past the caret's position, so if ``character`` is under
       the caret, nothing happens.
    """
    def run(self, edit, extend=False, character=None, mode=None, count=1, change_direction=True):
        def f(view, s):
            eol = view.line(s.b).end()
            if not s.empty():
                eol = view.line(s.b - 1).end()

            match = s
            offset = 1 if count > 1 else 0
            for i in range(count):

                # Define search range as 'rest of the line to the right'.
                if state.mode != MODE_VISUAL:
                    search_range = sublime.Region(min(match.b + 1 + offset, eol), eol)
                else:
                    search_range = sublime.Region(min(match.b + offset, eol), eol)

                match = find_in_range(view, character,
                                            search_range.a,
                                            search_range.b,
                                            sublime.LITERAL)

                # Count too high or simply no match; break.
                if match is None:
                    match = s
                    break

            if state.mode == MODE_VISUAL or mode == _MODE_INTERNAL_NORMAL:
                if match == s:
                    # FIXME: It won't blink because the current light can't be highlighted right
                    # now (we are in command mode and there is a selection on the screen. Perhaps
                    # we can make the gutter blink instead.)
                    utils.blink()
                    return s
                return sublime.Region(s.a, match.b - 1)

            if match == s:
                utils.blink()
                return s
            return sublime.Region(match.a - 1, match.a - 1)

        # TODO: Give feedback to the user that the search failed?
        if character is None:
            return
        else:
            state = VintageState(self.view)
            state.last_character_search = character
            # Change only if the command is f, F, t, T; not if it's ',' or ';'.
            if change_direction:
                state.last_character_search_forward = True

        regions_transformer(self.view, f)


class ViReverseFindInLineExclusive(sublime_plugin.TextCommand):
    """Contrary to *F*, *T* does not look past the caret's position, so if ``character`` is right
       before the caret, nothing happens.
    """
    def run(self, edit, extend=False, character=None, mode=None, count=1, change_direction=True):
        def f(view, s):
            line_text = view.substr(sublime.Region(view.line(s.b).a, s.b))
            a, b = view.line(s.b).a, s.b
            final_offset = -1

            try:
                for i in range(count):
                    line_text = view.substr(sublime.Region(a, b))
                    match_in_line = line_text.rindex(character)

                    final_offset = match_in_line

                    b = view.line(s.a).a + final_offset
            except ValueError:
                pass

            if final_offset > -1:
                pt = view.line(s.b).a + final_offset

                state = VintageState(view)
                if state.mode == MODE_VISUAL or mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.a, pt + 1)

                return sublime.Region(pt + 1, pt + 1)

            return s


        if character is None:
            return
        else:
            state = VintageState(self.view)
            state.last_character_search = character
            # Change only if the command is f, F, t, T; not if it's ',' or ';'.
            if change_direction:
                state.last_character_search_forward = False

        regions_transformer(self.view, f)


class ViGoToLine(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, line=None, mode=None):
        line = line if line > 0 else 1
        dest = self.view.text_point(line - 1, 0)

        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(dest, dest)
            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(view.line(s.a).a, view.line(dest).b)
            elif mode == MODE_VISUAL:
                if dest < s.a and s.a < s.b:
                    return sublime.Region(s.a + 1, dest)
                elif dest < s.a:
                    return sublime.Region(s.a, dest)
                elif dest > s.b and s.a > s.b:
                    return sublime.Region(s.a - 1, dest + 1)
                return sublime.Region(s.a, dest + 1)
            elif mode == MODE_VISUAL_LINE:
                if dest < s.a and s.a < s.b:
                    return sublime.Region(view.full_line(s.a).b, dest)
                elif dest < s.a:
                    return sublime.Region(s.a, dest)
                elif dest > s.a and s.a > s.b:
                    return sublime.Region(view.full_line(s.a - 1).a, view.full_line(dest).b)
                return sublime.Region(s.a, view.full_line(dest).b)
            return s

        regions_transformer(self.view, f)

        # FIXME: Bringing the selections into view will be undesirable in many cases. Maybe we
        # should have an optional .scroll_selections_into_view() step during command execution.
        self.view.show(self.view.sel()[0])


class ViPercent(sublime_plugin.TextCommand):
    # TODO: Perhaps truly support multiple regions here?
    pairs = (
            ('(', ')'),
            ('[', ']'),
            ('{', '}'),
    )

    def run(self, edit, extend=False, percent=None, mode=None):
        if percent == None:
            def move_to_bracket(view, s):
                def find_bracket_location(pt):
                    bracket, brackets, bracket_pt = self.find_a_bracket(pt)
                    if not bracket:
                        return

                    if bracket == brackets[0]:
                        return self.find_balanced_closing_bracket(bracket_pt + 1, brackets)
                    else:
                        return self.find_balanced_opening_bracket(bracket_pt, brackets)

                if mode == MODE_VISUAL:
                    # TODO: Improve handling of s.a < s.b and s.a > s.b cases.
                    a = find_bracket_location(s.b - 1)
                    if a is not None:
                        a = a + 1 if a > s.b else a
                        if a == s.a:
                            a += 1
                        return sublime.Region(s.a, a)

                elif mode == MODE_NORMAL:
                    a = find_bracket_location(s.b)
                    if a is not None:
                        return sublime.Region(a, a)

                # TODO: According to Vim we must swallow brackets in this case.
                elif mode == _MODE_INTERNAL_NORMAL:
                    a = find_bracket_location(s.b)
                    if a is not None:
                        return sublime.Region(s.a, a)

                return s

            regions_transformer(self.view, move_to_bracket)

            return

        row = self.view.rowcol(self.view.size())[0] * (percent / 100)

        def f(view, s):
            pt = view.text_point(row, 0)
            return sublime.Region(pt, pt)

        regions_transformer(self.view, f)

        # FIXME: Bringing the selections into view will be undesirable in many cases. Maybe we
        # should have an optional .scroll_selections_into_view() step during command execution.
        self.view.show(self.view.sel()[0])

    def find_a_bracket(self, caret_pt):
        """Locates the next bracket after the caret in the current line.
           If None is found, execution must be aborted.
           Returns: (bracket, brackets, bracket_pt)

           Example: ('(', ('(', ')'), 1337))
        """
        caret_row, caret_col = self.view.rowcol(caret_pt)
        line_text = self.view.substr(sublime.Region(caret_pt,
                                                    self.view.line(caret_pt).b))
        try:
            found_brackets = min([(line_text.index(bracket), bracket)
                                        for bracket in chain(*self.pairs)
                                        if bracket in line_text])
        except ValueError:
            return None, None, None

        bracket_a, bracket_b = [(a, b) for (a, b) in self.pairs
                                       if found_brackets[1] in (a, b)][0]
        return (found_brackets[1], (bracket_a, bracket_b),
                self.view.text_point(caret_row, caret_col + found_brackets[0]))

    def find_balanced_closing_bracket(self, start, brackets, unbalanced=0):
        new_start = start
        for i in range(unbalanced or 1):
            next_closing_bracket = find_in_range(self.view, brackets[1],
                                                 start=new_start,
                                                 end=self.view.size(),
                                                 flags=sublime.LITERAL)
            if next_closing_bracket is None:
                # Unbalanced brackets; nothing we can do.
                return
            new_start = next_closing_bracket.end()

        nested = 0
        while True:
            next_opening_bracket = find_in_range(self.view, brackets[0],
                                                 start=start,
                                                 end=next_closing_bracket.end(),
                                                 flags=sublime.LITERAL)
            if not next_opening_bracket:
                break
            nested += 1
            start = next_opening_bracket.end()

        if nested > 0:
            return self.find_balanced_closing_bracket(next_closing_bracket.end(),
                                                      brackets, nested)
        else:
            return next_closing_bracket.begin()

    def find_balanced_opening_bracket(self, start, brackets, unbalanced=0):
        new_start = start
        for i in range(unbalanced or 1):
            prev_opening_bracket = reverse_search_by_pt(self.view, brackets[0],
                                                      start=0,
                                                      end=new_start,
                                                      flags=sublime.LITERAL)
            if prev_opening_bracket is None:
                # Unbalanced brackets; nothing we can do.
                return
            new_start = prev_opening_bracket.begin()

        nested = 0
        while True:
            next_closing_bracket = reverse_search_by_pt(self.view, brackets[1],
                                                  start=prev_opening_bracket.a,
                                                  end=start,
                                                  flags=sublime.LITERAL)
            if not next_closing_bracket:
                break
            nested += 1
            start = next_closing_bracket.begin()

        if nested > 0:
            return self.find_balanced_opening_bracket(prev_opening_bracket.begin(),
                                                      brackets,
                                                      nested)
        else:
            return prev_opening_bracket.begin()


class _vi_big_h(sublime_plugin.TextCommand):
    def run(self, edit, count=None, extend=False, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(target, target)
            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a + 1, target)
            elif mode == MODE_VISUAL:
                new_target = utils.next_non_white_space_char(view, target)
                return sublime.Region(s.a + 1, new_target)
            else:
                return s

        r = self.view.visible_region()
        row, _ = self.view.rowcol(r.a)
        row += count + 1

        target = self.view.text_point(row, 0)

        regions_transformer(self.view, f)
        self.view.show(target)


class ViBigL(sublime_plugin.TextCommand):
    def run(self, edit, count=None, extend=False, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(target, target)
            elif mode == _MODE_INTERNAL_NORMAL:
                if s.b >= target:
                    return sublime.Region(s.a + 1, target)
                return sublime.Region(s.a, target)
            elif mode == MODE_VISUAL:
                if s.b >= target:
                    new_target = utils.next_non_white_space_char(view, target)
                    return sublime.Region(s.a + 1, new_target)
                new_target = utils.next_non_white_space_char(view, target)
                return sublime.Region(s.a, new_target + 1)
            else:
                return s

        r = self.view.visible_region()
        row, _ = self.view.rowcol(r.b)
        row -= count + 1

        # XXXX: Subtract 1 so that Sublime Text won't attempt to scroll the line into view, which
        # would be quite annoying.
        target = self.view.text_point(row - 1, 0)

        regions_transformer(self.view, f)
        self.view.show(target)


class ViBigM(sublime_plugin.TextCommand):
    def run(self, edit, count=None, extend=False, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(target, target)
            elif mode == _MODE_INTERNAL_NORMAL:
                if s.b >= target:
                    return sublime.Region(s.a + 1, target)
                return sublime.Region(s.a, target)
            elif mode == MODE_VISUAL:
                if s.b >= target:
                    new_target = utils.next_non_white_space_char(view, target)
                    return sublime.Region(s.a + 1, new_target)
                new_target = utils.next_non_white_space_char(view, target)
                return sublime.Region(s.a, new_target + 1)
            else:
                return s

        r = self.view.visible_region()
        row_a, _ = self.view.rowcol(r.a)
        row_b, _ = self.view.rowcol(r.b)
        row = ((row_a + row_b) / 2)

        target = self.view.text_point(row, 0)

        regions_transformer(self.view, f)
        self.view.show(target)


class ViStar(ExactWordBufferSearchBase):
    def run(self, edit, mode=None, extend=False, exact_word=True):
        def f(view, s):
            pattern = self.build_pattern(query)
            flags = self.calculate_flags()

            if mode == _MODE_INTERNAL_NORMAL:
                match = find_wrapping(view,
                                      term=pattern,
                                      start=view.word(s.end()).end(),
                                      end=view.size(),
                                      flags=flags,
                                      times=1)
            else:
                match = find_wrapping(view,
                                      term=pattern,
                                      start=view.word(s.end()).end(),
                                      end=view.size(),
                                      flags=flags,
                                      times=1)

            if match:
                if mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.a, match.begin())
                elif state.mode == MODE_VISUAL:
                    return sublime.Region(s.a, match.begin())
                elif state.mode == MODE_NORMAL:
                    return sublime.Region(match.begin(), match.begin())
            return s

        state = VintageState(self.view)

        query = self.get_query()
        if query:
            self.hilite(query)
            # Ensure n and N can repeat this search later.
            state.last_buffer_search = self.build_pattern(query)

        regions_transformer(self.view, f)


class ViOctothorp(ExactWordBufferSearchBase):
    def run(self, edit, mode=None, extend=False, exact_word=True):
        def f(view, s):
            pattern = self.build_pattern(query)
            flags = self.calculate_flags()

            if mode == _MODE_INTERNAL_NORMAL:
                match = reverse_find_wrapping(view,
                                              term=pattern,
                                              start=0,
                                              end=start_sel.a,
                                              flags=flags,
                                              times=1)
            else:
                match = reverse_find_wrapping(view,
                                              term=pattern,
                                              start=0,
                                              end=start_sel.a,
                                              flags=flags,
                                              times=1)

            if match:
                if mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.b, match.begin())
                elif state.mode == MODE_VISUAL:
                    return sublime.Region(s.b, match.begin())
                elif state.mode == MODE_NORMAL:
                    return sublime.Region(match.begin(), match.begin())
            return s

        state = VintageState(self.view)

        query = self.get_query()
        if query:
            self.hilite(query)
            # Ensure n and N can repeat this search later.
            state.last_buffer_search = self.build_pattern(query)

        start_sel = self.view.sel()[0]
        regions_transformer(self.view, f)


class ViBufferSearch(IrreversibleTextCommand, BufferSearchBase):
    def run(self):
        Vintageous.state._dont_reset_during_init = True

        state = VintageState(self.view)
        on_change = self.on_change if state.settings.vi['incsearch'] else None

        self.view.window().show_input_panel('', '', self.on_done, on_change, self.on_cancel)

    def on_done(self, s):
        self.view.erase_regions('vi_inc_search')
        state = VintageState(self.view)
        state.motion = 'vi_forward_slash'

        # If s is empty, we must repeat the last search.

        # The next time we set .user_input, the vi_forward_slash input parser will kick in. We
        # therefore need to ensure we only set .user_input once.
        state.user_input = s or state.last_buffer_search
        state.last_buffer_search = s or state.last_buffer_search

        state.eval()

    def on_change(self, s):
        flags = self.calculate_flags()
        self.view.erase_regions('vi_inc_search')
        state = VintageState(self.view)
        next_hit = find_wrapping(self.view,
                                 term=s,
                                 start=self.view.sel()[0].b + 1,
                                 end=self.view.size(),
                                 flags=flags,
                                 times=state.count)
        if next_hit:
            if state.mode == MODE_VISUAL:
                next_hit = sublime.Region(self.view.sel()[0].a, next_hit.a + 1)

            self.view.add_regions('vi_inc_search', [next_hit], 'comment', '')
            if not self.view.visible_region().contains(next_hit.b):
                self.view.show(next_hit.b)

    def on_cancel(self):
        self.view.erase_regions('vi_inc_search')
        state = VintageState(self.view)
        state.reset()

        if not self.view.visible_region().contains(self.view.sel()[0]):
            self.view.show(self.view.sel()[0])


class ViBufferReverseSearch(IrreversibleTextCommand, BufferSearchBase):
    def run(self):
        Vintageous.state._dont_reset_during_init = True

        state = VintageState(self.view)
        on_change = self.on_change if state.settings.vi['incsearch'] else None
        self.view.window().show_input_panel('', '', self.on_done, on_change, self.on_cancel)

    def on_done(self, s):
        self.view.erase_regions('vi_inc_search')
        state = VintageState(self.view)
        state.motion = 'vi_question_mark'

        # If s is empty, we must repeat the last search.

        # The next time we set .user_input, the vi_question_mark input parser will kick in. We
        # therefore need to ensure we only set .user_input once.
        state.user_input = s or state.last_buffer_search
        state.last_buffer_search = s or state.last_buffer_search

        state.eval()

    def on_change(self, s):
        flags = self.calculate_flags()
        self.view.erase_regions('vi_inc_search')
        state = VintageState(self.view)
        occurrence = reverse_find_wrapping(self.view,
                                 term=s,
                                 start=0,
                                 end=self.view.sel()[0].b,
                                 flags=flags,
                                 times=state.count)
        if occurrence:
            if state.mode == MODE_VISUAL:
                occurrence = sublime.Region(self.view.sel()[0].a, occurrence.a)
            self.view.add_regions('vi_inc_search', [occurrence], 'comment', '')
            if not self.view.visible_region().contains(occurrence):
                self.view.show(occurrence)

    def on_cancel(self):
        self.view.erase_regions('vi_inc_search')
        state = VintageState(self.view)
        state.reset()

        if not self.view.visible_region().contains(self.view.sel()[0]):
            self.view.show(self.view.sel()[0])


class _vi_forward_slash(BufferSearchBase):
    def run(self, edit, search_string, mode=None, count=1, extend=False):
        def f(view, s):
            if mode == MODE_VISUAL:
                return sublime.Region(s.a, match.a + 1)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, match.a)

            elif mode == MODE_NORMAL:
                return sublime.Region(match.a, match.a)

            elif mode == MODE_VISUAL_LINE:
                return sublime.Region(s.a, view.full_line(match.b - 1).b)

            return s

        # This happens when we attempt to repeat the search and there's no search term stored yet.
        if search_string is None:
            return

        # We want to start searching right after the current selection.
        current_sel = self.view.sel()[0]
        start = current_sel.b if not current_sel.empty() else current_sel.b + 1
        wrapped_end = self.view.size()

        # TODO: What should we do here? Case-sensitive or case-insensitive search? Configurable?
        # Search wrapping around the end of the buffer.
        # flags = sublime.IGNORECASE | sublime.LITERAL
        flags = self.calculate_flags()
        match = find_wrapping(self.view, search_string, start, wrapped_end, flags=flags, times=count)
        if not match:
            return

        regions_transformer(self.view, f)
        self.hilite(search_string)


class _vi_question_mark(BufferSearchBase):
    def run(self, edit, search_string, mode=None, count=1, extend=False):
        def f(view, s):
            # FIXME: Readjust carets if we searched for '\n'.
            if mode == MODE_VISUAL:
                return sublime.Region(s.end(), found.a)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.end(), found.a)

            elif mode == MODE_NORMAL:
                return sublime.Region(found.a, found.a)

            elif mode == MODE_VISUAL_LINE:
                # FIXME: Ensure that the very first ? search excludes the current line.
                return sublime.Region(s.end(), view.full_line(found.a).a)

            return s

        # This happens when we attempt to repeat the search and there's no search term stored yet.
        if search_string is None:
            return

        flags = self.calculate_flags()
        # FIXME: What should we do here? Case-sensitive or case-insensitive search? Configurable?
        found = reverse_find_wrapping(self.view,
                                      term=search_string,
                                      start=0,
                                      end=self.view.sel()[0].b,
                                      flags=flags,
                                      times=count)

        if not found:
            print("Vintageous: Pattern not found.")
            return

        regions_transformer(self.view, f)
        self.hilite(search_string)


class _vi_right_brace(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            # TODO: must skip empty paragraphs.
            start = utils.next_non_white_space_char(view, s.b, white_space='\n \t')
            par_as_region = view.expand_by_class(start, sublime.CLASS_EMPTY_LINE)

            if mode == MODE_NORMAL:
                min_pt = max(0, min(par_as_region.b, view.size() - 1))
                return sublime.Region(min_pt, min_pt)

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a, par_as_region.b + 1)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, par_as_region.b - 1)

            elif mode == MODE_VISUAL_LINE:
                if s.a <= s.b:
                    return sublime.Region(s.a, par_as_region.b + 1)
                else:
                    if par_as_region.b > s.a:
                        return sublime.Region(view.line(s.a - 1).a, par_as_region.b + 1)
                    return sublime.Region(s.a, par_as_region.b)

            return s

        regions_transformer(self.view, f)


class _vi_left_brace(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            # TODO: must skip empty paragraphs.
            start = utils.previous_non_white_space_char(view, s.b - 1, white_space='\n \t')
            par_as_region = view.expand_by_class(start, sublime.CLASS_EMPTY_LINE)

            if mode == MODE_NORMAL:
                return sublime.Region(par_as_region.a, par_as_region.a)

            elif mode == MODE_VISUAL:
                # FIXME: Improve motion when .b end crosses over .a end: must extend .a end
                # by one.
                if s.a == par_as_region.a:
                    return sublime.Region(s.a, s.a + 1)
                return sublime.Region(s.a, par_as_region.a)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, par_as_region.a)

            elif mode == MODE_VISUAL_LINE:
                if s.a <= s.b:
                    if par_as_region.a < s.a:
                        return sublime.Region(view.full_line(s.a).b, par_as_region.a)
                    return sublime.Region(s.a, par_as_region.a + 1)
                else:
                    return sublime.Region(s.a, par_as_region.a)

            return s

        regions_transformer(self.view, f)


class _vi_right_parenthesis(sublime_plugin.TextCommand):
    def find_next_sentence_end(self, r):
        sen = r
        non_ws = utils.next_non_white_space_char(self.view, sen.b, '\t \n')
        sen = sublime.Region(non_ws, non_ws)
        while True:
            sen = self.view.expand_by_class(sen, sublime.CLASS_PUNCTUATION_START |
                                                 sublime.CLASS_LINE_END)
            if (sen.b == self.view.size() or
                self.view.substr(sublime.Region(sen.b, sen.b + 2)).endswith(('. ', '.\t')) or
                self.view.substr(self.view.line(sen.b)).strip() == ''):
                    if self.view.substr(sen.b) == '.':
                        return sublime.Region(sen.a, sen.b + 1)
                    else:
                        if self.view.line(sen.b).empty():
                            return sublime.Region(sen.a, sen.b)
                        else:
                            return self.view.full_line(sen.b)

    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            # TODO: must skip empty paragraphs.
            sen = self.find_next_sentence_end(s)

            if mode == MODE_NORMAL:
                target = min(sen.b, view.size() - 1)
                return sublime.Region(target, target)

            elif mode == MODE_VISUAL:
                # TODO: Must encompass new line char too?
                return sublime.Region(s.a, sen.b)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, sen.b)

            return s

        regions_transformer(self.view, f)


class _vi_left_parenthesis(sublime_plugin.TextCommand):
    def find_previous_sentence_end(self, r):
        sen = r
        pt = utils.previous_non_white_space_char(self.view, sen.a, white_space='\n \t')
        sen = sublime.Region(pt, pt)
        while True:
            sen = self.view.expand_by_class(sen, sublime.CLASS_LINE_END | sublime.CLASS_PUNCTUATION_END)
            if sen.a <= 0 or self.view.substr(sen.begin() - 1) in ('.', '\n'):
                if self.view.substr(sen.begin() - 1) == '.' and not self.view.substr(sen.begin()) == ' ':
                    continue
                return sen

    def run(self, edit, mode=None, extend=False):

        def f(view, s):
            # TODO: must skip empty paragraphs.
            sen = self.find_previous_sentence_end(s)

            if mode == MODE_NORMAL:
                return sublime.Region(sen.a, sen.a)

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a + 1, sen.a +  1)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, sen.a + 1)

            return s

        regions_transformer(self.view, f)


class _vi_go_to_symbol(sublime_plugin.TextCommand):
    """Go to local declaration. Differs from Vim because it leverages Sublime Text's ability to
       actually locate symbols (Vim simply searches from the top of the file).
    """
    def find_symbol(self, r, globally):
        query = self.view.substr(self.view.word(r))
        fname = self.view.file_name().replace('\\', '/')

        locations = self.view.window().lookup_symbol_in_index(query)
        if not locations:
            return

        try:
            if not globally:
                location = [hit[2] for hit in locations if fname.endswith(hit[1])][0]
                return location[0] - 1, location[1] - 1
            else:
                # TODO: There might be many symbols with the same name.
                return locations[0]
        except IndexError:
            return


    def run(self, edit, mode=None, extend=False, globally=False):

        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(location, location)

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a + 1, location)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, location)

            return s

        current_sel = self.view.sel()[0]
        self.view.sel().clear()
        self.view.sel().add(current_sel)

        location = self.find_symbol(current_sel, globally=globally)
        if not location:
            return

        if globally:
            # Global symbol; simply open the file; not a motion.
            # TODO: Perhaps must be a motion if the target file happens to be the current one?
            self.view.window().open_file(location[0] + ':' + ':'.join([str(x) for x in location[2]]), sublime.ENCODED_POSITION)
            return

        # Local symbol; select.
        location = self.view.text_point(*location)
        regions_transformer(self.view, f)


class _vi_double_single_quote(IrreversibleTextCommand):
    # (view_id, row) so we know where we stand.
    _latest_known_location = None
    next_command = 'jump_back'
    def run(self):
        # TODO: Long jumps are already recorded automatically, but if we press j many times, for
        # example, the current position won't be updated, and we'll jump back to unexpected
        # places.

        # We have jumped back before, but then we've moved rows, so we don't want to jump forward
        # any more.
        if (_vi_double_single_quote._latest_known_location and
            _vi_double_single_quote.next_command == 'jump_forward'):
                if (_vi_double_single_quote._latest_known_location !=
                     (self.view.view_id, self.view.rowcol(self.view.sel()[0].b)[0])):
                        _vi_double_single_quote.next_command = 'jump_back'

        # FIXME: Whenever there's a motion (any motion) after jumping back, we need to reset
        # this command to jumping back again. Otherwise the result will be confusing.
        # FIXME: We should create a jump entry at the current position.
        self.view.run_command(_vi_double_single_quote.next_command)

        if _vi_double_single_quote.next_command == 'jump_back':
            # Jumping back... Store the far location.
            _vi_double_single_quote._latest_known_location = (self.view.view_id, self.view.rowcol(self.view.sel()[0].b)[0])

        current = _vi_double_single_quote.next_command
        _vi_double_single_quote.next_command = 'jump_forward' if current == 'jump_back' else 'jump_back'


class _vi_pipe(sublime_plugin.TextCommand):
    def col_to_pt(self, pt, nr):
        if self.view.line(pt).size() < nr:
            return self.view.line(pt).b - 1

        row = self.view.rowcol(pt)[0]
        return self.view.text_point(row, nr) - 1

    def run(self, edit, mode=None, extend=False, count=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                pt = self.col_to_pt(pt=s.b, nr=count)
                return sublime.Region(pt, pt)

            elif mode == MODE_VISUAL:
                pt = self.col_to_pt(pt=s.b - 1, nr=count)
                if s.a < s.b:
                    if pt < s.a:
                        return sublime.Region(s.a + 1, pt)
                    else:
                        return sublime.Region(s.a, pt + 1)
                else:
                    if pt > s.a:
                        return sublime.Region(s.a - 1, pt + 1)
                    else:
                        return sublime.Region(s.a, pt)

            elif mode == _MODE_INTERNAL_NORMAL:
                pt = self.col_to_pt(pt=s.b, nr=count)
                if s.a < s.b:
                    return sublime.Region(s.a, pt)
                else:
                    return sublime.Region(s.a + 1, pt)

            return s

        regions_transformer(self.view, f)


class _vi_shift_enter_post_motion(sublime_plugin.TextCommand):
    def first_non_white_space_char(self, where):
        start = self.view.text_point(self.view.rowcol(where)[0], 0)
        pt = utils.next_non_white_space_char(self.view, start, white_space=' \t')
        return pt

    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            if mode == MODE_NORMAL:
                pt = self.first_non_white_space_char(s.b)
                pt = min((pt, self.view.line(pt).b))
                return sublime.Region(pt, pt)

            elif mode == MODE_VISUAL:
                pt = self.first_non_white_space_char(s.b)
                return sublime.Region(s.a, pt)

            elif mode == _MODE_INTERNAL_NORMAL:
                # Same as dj, dk delete two entire lines, here we do a similar thing.
                return sublime.Region(s.a, self.view.line(s.b).a)

            return s

        regions_transformer(self.view, f)


class _vi_g_e_pre_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            if mode == MODE_NORMAL:
                pass

            elif mode == MODE_VISUAL:
                if s.a < s.b:
                    if s.size() == 1:
                        return sublime.Region(s.b, s.a)
                else:
                    pass


            elif mode == _MODE_INTERNAL_NORMAL:
                pass

            return s

        regions_transformer(self.view, f)


class _vi_g_e_post_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            if mode == MODE_NORMAL:
                pass

            elif mode == MODE_VISUAL:
                if s.a > s.b:
                    return sublime.Region(s.a, s.b - 1)


            elif mode == _MODE_INTERNAL_NORMAL:
                pass

            return s

        regions_transformer(self.view, f)


class _vi_ctrl_d(sublime_plugin.TextCommand):
    def next_half_page(self, count):

        origin = self.view.sel()[0]

        visible = self.view.visible_region()
        row_a = self.view.rowcol(visible.a)[0]
        row_b = self.view.rowcol(visible.b)[0]

        half_page_span = (row_b - row_a) // 2 * count

        next_half_page = self.view.rowcol(origin.b)[0] + half_page_span

        pt = self.view.text_point(next_half_page, 0)
        return sublime.Region(pt, pt), (self.view.rowcol(pt)[0] -
                                        self.view.rowcol(visible.a)[0])

    def run(self, edit, mode=None, extend=False, count=None):

        def f(view, s):
            if mode == MODE_NORMAL:
                return next

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a, next.b)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, next.b)

            elif mode == MODE_VISUAL_LINE:
                return sublime.Region(s.a, self.view.full_line(next.b).b)

            return s

        next, scroll_amount = self.next_half_page(count)
        regions_transformer(self.view, f)


class _vi_ctrl_u(sublime_plugin.TextCommand):
    def prev_half_page(self, count):

        origin = self.view.sel()[0]

        visible = self.view.visible_region()
        row_a = self.view.rowcol(visible.a)[0]
        row_b = self.view.rowcol(visible.b)[0]

        half_page_span = (row_b - row_a) // 2 * count

        prev_half_page = self.view.rowcol(origin.b)[0] - half_page_span

        pt = self.view.text_point(prev_half_page, 0)
        return sublime.Region(pt, pt), (self.view.rowcol(visible.b)[0] -
                                        self.view.rowcol(pt)[0])

    def run(self, edit, mode=None, extend=False, count=None):

        def f(view, s):
            if mode == MODE_NORMAL:
                return previous

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a, previous.b)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, previous.b)

            elif mode == MODE_VISUAL_LINE:
                return sublime.Region(s.a, self.view.full_line(previous.b).b)

            return s

        previous, scroll_amount = self.prev_half_page(count)
        regions_transformer(self.view, f)


class _vi_g__(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                eol = view.line(s.b).b
                return sublime.Region(eol - 1, eol - 1)

            elif mode == MODE_VISUAL:
                eol = view.line(s.b - 1).b
                return sublime.Region(s.a, eol)

            elif mode == _MODE_INTERNAL_NORMAL:
                eol = view.line(s.b).b
                return sublime.Region(s.a, eol)

            return s

        regions_transformer(self.view, f)


class _vi_big_g(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                pt = eof
                if not view.line(eof).empty():
                    pt = utils.previous_non_white_space_char(view, eof - 1,
                                                         white_space='\n')
                return sublime.Region(pt, pt)

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a, eof)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, eof)

            elif mode == MODE_VISUAL_LINE:
                return sublime.Region(s.a, eof)

            return s

        eof = self.view.size()
        regions_transformer(self.view, f)


class _vi_dollar(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                if count > 1:
                    pt = view.line(target_row_pt).b
                else:
                    pt = view.line(s.b).b
                if not view.line(pt).empty():
                    return sublime.Region(pt - 1, pt - 1)
                return sublime.Region(pt, pt)

            elif mode == MODE_VISUAL:
                current_line_pt = (s.b - 1) if (s.a < s.b) else s.b
                if count > 1:
                    end = view.full_line(target_row_pt).b
                else:
                    end = s.end()
                    if not end == view.full_line(s.b - 1).b:
                        end = view.full_line(s.b).b
                end = end if (s.a < end) else (end - 1)
                start = s.a if ((s.a < s.b) or (end < s.a)) else s.a - 1
                return sublime.Region(start, end)

            elif mode == _MODE_INTERNAL_NORMAL:
                if count > 1:
                    pt = view.line(target_row_pt).b
                else:
                    pt = view.line(s.b).b
                if count == 1:
                    return sublime.Region(s.a, pt)
                return sublime.Region(s.a, pt + 1)

            elif mode == MODE_VISUAL_LINE:
                # TODO: Implement this. Not too useful, though.
                return s

            return s

        sel = self.view.sel()[0]
        target_row_pt = (sel.b - 1) if (sel.b > sel.a) else sel.b
        if count > 1:
            current_row = self.view.rowcol(target_row_pt)[0]
            target_row = current_row + count - 1
            target_row_pt = self.view.text_point(target_row, 0)

        regions_transformer(self.view, f)


class _vi_cc_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=1):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                if count == 1:
                    return view.line(s.b)
                row, _ = view.rowcol(s.b)
                target_line = view.text_point(row + count - 1, 0)
                return sublime.Region(view.line(s.b).a, view.line(target_line).b)
            return s

        regions_transformer(self.view, f)


class _vi_big_s_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=1):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                if count == 1:
                    line = view.line(s.b)
                    if not view.substr(line).strip():
                        return s
                    return line
                row, _ = view.rowcol(s.b)
                target_line = view.text_point(row + count - 1, 0)
                return sublime.Region(view.line(s.b).a, view.line(target_line).b)
            return s

        regions_transformer(self.view, f)


class _vi_w(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=1):
        def f(view, s):
            if mode == MODE_NORMAL:
                pt = units.word_starts(view, start=s.b, count=count)
                if ((pt == view.size()) and (not view.line(pt).empty())):
                    pt = utils.previous_non_white_space_char(view, pt - 1,
                                                            white_space='\n')
                return sublime.Region(pt, pt)
            elif mode == MODE_VISUAL:
                pt = units.word_starts(view, start=s.b - 1, count=count)
                if s.a > s.b and pt >= s.a:
                    return sublime.Region(s.a - 1, pt + 1)
                elif s.a > s.b:
                    return sublime.Region(s.a, pt)
                elif (view.size() == pt):
                    pt -= 1
                return sublime.Region(s.a, pt + 1)
            elif mode == _MODE_INTERNAL_NORMAL:
                a = s.a
                pt = units.word_starts(view, start=s.b, count=count, internal=True)
                if (not view.substr(view.line(s.a)).strip() and
                    (view.line(s.b) != view.line(pt))):
                        a = view.line(s.a).a
                return sublime.Region(a, pt)
            return s

        regions_transformer(self.view, f)


class _vi_big_w(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=1):
        def f(view, s):
            if mode == MODE_NORMAL:
                pt = units.big_word_starts(view, start=s.b, count=count)
                if ((pt == view.size()) and (not view.line(pt).empty())):
                    pt = utils.previous_non_white_space_char(view, pt - 1,
                                                            white_space='\n')
                return sublime.Region(pt, pt)
            elif mode == MODE_VISUAL:
                pt = units.big_word_starts(view, start=s.b - 1, count=count)
                if s.a > s.b and pt >= s.a:
                    return sublime.Region(s.a - 1, pt + 1)
                elif s.a > s.b:
                    return sublime.Region(s.a, pt)
                elif (view.size() == pt):
                    pt -= 1
                return sublime.Region(s.a, pt + 1)
            elif mode == _MODE_INTERNAL_NORMAL:
                a = s.a
                pt = units.big_word_starts(view, start=s.b, count=count, internal=True)
                if (not view.substr(view.line(s.a)).strip() and
                    (view.line(s.b) != view.line(pt))):
                        a = view.line(s.a).a
                return sublime.Region(a, pt)
            return s

        regions_transformer(self.view, f)


class _vi_e(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=1):
        def f(view, s):
            if mode == MODE_NORMAL:
                pt = units.word_ends(view, start=s.b, count=count)

                if (view.substr(pt) == '\n' and not view.line(pt).empty()):
                    return sublime.Region(pt - 1, pt - 1)
                elif (view.line(pt).empty()):
                    return s

                return sublime.Region(pt, pt)
            elif mode == MODE_VISUAL:
                pt = units.word_ends(view, start=s.b - 1, count=count)
                if s.a > s.b and pt >= s.a:
                    return sublime.Region(s.a - 1, pt + 1)
                elif s.a > s.b:
                    return sublime.Region(s.a, pt)
                elif (view.size() == pt):
                    pt -= 1
                return sublime.Region(s.a, pt + 1)
            elif mode == _MODE_INTERNAL_NORMAL:
                a = s.a
                pt = units.word_ends(view, start=s.b, count=count, internal=True)
                if (not view.substr(view.line(s.a)).strip() and
                    (view.line(s.b) != view.line(pt))):
                        a = view.line(s.a).a
                return sublime.Region(a, pt + 1)
            return s

        regions_transformer(self.view, f)
