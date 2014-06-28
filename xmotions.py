# TODO: weird name to avoid init issues with state.py::State.

import sublime
import sublime_plugin

from itertools import chain
from collections import Counter


from Vintageous import state as state_module
from Vintageous.vi import units
from Vintageous.vi import utils
from Vintageous.vi.core import ViMotionCommand
from Vintageous.vi.keys import mappings
from Vintageous.vi.keys import seqs
from Vintageous.vi.search import BufferSearchBase
from Vintageous.vi.search import ExactWordBufferSearchBase
from Vintageous.vi.search import find_in_range
from Vintageous.vi.search import find_wrapping
from Vintageous.vi.search import reverse_find_wrapping
from Vintageous.vi.search import reverse_search
from Vintageous.vi.search import reverse_search_by_pt
from Vintageous.state import State
from Vintageous.vi.text_objects import get_text_object_region
from Vintageous.vi.utils import col_at
from Vintageous.vi.utils import directions
from Vintageous.vi.utils import IrreversibleTextCommand
from Vintageous.vi.utils import modes
from Vintageous.vi.utils import regions_transformer
from Vintageous.vi.utils import mark_as_widget
from Vintageous.vi import cmd_defs
from Vintageous.vi.text_objects import word_reverse
from Vintageous.vi.text_objects import word_end_reverse
from Vintageous.vi.text_objects import get_closest_tag
from Vintageous.vi.text_objects import find_containing_tag
from Vintageous.vi.text_objects import find_prev_lone_bracket
from Vintageous.vi.text_objects import find_next_lone_bracket


class _vi_find_in_line(ViMotionCommand):
    """
    Contrary to *f*, *t* does not look past the caret's position, so if
    @character is under the caret, nothing happens.
    """
    def run(self, char=None, mode=None, count=1, inclusive=True):
        def f(view, s):
            if mode == modes.VISUAL_LINE:
                raise ValueError(
                    'this operator is not valid in mode {}'.format(mode))

            b = s.b
            # If we are in any visual mode, get the actual insertion point.
            if s.size() > 0:
                b = utils.get_caret_pos_at_b(s)

            eol = view.line(b).end()

            match = sublime.Region(b + 1)
            for i in range(count):
                # Define search range as 'rest of the line to the right'.
                search_range = sublime.Region(match.end(), eol)
                match = find_in_range(view, char,
                                            search_range.a,
                                            search_range.b,
                                            sublime.LITERAL)

                # Count too high or simply no match; break.
                if match is None:
                    return s

            target_pos = match.a
            if not inclusive:
                target_pos = target_pos - 1

            if mode == modes.NORMAL:
                return sublime.Region(target_pos)
            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, target_pos + 1)
            # For visual modes...
            else:
                new_a = utils.get_caret_pos_at_a(s)
                return utils.new_inclusive_region(new_a, target_pos)

        if not all([char, mode]):
            print('char', char, 'mode', mode)
            raise ValueError('bad parameters')

        char = utils.translate_char(char)

        state = self.state

        regions_transformer(self.view, f)


class _vi_reverse_find_in_line(ViMotionCommand):
    """Contrary to *F*, *T* does not look past the caret's position, so if ``character`` is right
       before the caret, nothing happens.
    """
    def run(self, char=None, mode=None, count=1, inclusive=True):
        def f(view, s):
            if mode == modes.VISUAL_LINE:
                raise ValueError(
                    'this operator is not valid in mode {}'.format(mode))

            b = s.b
            if s.size() > 0:
                b = utils.get_caret_pos_at_b(s)

            line_start = view.line(b).a

            try:
                match = b
                for i in range(count):
                    # line_text does not include character at match
                    line_text = view.substr(sublime.Region(line_start, match))
                    found_at = line_text.rindex(char)
                    match = line_start + found_at
            except ValueError:
                return s

            target_pos = match
            if not inclusive:
                target_pos = target_pos + 1

            if mode == modes.NORMAL:
                return sublime.Region(target_pos)
            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(b, target_pos)
            # For visual modes...
            else:
                new_a = utils.get_caret_pos_at_a(s)
                return utils.new_inclusive_region(new_a, target_pos)

        if not all([char, mode]):
            raise ValueError('bad parameters')

        char = utils.translate_char(char)

        state = self.state
        regions_transformer(self.view, f)


class _vi_slash(ViMotionCommand, BufferSearchBase):
    """
    Collects input for the / motion.
    """
    def run(self, default=''):
        self.state.reset_during_init = False

        # TODO: re-enable this.
        # on_change = self.on_change if state.settings.vi['incsearch'] else None
        on_change = self.on_change

        mark_as_widget(self.view.window().show_input_panel(
                                                            '',
                                                            default,
                                                            self.on_done,
                                                            on_change,
                                                            self.on_cancel))

    def on_done(self, s):
        state = self.state
        state.sequence += s + '<CR>'
        self.view.erase_regions('vi_inc_search')
        state.motion = cmd_defs.ViSearchForwardImpl(term=s)

        # If s is empty, we must repeat the last search.
        state.last_buffer_search = s or state.last_buffer_search
        state.eval()

    def on_change(self, s):
        state = self.state
        flags = self.calculate_flags()
        self.view.erase_regions('vi_inc_search')
        next_hit = find_wrapping(self.view,
                                 term=s,
                                 start=self.view.sel()[0].b + 1,
                                 end=self.view.size(),
                                 flags=flags,
                                 times=state.count)
        if next_hit:
            if state.mode == modes.VISUAL:
                next_hit = sublime.Region(self.view.sel()[0].a, next_hit.a + 1)

            self.view.add_regions('vi_inc_search', [next_hit], 'comment', '')
            if not self.view.visible_region().contains(next_hit.b):
                self.view.show(next_hit.b)

    def on_cancel(self):
        state = self.state
        self.view.erase_regions('vi_inc_search')
        state.reset_command_data()

        if not self.view.visible_region().contains(self.view.sel()[0]):
            self.view.show(self.view.sel()[0])


class _vi_slash_impl(ViMotionCommand, BufferSearchBase):
    def run(self, search_string='', mode=None, count=1):
        def f(view, s):
            if mode == modes.VISUAL:
                return sublime.Region(s.a, match.a + 1)

            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, match.a)

            elif mode == modes.NORMAL:
                return sublime.Region(match.a, match.a)

            elif mode == modes.VISUAL_LINE:
                return sublime.Region(s.a, view.full_line(match.b - 1).b)

            return s

        # This happens when we attempt to repeat the search and there's no search term stored yet.
        if not search_string:
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



class _vi_l(ViMotionCommand):
    def run(self, mode=None, count=None):
        def f(view, s):
            if mode == modes.NORMAL:
                if view.line(s.b).empty():
                    return s

                x_limit = min(view.line(s.b).b - 1, s.b + count, view.size())
                return sublime.Region(x_limit, x_limit)

            if mode == modes.INTERNAL_NORMAL:
                x_limit = min(view.line(s.b).b, s.b + count)
                x_limit = max(0, x_limit)
                return sublime.Region(s.a, x_limit)

            if mode in (modes.VISUAL, modes.VISUAL_BLOCK):
                if s.a < s.b:
                    x_limit = min(view.full_line(s.b - 1).b, s.b + count)
                    return sublime.Region(s.a, x_limit)

                if s.a > s.b:
                    x_limit = min(view.full_line(s.b).b - 1, s.b + count)
                    if view.substr(s.b) == '\n':
                        return s

                    if view.line(s.a) == view.line(s.b) and count >= s.size():
                        x_limit = min(view.full_line(s.b).b, s.b + count + 1)
                        return sublime.Region(s.a - 1, x_limit)

                    return sublime.Region(s.a, x_limit)

            return s

        regions_transformer(self.view, f)
        state = self.state
        # state.xpos = self.view.rowcol(self.view.sel()[0].b)[1]


class _vi_h(ViMotionCommand):
    def run(self, count=1, mode=None):
        def f(view, s):
            if mode == modes.INTERNAL_NORMAL:
                x_limit = max(view.line(s.b).a, s.b - count)
                return sublime.Region(s.a, x_limit)

            # TODO: Split handling of the two modes for clarity.
            elif mode in (modes.VISUAL, modes.VISUAL_BLOCK):

                if s.a < s.b:
                    if mode == modes.VISUAL_BLOCK and self.view.rowcol(s.b - 1)[1] == baseline:
                        return s

                    x_limit = max(view.line(s.b - 1).a + 1, s.b - count)
                    if view.line(s.a) == view.line(s.b - 1) and count >= s.size():
                        x_limit = max(view.line(s.b - 1).a, s.b - count - 1)
                        return sublime.Region(s.a + 1, x_limit)
                    return sublime.Region(s.a, x_limit)

                if s.a > s.b:
                    x_limit = max(view.line(s.b).a, s.b - count)
                    return sublime.Region(s.a, x_limit)

            elif mode == modes.NORMAL:
                x_limit = max(view.line(s.b).a, s.b - count)
                return sublime.Region(x_limit, x_limit)

            # XXX: We should never reach this.
            return s

        # For jagged selections (on the rhs), only those sticking out need to move leftwards.
        # Example ([] denotes the selection):
        #
        #   10 foo bar foo [bar]
        #   11 foo bar foo [bar foo bar]
        #   12 foo bar foo [bar foo]
        #
        #  Only lines 11 and 12 should move when we press h.
        baseline = 0
        if mode == modes.VISUAL_BLOCK:
            sel = self.view.sel()[0]
            if sel.a < sel.b:
                min_ = min(self.view.rowcol(r.b - 1)[1] for r in self.view.sel())
                if any(self.view.rowcol(r.b - 1)[1] != min_ for r in self.view.sel()):
                    baseline = min_

        regions_transformer(self.view, f)
        state = self.state
        # state.xpos = self.view.rowcol(self.view.sel()[0].b)[1]


class _vi_j(ViMotionCommand):
    def folded_rows(self, pt):
        folds = self.view.folded_regions()
        try:
            fold = [f for f in folds if f.contains(pt)][0]
            fold_row_a = self.view.rowcol(fold.a)[0]
            fold_row_b = self.view.rowcol(fold.b - 1)[0]
            # Return no. of hidden lines.
            return (fold_row_b - fold_row_a)
        except IndexError:
            return 0

    def next_non_folded_pt(self, pt):
        # FIXME: If we have two contiguous folds, this method will fail.
        # Handle folded regions.
        folds = self.view.folded_regions()
        try:
            fold = [f for f in folds if f.contains(pt)][0]
            non_folded_row = self.view.rowcol(self.view.full_line(fold.b).b)[0]
            pt = self.view.text_point(non_folded_row, 0)
        except IndexError:
            pass
        return pt

    def calculate_xpos(self, start, xpos):
        size = self.view.settings().get('tab_size')
        if self.view.line(start).empty():
            return start, 0
        else:
            eol = self.view.line(start).b - 1
        pt = 0
        chars = 0
        while (pt < xpos):
            if self.view.substr(start + chars) == '\t':
                pt += size
            else:
                pt += 1
            chars += 1
        pt = min(eol, start + chars)
        return pt, chars

    def run(self, count=1, mode=None, xpos=0, no_translation=False):
        def f(view, s):
            nonlocal xpos
            if mode == modes.NORMAL:
                current_row = view.rowcol(s.b)[0]
                target_row = min(current_row + count, view.rowcol(view.size())[0])
                invisible_rows = self.folded_rows(view.line(s.b).b + 1)
                target_pt = view.text_point(target_row + invisible_rows, 0)
                target_pt = self.next_non_folded_pt(target_pt)

                if view.line(target_pt).empty():
                    return sublime.Region(target_pt, target_pt)

                pt = self.calculate_xpos(target_pt, xpos)[0]
                return sublime.Region(pt)

            if mode == modes.INTERNAL_NORMAL:
                current_row = view.rowcol(s.b)[0]
                target_row = min(current_row + count, view.rowcol(view.size())[0])
                target_pt = view.text_point(target_row, 0)
                return sublime.Region(view.line(s.a).a, view.full_line(target_pt).b)

            if mode == modes.VISUAL:
                exact_position = s.b - 1 if (s.a < s.b) else s.b
                current_row = view.rowcol(exact_position)[0]
                target_row = min(current_row + count, view.rowcol(view.size())[0])
                target_pt = view.text_point(target_row, 0)
                _, xpos = self.calculate_xpos(target_pt, xpos)

                end = min(self.view.line(target_pt).b, target_pt + xpos)
                if s.a < s.b:
                    return sublime.Region(s.a, end + 1)

                if (target_pt + xpos) >= s.a:
                    return sublime.Region(s.a - 1, end + 1)
                return sublime.Region(s.a, target_pt + xpos)


            if mode == modes.VISUAL_LINE:
                if s.a < s.b:
                    current_row = view.rowcol(s.b - 1)[0]
                    target_row = min(current_row + count, view.rowcol(view.size())[0])

                    target_pt = view.text_point(target_row, 0)
                    return sublime.Region(s.a, view.full_line(target_pt).b)

                elif s.a > s.b:
                    current_row = view.rowcol(s.b)[0]
                    target_row = min(current_row + count, view.rowcol(view.size())[0])
                    target_pt = view.text_point(target_row, 0)

                    if target_row > view.rowcol(s.a - 1)[0]:
                        return sublime.Region(view.line(s.a - 1).a, view.full_line(target_pt).b)

                    return sublime.Region(s.a, view.full_line(target_pt).a)

            return s

        state = State(self.view)

        if mode == modes.VISUAL_BLOCK:
            if len(self.view.sel()) == 1:
                state.visual_block_direction = directions.DOWN

            # Don't do anything if we have reversed selections.
            if any((r.b < r.a) for r in self.view.sel()):
                return

            if state.visual_block_direction == directions.DOWN:
                for i in range(count):
                    # FIXME: When there are multiple rectangular selections, S3 considers sel 0 to be the
                    # active one in all cases, so we can't know the 'direction' of such a selection and,
                    # therefore, we can't shrink it when we press k or j. We can only easily expand it.
                    # We could, however, have some more global state to keep track of the direction of
                    # visual block selections.
                    row, rect_b = self.view.rowcol(self.view.sel()[-1].b - 1)

                    # Don't do anything if the next row is empty or too short. Vim does a crazy thing: it
                    # doesn't select it and it doesn't include it in actions, but you have to still navigate
                    # your way through them.
                    # TODO: Match Vim's behavior.
                    next_line = self.view.line(self.view.text_point(row + 1, 0))
                    if next_line.empty() or self.view.rowcol(next_line.b)[1] < rect_b:
                        return

                    max_size = max(r.size() for r in self.view.sel())
                    row, col = self.view.rowcol(self.view.sel()[-1].a)
                    start = self.view.text_point(row + 1, col)
                    new_region = sublime.Region(start, start + max_size)
                    self.view.sel().add(new_region)
                    # FIXME: Perhaps we should scroll into view in a more general way...

                self.view.show(new_region, False)
                return

            else:
                # Must delete last sel.
                self.view.sel().subtract(self.view.sel()[0])
                return

        regions_transformer(self.view, f)


class _vi_k(ViMotionCommand):
    def previous_non_folded_pt(self, pt):
        # FIXME: If we have two contiguous folds, this method will fail.
        # Handle folded regions.
        folds = self.view.folded_regions()
        try:
            fold = [f for f in folds if f.contains(pt)][0]
            non_folded_row = self.view.rowcol(fold.a - 1)[0]
            pt = self.view.text_point(non_folded_row, 0)
        except IndexError:
            pass
        return pt

    def calculate_xpos(self, start, xpos):
        if self.view.line(start).empty():
            return start, 0
        size = self.view.settings().get('tab_size')
        eol = self.view.line(start).b - 1
        pt = 0
        chars = 0
        while (pt < xpos):
            if self.view.substr(start + chars) == '\t':
                pt += size
            else:
                pt += 1
            chars += 1
        pt = min(eol, start + chars)
        return (pt, chars)

    def run(self, count=1, mode=None, xpos=0, no_translation=False):
        def f(view, s):
            nonlocal xpos
            if mode == modes.NORMAL:
                current_row = view.rowcol(s.b)[0]
                target_row = min(current_row - count, view.rowcol(view.size())[0])
                target_pt = view.text_point(target_row, 0)
                target_pt = self.previous_non_folded_pt(target_pt)

                if view.line(target_pt).empty():
                    return sublime.Region(target_pt, target_pt)

                pt, _ = self.calculate_xpos(target_pt, xpos)
                return sublime.Region(pt)

            if mode == modes.INTERNAL_NORMAL:
                current_row = view.rowcol(s.b)[0]
                target_row = min(current_row - count, view.rowcol(view.size())[0])
                target_pt = view.text_point(target_row, 0)
                return sublime.Region(view.full_line(s.a).b, view.line(target_pt).a)

            if mode == modes.VISUAL:
                exact_position = s.b - 1 if (s.a < s.b) else s.b
                current_row = view.rowcol(exact_position)[0]
                target_row = max(current_row - count, 0)
                target_pt = view.text_point(target_row, 0)
                _, xpos = self.calculate_xpos(target_pt, xpos)

                end = min(self.view.line(target_pt).b, target_pt + xpos)
                if s.b >= s.a:
                    if (self.view.line(s.a).contains(s.b - 1) and
                        not self.view.line(s.a).contains(target_pt)):
                            return sublime.Region(s.a + 1, end)
                    else:
                        if (target_pt + xpos) < s.a:
                            return sublime.Region(s.a + 1, end)
                        else:
                            return sublime.Region(s.a, end + 1)
                return sublime.Region(s.a, end)

            if mode == modes.VISUAL_LINE:
                if s.a < s.b:
                    current_row = view.rowcol(s.b - 1)[0]
                    target_row = min(current_row - count, view.rowcol(view.size())[0])
                    target_pt = view.text_point(target_row, 0)

                    if target_row < view.rowcol(s.begin())[0]:
                        return sublime.Region(view.full_line(s.a).b, view.full_line(target_pt).a)

                    return sublime.Region(s.a, view.full_line(target_pt).b)

                elif s.a > s.b:
                    current_row = view.rowcol(s.b)[0]
                    target_row = max(current_row - count, 0)
                    target_pt = view.text_point(target_row, 0)

                    return sublime.Region(s.a, view.full_line(target_pt).a)

        state = State(self.view)

        if mode == modes.VISUAL_BLOCK:
            if len(self.view.sel()) == 1:
                state.visual_block_direction = directions.UP

            # Don't do anything if we have reversed selections.
            if any((r.b < r.a) for r in self.view.sel()):
                return

            if state.visual_block_direction == directions.UP:

                for i in range(count):
                    rect_b = max(self.view.rowcol(r.b - 1)[1] for r in self.view.sel())
                    row, rect_a = self.view.rowcol(self.view.sel()[0].a)
                    previous_line = self.view.line(self.view.text_point(row - 1, 0))
                    # Don't do anything if previous row is empty. Vim does crazy stuff in that case.
                    # Don't do anything either if the previous line can't accomodate a rectangular selection
                    # of the required size.
                    if (previous_line.empty() or
                        self.view.rowcol(previous_line.b)[1] < rect_b):
                            return
                    rect_size = max(r.size() for r in self.view.sel())
                    rect_a_pt = self.view.text_point(row - 1, rect_a)
                    new_region = sublime.Region(rect_a_pt, rect_a_pt + rect_size)
                    self.view.sel().add(new_region)
                    # FIXME: We should probably scroll into view in a more general way.
                    #        Or maybe every motion should handle this on their own.

                self.view.show(new_region, False)
                return

            elif modes.SELECT:
                # Must remove last selection.
                self.view.sel().subtract(self.view.sel()[-1])
                return
            else:
                return

        regions_transformer(self.view, f)


class _vi_k_select(ViMotionCommand):
    def run(self, count=1, mode=None):
        # FIXME: It isn't working.
        if mode != modes.SELECT:
            utils.blink()
            return

        for i in range(count):
            self.view.window().run_command('soft_undo')
            return


class _vi_gg(ViMotionCommand):
    def run(self, mode=None, count=1):
        def f(view, s):
            if mode == modes.NORMAL:
                return sublime.Region(0)
            elif mode == modes.VISUAL:
                if s.a < s.b:
                    return sublime.Region(s.a + 1, 0)
                else:
                    return sublime.Region(s.a, 0)
            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(view.full_line(s.b).b, 0)
            elif mode == modes.VISUAL_LINE:
                if s.a < s.b:
                    return sublime.Region(0, s.b)
                else:
                    return sublime.Region(0, s.a)
            return s

        self.view.window().run_command('_vi_add_to_jump_list')
        regions_transformer(self.view, f)
        self.view.window().run_command('_vi_add_to_jump_list')


class _vi_go_to_line(ViMotionCommand):
    def run(self, line=None, mode=None):
        line = line if line > 0 else 1
        dest = self.view.text_point(line - 1, 0)

        def f(view, s):
            if mode == modes.NORMAL:
                non_ws = utils.next_non_white_space_char(view, dest)
                return sublime.Region(non_ws, non_ws)
            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(view.line(s.a).a, view.line(dest).b)
            elif mode == modes.VISUAL:
                if dest < s.a and s.a < s.b:
                    return sublime.Region(s.a + 1, dest)
                elif dest < s.a:
                    return sublime.Region(s.a, dest)
                elif dest > s.b and s.a > s.b:
                    return sublime.Region(s.a - 1, dest + 1)
                return sublime.Region(s.a, dest + 1)
            elif mode == modes.VISUAL_LINE:
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


class _vi_big_g(ViMotionCommand):
    def run(self, mode=None, count=None):
        def f(view, s):
            if mode == modes.NORMAL:
                pt = eof
                if not view.line(eof).empty():
                    pt = utils.previous_non_white_space_char(view, eof - 1,
                                                         white_space='\n')
                return sublime.Region(pt, pt)
            elif mode == modes.VISUAL:
                return sublime.Region(s.a, eof)
            elif mode == modes.INTERNAL_NORMAL:
                begin = view.line(s.b).a
                begin = max(0, begin - 1)
                return sublime.Region(begin, eof)
            elif mode == modes.VISUAL_LINE:
                return sublime.Region(s.a, eof)

            return s

        self.view.window().run_command('_vi_add_to_jump_list')
        eof = self.view.size()
        regions_transformer(self.view, f)
        self.view.window().run_command('_vi_add_to_jump_list')


class _vi_dollar(ViMotionCommand):
    def run(self, mode=None, count=1):
        def f(view, s):
            if mode == modes.NORMAL:
                if count > 1:
                    pt = view.line(target_row_pt).b
                else:
                    pt = view.line(s.b).b
                if not view.line(pt).empty():
                    return sublime.Region(pt - 1, pt - 1)
                return sublime.Region(pt, pt)

            elif mode == modes.VISUAL:
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

            elif mode == modes.INTERNAL_NORMAL:
                if count > 1:
                    pt = view.line(target_row_pt).b
                else:
                    pt = view.line(s.b).b
                if count == 1:
                    return sublime.Region(s.a, pt)
                return sublime.Region(s.a, pt + 1)

            elif mode == modes.VISUAL_LINE:
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


class _vi_w(ViMotionCommand):
    def run(self, mode=None, count=1):
        def f(view, s):
            if mode == modes.NORMAL:
                pt = units.word_starts(view, start=s.b, count=count)
                if ((pt == view.size()) and (not view.line(pt).empty())):
                    pt = utils.previous_non_white_space_char(view, pt - 1,
                                                             white_space='\n')
                return sublime.Region(pt, pt)

            elif mode in (modes.VISUAL, modes.VISUAL_BLOCK):
                start = (s.b - 1) if (s.a < s.b) else s.b
                pt = units.word_starts(view, start=start, count=count)

                if (s.a > s.b) and (pt >= s.a):
                    return sublime.Region(s.a - 1, pt + 1)
                elif s.a > s.b:
                    return sublime.Region(s.a, pt)
                elif view.size() == pt:
                    pt -= 1
                return sublime.Region(s.a, pt + 1)

            elif mode == modes.INTERNAL_NORMAL:
                a = s.a
                pt = units.word_starts(view, start=s.b, count=count,
                                       internal=True)
                if (not view.substr(view.line(s.a)).strip() and
                   view.line(s.b) != view.line(pt)):
                        a = view.line(s.a).a
                return sublime.Region(a, pt)

            return s

        regions_transformer(self.view, f)


class _vi_big_w(ViMotionCommand):
    def run(self, mode=None, count=1):
        def f(view, s):
            if mode == modes.NORMAL:
                pt = units.big_word_starts(view, start=s.b, count=count)
                if ((pt == view.size()) and (not view.line(pt).empty())):
                    pt = utils.previous_non_white_space_char(view, pt - 1,
                                                             white_space='\n')
                return sublime.Region(pt, pt)

            elif mode == modes.VISUAL:
                pt = units.big_word_starts(view, start=s.b - 1, count=count)
                if s.a > s.b and pt >= s.a:
                    return sublime.Region(s.a - 1, pt + 1)
                elif s.a > s.b:
                    return sublime.Region(s.a, pt)
                elif (view.size() == pt):
                    pt -= 1
                return sublime.Region(s.a, pt + 1)

            elif mode == modes.INTERNAL_NORMAL:
                a = s.a
                pt = units.big_word_starts(view,
                                           start=s.b,
                                           count=count,
                                           internal=True)
                if (not view.substr(view.line(s.a)).strip() and
                   view.line(s.b) != view.line(pt)):
                        a = view.line(s.a).a
                return sublime.Region(a, pt)

            return s

        regions_transformer(self.view, f)


class _vi_e(ViMotionCommand):
    def run(self, mode=None, count=1):
        def f(view, s):
            if mode == modes.NORMAL:
                pt = units.word_ends(view, start=s.b, count=count)
                return sublime.Region(pt - 1)

            elif mode == modes.VISUAL:
                pt = units.word_ends(view, start=s.b - 1, count=count)
                if (s.a > s.b) and (pt >= s.a):
                    return sublime.Region(s.a - 1, pt)
                elif (s.a > s.b):
                    return sublime.Region(s.a, pt)
                elif (view.size() == pt):
                    pt -= 1
                return sublime.Region(s.a, pt)

            elif mode == modes.INTERNAL_NORMAL:
                a = s.a
                pt = units.word_ends(view,
                                     start=s.b,
                                     count=count)
                if (not view.substr(view.line(s.a)).strip() and
                   view.line(s.b) != view.line(pt)):
                        a = view.line(s.a).a
                return sublime.Region(a, pt)
            return s

        regions_transformer(self.view, f)


class _vi_zero(ViMotionCommand):
    def run(self, mode=None, count=1):
        def f(view, s):
            if mode == modes.NORMAL:
                return sublime.Region(view.line(s.b).a)
            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, view.line(s.b).a)
            elif mode == modes.VISUAL:
                if s.a < s.b:
                    return sublime.Region(s.a, view.line(s.b - 1).a + 1)
                else:
                    return sublime.Region(s.a, view.line(s.b).a)
            return s

        regions_transformer(self.view, f)


class _vi_right_brace(ViMotionCommand):
    def run(self, mode=None, count=1):
        def f(view, s):
            # TODO: must skip empty paragraphs.
            start = utils.next_non_white_space_char(view, s.b, white_space='\n \t')
            par_as_region = view.expand_by_class(start, sublime.CLASS_EMPTY_LINE)

            if mode == modes.NORMAL:
                min_pt = max(0, min(par_as_region.b, view.size() - 1))
                return sublime.Region(min_pt, min_pt)

            elif mode == modes.VISUAL:
                return sublime.Region(s.a, par_as_region.b + 1)

            elif mode == modes.INTERNAL_NORMAL:
                if view.substr(s.begin()) == '\n':
                    return sublime.Region(s.a, par_as_region.b)
                else:
                    return sublime.Region(s.a, par_as_region.b - 1)

            elif mode == modes.VISUAL_LINE:
                if s.a <= s.b:
                    return sublime.Region(s.a, par_as_region.b + 1)
                else:
                    if par_as_region.b > s.a:
                        return sublime.Region(view.line(s.a - 1).a, par_as_region.b + 1)
                    return sublime.Region(s.a, par_as_region.b)

            return s

        regions_transformer(self.view, f)


class _vi_left_brace(ViMotionCommand):
    def run(self, mode=None, count=1):
        def f(view, s):
            # TODO: must skip empty paragraphs.
            start = utils.previous_non_white_space_char(view, s.b - 1, white_space='\n \t')
            par_as_region = view.expand_by_class(start, sublime.CLASS_EMPTY_LINE)

            if mode == modes.NORMAL:
                return sublime.Region(par_as_region.a, par_as_region.a)

            elif mode == modes.VISUAL:
                # FIXME: Improve motion when .b end crosses over .a end: must extend .a end
                # by one.
                if s.a == par_as_region.a:
                    return sublime.Region(s.a, s.a + 1)
                return sublime.Region(s.a, par_as_region.a)

            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, par_as_region.a)

            elif mode == modes.VISUAL_LINE:
                if s.a <= s.b:
                    if par_as_region.a < s.a:
                        return sublime.Region(view.full_line(s.a).b, par_as_region.a)
                    return sublime.Region(s.a, par_as_region.a + 1)
                else:
                    return sublime.Region(s.a, par_as_region.a)

            return s

        regions_transformer(self.view, f)


class _vi_percent(ViMotionCommand):
    # TODO: Perhaps truly support multiple regions here?
    pairs = (
            ('(', ')'),
            ('[', ']'),
            ('{', '}'),
            ('<', '>'),
    )

    def find_tag(self, pt):
        if (self.view.score_selector(0, 'text.html') == 0 and
            self.view.score_selector(0, 'text.xml') == 0):
                return None

        if any([self.view.substr(pt) in p for p in self.pairs]):
            return None

        _, tag = get_closest_tag(self.view, pt)
        if tag.contains(pt):
            begin_tag, end_tag, _ = find_containing_tag(self.view, pt)
            if begin_tag:
                return begin_tag if end_tag.contains(pt) else end_tag


    def run(self, percent=None, mode=None):
        if percent == None:
            def move_to_bracket(view, s):
                def find_bracket_location(region):
                    pt = region.b
                    if (region.size() > 0) and (region.b > region.a):
                        pt = region.b - 1

                    tag = self.find_tag(pt)
                    if tag:
                        return tag.a

                    bracket, brackets, bracket_pt = self.find_a_bracket(pt)
                    if not bracket:
                        return

                    if bracket == brackets[0]:
                        return self.find_balanced_closing_bracket(bracket_pt + 1, brackets)
                    else:
                        return self.find_balanced_opening_bracket(bracket_pt, brackets)

                if mode == modes.VISUAL:
                    found = find_bracket_location(s)
                    if found is not None:
                        # Offset by 1 if s.a was upperbound but begin is not
                        begin = (s.a - 1) if (s.b < s.a and (s.a - 1) < found) else s.a
                        # Offset by 1 if begin is now upperbound but s.a was not
                        begin = (s.a + 1) if (found < s.a and s.a < s.b) else begin

                        # Testing against adjusted begin
                        end = (found + 1) if (begin <= found) else found

                        return sublime.Region(begin, end)

                if mode == modes.VISUAL_LINE:
                    # TODO: Improve handling of s.a < s.b and s.a > s.b cases.
                    a = find_bracket_location(s)
                    if a is not None:
                        a = self.view.full_line(a).b
                        return sublime.Region(s.begin(), a)

                elif mode == modes.NORMAL:
                    a = find_bracket_location(s)
                    if a is not None:
                        return sublime.Region(a, a)

                # TODO: According to Vim we must swallow brackets in this case.
                elif mode == modes.INTERNAL_NORMAL:
                    found = find_bracket_location(s)
                    if found is not None:
                        if found < s.a:
                            return sublime.Region(s.a + 1, found)
                        else:
                            return sublime.Region(s.a, found + 1)

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


class _vi_big_h(ViMotionCommand):
    def run(self, count=None, mode=None):
        def f(view, s):
            if mode == modes.NORMAL:
                non_ws = utils.next_non_white_space_char(view, target)
                return sublime.Region(non_ws, non_ws)
            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a + 1, target)
            elif mode == modes.VISUAL:
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


class _vi_big_l(ViMotionCommand):
    def run(self, count=None, mode=None):
        def f(view, s):
            if mode == modes.NORMAL:
                non_ws = utils.next_non_white_space_char(view, target)
                return sublime.Region(non_ws, non_ws)
            elif mode == modes.INTERNAL_NORMAL:
                if s.b >= target:
                    return sublime.Region(s.a + 1, target)
                return sublime.Region(s.a, target)
            elif mode == modes.VISUAL:
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


class _vi_big_m(ViMotionCommand):
    def run(self, count=None, extend=False, mode=None):
        def f(view, s):
            if mode == modes.NORMAL:
                non_ws = utils.next_non_white_space_char(view, target)
                return sublime.Region(non_ws, non_ws)
            elif mode == modes.INTERNAL_NORMAL:
                if s.b >= target:
                    return sublime.Region(s.a + 1, target)
                return sublime.Region(s.a, target)
            elif mode == modes.VISUAL:
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


class _vi_star(ViMotionCommand, ExactWordBufferSearchBase):
    def run(self, count=1, mode=None, exact_word=True):
        def f(view, s):
            pattern = self.build_pattern(query)
            flags = self.calculate_flags()

            if mode == modes.INTERNAL_NORMAL:
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
                if mode == modes.INTERNAL_NORMAL:
                    return sublime.Region(s.a, match.begin())
                elif state.mode == modes.VISUAL:
                    return sublime.Region(s.a, match.begin())
                elif state.mode == modes.NORMAL:
                    return sublime.Region(match.begin(), match.begin())

            elif mode == modes.NORMAL:
                pt = utils.previous_white_space_char(view, s.b)
                return sublime.Region(pt + 1)

            return s

        state = self.state

        query = self.get_query()
        if query:
            self.hilite(query)
            # Ensure n and N can repeat this search later.
            state.last_buffer_search = query

        regions_transformer(self.view, f)


class _vi_octothorp(ViMotionCommand, ExactWordBufferSearchBase):
    def run(self, count=1, mode=None, exact_word=True):
        def f(view, s):
            pattern = self.build_pattern(query)
            flags = self.calculate_flags()

            if mode == modes.INTERNAL_NORMAL:
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
                if mode == modes.INTERNAL_NORMAL:
                    return sublime.Region(s.b, match.begin())
                elif state.mode == modes.VISUAL:
                    return sublime.Region(s.b, match.begin())
                elif state.mode == modes.NORMAL:
                    return sublime.Region(match.begin(), match.begin())

            elif mode == modes.NORMAL:
                pt = utils.previous_white_space_char(view, s.b)
                return sublime.Region(pt + 1)

            return s

        state = self.state

        query = self.get_query()
        if query:
            self.hilite(query)
            # Ensure n and N can repeat this search later.
            state.last_buffer_search = query

        start_sel = self.view.sel()[0]
        regions_transformer(self.view, f)


class _vi_b(ViMotionCommand):
    def run(self, mode=None, count=1):
        def do_motion(view, s):
            if mode == modes.NORMAL:
                pt = word_reverse(self.view, s.b, count)
                return sublime.Region(pt)

            elif mode == modes.INTERNAL_NORMAL:
                pt = word_reverse(self.view, s.b, count)
                return sublime.Region(s.a, pt)

            elif mode in (modes.VISUAL, modes.VISUAL_BLOCK):
                if s.a < s.b:
                    pt = word_reverse(self.view, s.b - 1, count)
                    if pt < s.a:
                        return sublime.Region(s.a + 1, pt)
                    return sublime.Region(s.a, pt + 1)
                elif s.b < s.a:
                    pt = word_reverse(self.view, s.b, count)
                    return sublime.Region(s.a, pt)

            return s

        regions_transformer(self.view, do_motion)


class _vi_big_b(ViMotionCommand):
    # TODO: Reimplement this.
    def run(self, count=1, mode=None):
        def do_motion(view, s):
            if mode == modes.NORMAL:
                pt = word_reverse(self.view, s.b, count, big=True)
                return sublime.Region(pt)

            elif mode == modes.INTERNAL_NORMAL:
                pt = word_reverse(self.view, s.b, count, big=True)
                return sublime.Region(s.a, pt)

            elif mode in (modes.VISUAL, modes.VISUAL_BLOCK):
                if s.a < s.b:
                    pt = word_reverse(self.view, s.b - 1, count, big=True)
                    if pt < s.a:
                        return sublime.Region(s.a + 1, pt)
                    return sublime.Region(s.a, pt + 1)
                elif s.b < s.a:
                    pt = word_reverse(self.view, s.b, count, big=True)
                    return sublime.Region(s.a, pt)

            return s

        regions_transformer(self.view, do_motion)


class _vi_underscore(ViMotionCommand):
    def run(self, count=None, mode=None):
        def f(view, s):
            if mode == modes.NORMAL:
                current_row, _ = self.view.rowcol(s.b)
                bol = self.view.text_point(current_row + (count - 1), 0)
                bol = utils.next_non_white_space_char(self.view, bol, white_space='\t ')
                return sublime.Region(bol)
            elif mode == modes.INTERNAL_NORMAL:
                current_row, _ = self.view.rowcol(s.b)
                begin = self.view.text_point(current_row, 0)
                end = self.view.text_point(current_row + (count - 1), 0)
                end = self.view.full_line(end).b
                return sublime.Region(begin, end)
            elif mode == modes.VISUAL:
                if self.view.rowcol(s.b)[1] == 0:
                    return s
                bol = self.view.line(s.b - 1).a
                bol = utils.next_non_white_space_char(self.view, bol, white_space='\t ')
                if (s.a < s.b) and (bol < s.a):
                    return sublime.Region(s.a + 1, bol)
                elif (s.a < s.b):
                    return sublime.Region(s.a, bol + 1)
                return sublime.Region(s.a, bol)
            else:
                return s

        regions_transformer(self.view, f)


class _vi_hat(ViMotionCommand):
    def run(self, count=None, mode=None):
        def f(view, s):
            if mode == modes.NORMAL:
                bol = self.view.line(s.b).a
                bol = utils.next_non_white_space_char(self.view, bol, white_space='\t ')
                return sublime.Region(bol)
            elif mode == modes.INTERNAL_NORMAL:
                begin = self.view.line(s.b).a
                begin = utils.next_non_white_space_char(self.view, begin, white_space='\t ')
                return sublime.Region(begin, s.b)
            elif mode == modes.VISUAL:
                if self.view.rowcol(s.b)[1] == 0:
                    return s
                bol = self.view.line(s.b - 1).a
                bol = utils.next_non_white_space_char(self.view, bol, white_space='\t ')
                if (s.a < s.b) and (bol < s.a):
                    return sublime.Region(s.a + 1, bol)
                elif (s.a < s.b):
                    return sublime.Region(s.a, bol + 1)
                return sublime.Region(s.a, bol)
            else:
                return s

        regions_transformer(self.view, f)


class _vi_gj(ViMotionCommand):
    def run(self, mode=None, count=1):
        if mode == modes.NORMAL:
            for i in range(count):
                self.view.run_command('move', {'by': 'lines', 'forward': True, 'extend': False})
        elif mode == modes.VISUAL:
            for i in range(count):
                self.view.run_command('move', {'by': 'lines', 'forward': True, 'extend': True})
        elif mode == modes.INTERNAL_NORMAL:
            for i in range(count):
                self.view.run_command('move', {'by': 'lines', 'forward': True, 'extend': False})


class _vi_gk(ViMotionCommand):
    def run(self, mode=None, count=1):
        if mode == modes.NORMAL:
            for i in range(count):
                self.view.run_command('move', {'by': 'lines', 'forward': False, 'extend': False})
        elif mode == modes.VISUAL:
            for i in range(count):
                self.view.run_command('move', {'by': 'lines', 'forward': False, 'extend': True})
        elif mode == modes.INTERNAL_NORMAL:
            for i in range(count):
                self.view.run_command('move', {'by': 'lines', 'forward': False, 'extend': False})


class _vi_g__(ViMotionCommand):
    def run(self, count=1, mode=None):
        def f(view, s):
            if mode == modes.NORMAL:
                eol = view.line(s.b).b
                return sublime.Region(eol - 1, eol - 1)

            elif mode == modes.VISUAL:
                eol = view.line(s.b - 1).b
                return sublime.Region(s.a, eol)

            elif mode == modes.INTERNAL_NORMAL:
                eol = view.line(s.b).b
                return sublime.Region(s.a, eol)

            return s

        regions_transformer(self.view, f)


class _vi_ctrl_u(ViMotionCommand):
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

    def run(self, mode=None, count=None):

        def f(view, s):
            if mode == modes.NORMAL:
                return previous

            elif mode == modes.VISUAL:
                return sublime.Region(s.a, previous.b)

            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, previous.b)

            elif mode == modes.VISUAL_LINE:
                return sublime.Region(s.a, self.view.full_line(previous.b).b)

            return s

        previous, scroll_amount = self.prev_half_page(count)
        regions_transformer(self.view, f)


class _vi_ctrl_d(ViMotionCommand):
    def next_half_page(self, count=1, mode=None):

        origin = self.view.sel()[0]

        visible = self.view.visible_region()
        row_a = self.view.rowcol(visible.a)[0]
        row_b = self.view.rowcol(visible.b)[0]

        half_page_span = (row_b - row_a) // 2 * count

        next_half_page = self.view.rowcol(origin.b)[0] + half_page_span

        pt = self.view.text_point(next_half_page, 0)
        return sublime.Region(pt, pt), (self.view.rowcol(pt)[0] -
                                        self.view.rowcol(visible.a)[0])

    def run(self, mode=None, extend=False, count=None):

        def f(view, s):
            if mode == modes.NORMAL:
                return next

            elif mode == modes.VISUAL:
                return sublime.Region(s.a, next.b)

            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, next.b)

            elif mode == modes.VISUAL_LINE:
                return sublime.Region(s.a, self.view.full_line(next.b).b)

            return s

        next, scroll_amount = self.next_half_page(count)
        regions_transformer(self.view, f)


class _vi_pipe(ViMotionCommand):
    def col_to_pt(self, pt, nr):
        if self.view.line(pt).size() < nr:
            return self.view.line(pt).b - 1

        row = self.view.rowcol(pt)[0]
        return self.view.text_point(row, nr) - 1

    def run(self, mode=None, count=None):
        def f(view, s):
            if mode == modes.NORMAL:
                pt = self.col_to_pt(pt=s.b, nr=count)
                return sublime.Region(pt, pt)

            elif mode == modes.VISUAL:
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

            elif mode == modes.INTERNAL_NORMAL:
                pt = self.col_to_pt(pt=s.b, nr=count)
                if s.a < s.b:
                    return sublime.Region(s.a, pt)
                else:
                    return sublime.Region(s.a + 1, pt)

            return s

        regions_transformer(self.view, f)


class _vi_ge(ViMotionCommand):
    def run(self, mode=None, count=1):
        def to_word_end(view, s):
            if mode == modes.NORMAL:
                pt = word_end_reverse(view, s.b, count)
                return sublime.Region(pt)
            elif mode in (modes.VISUAL, modes.VISUAL_BLOCK):
                if s.a < s.b:
                    pt = word_end_reverse(view, s.b - 1, count)
                    if pt > s.a:
                        return sublime.Region(s.a, pt + 1)
                    return sublime.Region(s.a + 1, pt)
                pt = word_end_reverse(view, s.b, count)
                return sublime.Region(s.a, pt)
            return s

        regions_transformer(self.view, to_word_end)


class _vi_g_big_e(ViMotionCommand):
    def run(self, mode=None, count=1):
        def to_word_end(view, s):
            if mode == modes.NORMAL:
                pt = word_end_reverse(view, s.b, count, big=True)
                return sublime.Region(pt)
            elif mode in (modes.VISUAL, modes.VISUAL_BLOCK):
                if s.a < s.b:
                    pt = word_end_reverse(view, s.b - 1, count, big=True)
                    if pt > s.a:
                        return sublime.Region(s.a, pt + 1)
                    return sublime.Region(s.a + 1, pt)
                pt = word_end_reverse(view, s.b, count, big=True)
                return sublime.Region(s.a, pt)
            return s

        regions_transformer(self.view, to_word_end)


class _vi_left_paren(ViMotionCommand):
    def find_previous_sentence_end(self, r):
        sen = r
        pt = utils.previous_non_white_space_char(self.view, sen.a, white_space='\n \t')
        sen = sublime.Region(pt, pt)
        while True:
            sen = self.view.expand_by_class(sen, sublime.CLASS_LINE_END | sublime.CLASS_PUNCTUATION_END)
            if sen.a <= 0 or self.view.substr(sen.begin() - 1) in ('.', '\n', '?', '!'):
                if self.view.substr(sen.begin() - 1) == '.' and not self.view.substr(sen.begin()) == ' ':
                    continue
                return sen

    def run(self, mode=None, count=1):

        def f(view, s):
            # TODO: must skip empty paragraphs.
            sen = self.find_previous_sentence_end(s)

            if mode == modes.NORMAL:
                return sublime.Region(sen.a, sen.a)

            elif mode == modes.VISUAL:
                return sublime.Region(s.a + 1, sen.a +  1)

            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, sen.a + 1)

            return s

        regions_transformer(self.view, f)



class _vi_right_paren(ViMotionCommand):
    def find_next_sentence_end(self, r):
        sen = r
        non_ws = utils.next_non_white_space_char(self.view, sen.b, '\t \n')
        sen = sublime.Region(non_ws, non_ws)
        while True:
            sen = self.view.expand_by_class(sen, sublime.CLASS_PUNCTUATION_START |
                                                 sublime.CLASS_LINE_END)
            if (sen.b == self.view.size() or
                (self.view.substr(sublime.Region(sen.b, sen.b + 2)).endswith(('. ', '.\t'))) or
                (self.view.substr(sublime.Region(sen.b, sen.b + 1)).endswith(('?', '!'))) or
                (self.view.substr(self.view.line(sen.b)).strip() == '')):
                    if self.view.substr(sen.b) in '.?!':
                        return sublime.Region(sen.a, sen.b + 1)
                    else:
                        if self.view.line(sen.b).empty():
                            return sublime.Region(sen.a, sen.b)
                        else:
                            return self.view.full_line(sen.b)

    def run(self, mode=None, count=1):
        def f(view, s):
            # TODO: must skip empty paragraphs.
            sen = self.find_next_sentence_end(s)

            if mode == modes.NORMAL:
                target = min(sen.b, view.size() - 1)
                return sublime.Region(target, target)

            elif mode == modes.VISUAL:
                # TODO: Must encompass new line char too?
                return sublime.Region(s.a, sen.b)

            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, sen.b)

            return s

        regions_transformer(self.view, f)


class _vi_question_mark_impl(ViMotionCommand, BufferSearchBase):
    def run(self, search_string, mode=None, count=1, extend=False):
        def f(view, s):
            # FIXME: readjust carets if we searched for '\n'.
            if mode == modes.VISUAL:
                return sublime.Region(s.end(), found.a)

            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.end(), found.a)

            elif mode == modes.NORMAL:
                return sublime.Region(found.a, found.a)

            elif mode == modes.VISUAL_LINE:
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
class _vi_question_mark(ViMotionCommand, BufferSearchBase):
    def run(self, default=''):
        self.state.reset_during_init = False
        state = self.state
        on_change = self.on_change if state.settings.vi['incsearch'] else None
        mark_as_widget(self.view.window().show_input_panel(
                                                            '',
                                                            default,
                                                            self.on_done,
                                                            on_change,
                                                            self.on_cancel))

    def on_done(self, s):
        state = self.state
        state.sequence += s + '<CR>'
        self.view.erase_regions('vi_inc_search')
        state.motion = cmd_defs.ViSearchBackwardImpl(term=s)

        # If s is empty, we must repeat the last search.
        state.last_buffer_search = s or state.last_buffer_search
        state.eval()

    def on_change(self, s):
        flags = self.calculate_flags()
        self.view.erase_regions('vi_inc_search')
        state = self.state
        occurrence = reverse_find_wrapping(self.view,
                                 term=s,
                                 start=0,
                                 end=self.view.sel()[0].b,
                                 flags=flags,
                                 times=state.count)
        if occurrence:
            if state.mode == modes.VISUAL:
                occurrence = sublime.Region(self.view.sel()[0].a, occurrence.a)
            self.view.add_regions('vi_inc_search', [occurrence], 'comment', '')
            if not self.view.visible_region().contains(occurrence):
                self.view.show(occurrence)

    def on_cancel(self):
        self.view.erase_regions('vi_inc_search')
        state = self.state
        state.reset_command_data()

        if not self.view.visible_region().contains(self.view.sel()[0]):
            self.view.show(self.view.sel()[0])


class _vi_n(ViMotionCommand):
    # TODO: This is a jump.
    def run(self, mode=None, count=1, search_string=''):
        self.view.run_command('_vi_slash_impl', {'mode': mode, 'count': count, 'search_string': search_string})


class _vi_big_n(ViMotionCommand):
    # TODO: This is a jump.
    def run(self, count=1, mode=None, search_string=''):
        self.view.run_command('_vi_question_mark_impl', {'mode': mode, 'count': count, 'search_string': search_string})


class _vi_big_e(ViMotionCommand):
    def run(self, mode=None, count=1):
        def do_move(view, s):
            b = s.b
            if s.a < s.b:
                b = s.b - 1

            pt = units.word_ends(view, b, count=count, big=True)

            if mode == modes.NORMAL:
                return sublime.Region(pt - 1)

            elif mode == modes.INTERNAL_NORMAL:
                return sublime.Region(s.a, pt)

            elif mode == modes.VISUAL:
                start = s.a
                if s.b < s.a:
                    start = s.a - 1
                end = pt - 1
                if start <= end:
                    return sublime.Region(start, end + 1)
                else:
                    return sublime.Region(start + 1, end)

            # Untested
            elif mode == modes.VISUAL_BLOCK:
                if s.a > s.b:
                    if pt > s.a:
                        return sublime.Region(s.a - 1, pt)
                    return sublime.Region(s.a, pt - 1)
                return sublime.Region(s.a, pt)

            return s

        regions_transformer(self.view, do_move)


class _vi_ctrl_f(ViMotionCommand):
    def run(self, mode=None, count=1):
        def extend_to_full_line(view, s):
            return view.full_line(s.b)

        if mode == modes.NORMAL:
            self.view.run_command('move', {'by': 'pages', 'forward': True})
        if mode == modes.VISUAL:
            self.view.run_command('move', {'by': 'pages', 'forward': True, 'extend': True})
        elif mode == modes.VISUAL_LINE:
            self.view.run_command('move', {'by': 'pages', 'forward': True, 'extend': True})
            regions_transformer(self.view, extend_to_full_line)
        elif mode == modes.VISUAL_BLOCK:
            return


class _vi_ctrl_b(ViMotionCommand):
    def run(self, mode=None, count=1):
        if mode == modes.NORMAL:
            self.view.run_command('move', {'by': 'pages', 'forward': False})
        elif mode != modes.NORMAL:
            return


class _vi_enter(ViMotionCommand):
   def run(self, mode=None, count=1):
        self.view.run_command('_vi_j', {'mode': mode, 'count': count})

        def advance(view, s):
            if mode == modes.NORMAL:
                pt = utils.next_non_white_space_char(view, s.b,
                                                     white_space=' \t')
                return sublime.Region(pt)
            elif mode == modes.VISUAL:
                if s.a < s.b:
                    pt = utils.next_non_white_space_char(view, s.b - 1,
                                                         white_space=' \t')
                    return sublime.Region(s.a, pt + 1)
                pt = utils.next_non_white_space_char(view, s.b,
                                                     white_space=' \t')
                return sublime.Region(s.a, pt)
            return s

        regions_transformer(self.view, advance)


class _vi_shift_enter(ViMotionCommand):
   def run(self, mode=None, count=1):
        self.view.run_command('_vi_ctrl_f', {'mode': mode, 'count': count})


class _vi_select_text_object(ViMotionCommand):
    def run(self, text_object=None, mode=None, count=1, extend=False, inclusive=False):
        def f(view, s):
            # TODO: Vim seems to swallow the delimiters if you give this command a count, which is
            #       a pretty weird behavior.
            if mode == modes.INTERNAL_NORMAL:

                return get_text_object_region(view, s, text_object,
                                              inclusive=inclusive,
                                              count=count)

            if mode == modes.VISUAL:
                return get_text_object_region(view, s, text_object,
                                              inclusive=inclusive,
                                              count=count)

            return s

        regions_transformer(self.view, f)


class _vi_go_to_symbol(ViMotionCommand):
    """Go to local declaration. Differs from Vim because it leverages Sublime Text's ability to
       actually locate symbols (Vim simply searches from the top of the file).
    """
    def find_symbol(self, r, globally=False):
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


    def run(self, count=1, mode=None, globally=False):

        def f(view, s):
            if mode == modes.NORMAL:
                return sublime.Region(location, location)

            elif mode == modes.VISUAL:
                return sublime.Region(s.a + 1, location)

            elif mode == modes.INTERNAL_NORMAL:
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
            # TODO: Perhaps must be a motion if the target file happens to be
            #       the current one?
            self.view.window().open_file(
                location[0] + ':' + ':'.join([str(x) for x in location[2]]),
                sublime.ENCODED_POSITION)
            return

        # Local symbol; select.
        location = self.view.text_point(*location)
        regions_transformer(self.view, f)


class _vi_gm(ViMotionCommand):
    """
    Vim: `gm`
    """
    def run(self, mode=None, count=1):
        if mode != modes.NORMAL:
            utils.blink()
            return

        def advance(view, s):
            line = view.line(s.b)
            delta = (line.b - s.b) // 2
            return sublime.Region(min(s.b + delta, line.b - 1))

        regions_transformer(self.view, advance)


class _vi_left_square_bracket(ViMotionCommand):
    """
    Vim: `[`
    """
    BRACKETS = {
        '{': ('\\{', '\\}'),
        '}': ('\\{', '\\}'),
        '(': ('\\(', '\\)'),
        ')': ('\\(', '\\)'),
    }

    def run(self, mode=None, count=1, char=None):
        def move(view, s):
            reg = find_prev_lone_bracket(self.view, s.b, brackets)
            if reg is not None:
                return sublime.Region(reg.a)
            return s

        if mode != modes.NORMAL:
            self.enter_normal_mode(mode=mode)
            utils.blink()
            return

        brackets = self.BRACKETS.get(char)
        if brackets is None:
            utils.blink()
            return

        regions_transformer(self.view, move)


class _vi_right_square_bracket(ViMotionCommand):
    """
    Vim: `]`
    """
    BRACKETS = {
        '{': ('\\{', '\\}'),
        '}': ('\\{', '\\}'),
        '(': ('\\(', '\\)'),
        ')': ('\\(', '\\)'),
    }

    def run(self, mode=None, count=1, char=None):
        def move(view, s):
            reg = find_next_lone_bracket(self.view, s.b, brackets)
            if reg is not None:
                return sublime.Region(reg.a)
            return s

        if mode != modes.NORMAL:
            utils.blink()
            self.enter_normal_mode(mode=mode)
            return

        brackets = self.BRACKETS.get(char)
        if brackets is None:
            utils.blink()
            return

        regions_transformer(self.view, move)
