import sublime
import sublime_plugin

from Vintageous.run import ViExecutionState
from Vintageous.state import VintageState
from Vintageous.vi import utils
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.constants import MODE_VISUAL_BLOCK
from Vintageous.vi.constants import regions_transformer
from Vintageous.vi.text_objects import get_text_object_region


class ExtendToMinimalWidth(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            # TODO: This will confuse users, but otherwise they will be even more confused, because
            # the caret will disappear until they press h, l, etc.
            # Alternatively, we could abort the mode change?
            if view.size() == 0:
                return s

            if s.empty():
                return sublime.Region(s.a, s.b + 1)
            else:
                return s

        regions_transformer(self.view, f)


class CollapseToDirection(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            if not s.empty():
                if s.a < s.b:
                    return sublime.Region(s.b - 1, s.b - 1)
                else:
                    return sublime.Region(s.b, s.b)
            else:
                return s

        regions_transformer(self.view, f)


class CollapseToA(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            if not s.empty():
                return sublime.Region(s.a, s.a)
            else:
                return s

        regions_transformer(self.view, f)


class _align_b_with_xpos(sublime_plugin.TextCommand):
    def run(self, edit, xpos=-1):
        def f(view, s):
            row, col = view.rowcol(s.b)
            # We assume every time we need to adjust xpos it's because the old one is smaller.
            if (s.a >= s.b) and col < xpos:
                limit = view.line(s.b).size()
                new_col = min(xpos + 1, limit)

                return sublime.Region(s.a, view.text_point(row, new_col))
            return s

        if xpos < 0:
            return

        regions_transformer(self.view, f)


class _vi_collapse_to_begin(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            if not s.empty():
                return sublime.Region(s.begin(), s.begin())
            else:
                return s

        regions_transformer(self.view, f)


class ReorientCaret(sublime_plugin.TextCommand):
    def run(self, edit, forward=True, mode=None):
        def f(view, s):
            if mode != MODE_VISUAL_LINE:
                if s.end() - s.begin() == 1:
                    if forward:
                        if s.b < s.a:
                            return sublime.Region(s.b, s.a)
                        else:
                            return s
                    else:
                        if s.b > s.a:
                            return sublime.Region(s.b, s.a)
                        else:
                            return s
                else:
                    return s

            else:
                if forward:
                    if self.view.full_line(s.b).a == s.b and self.view.full_line(s.b).b == s.a:
                        return sublime.Region(s.b, s.a)
                    else:
                        return s
                elif self.view.full_line(s.b - 1).a == s.a and self.view.full_line(s.b - 1).b == s.b:
                    r = sublime.Region(self.view.full_line(s.a).b, s.a)
                    return r
                else:
                    return s

        regions_transformer(self.view, f)


class VisualExtendToFullLine(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            if s.size() > 0:
                if view.full_line(s.b - 1).b == s.b:
                    return self.view.full_line(sublime.Region(s.a, s.b - 1))
                else:
                    return self.view.full_line(s)
            else:
                return self.view.full_line(s)

        regions_transformer(self.view, f)


class _vi_dd_pre_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                current_line = view.line(s.b)
                return sublime.Region(current_line.a, current_line.a)
            return s

        regions_transformer(self.view, f)


class _vi_dd_post_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if view.full_line(s.b - 1).b == view.size():
                return sublime.Region(max(s.a - 1, 0), view.size())

            if view.substr(s.b - 1) != '\n':
                return sublime.Region(s.a, view.full_line(s.b).b)
            return s

        regions_transformer(self.view, f)


class VisualExtendToLine(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            return self.view.line(s)

        regions_transformer(self.view, f)


class _vi_big_c(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                if view.line(s).empty():
                    return s
            elif mode == MODE_VISUAL:
                if view.line(s.b - 1).empty():
                    return s

            return sublime.Region(s.a, self.view.line(s).b)

        regions_transformer(self.view, f)


class _vi_w_last_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                if s.a <= s.b:
                    if view.substr(s.b) != '\n':
                        end = view.word(s.b).b
                        end = utils.next_non_white_space_char(view, end, white_space='\t ')
                        if end == s.b:
                            end = view.expand_by_class(s.b, sublime.CLASS_PUNCTUATION_END).b
                        return sublime.Region(s.a, end)

                    elif view.line(s.b).empty():
                        return sublime.Region(s.a, s.b + 1)
            return s

        regions_transformer(self.view, f)


class _vi_big_w_last_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                if s.a <= s.b:
                    if view.substr(s.b) != '\n':
                        end = view.word(s.b).b
                        if view.classify(end) & sublime.CLASS_PUNCTUATION_START == sublime.CLASS_PUNCTUATION_START:
                            end = view.expand_by_class(end, sublime.CLASS_PUNCTUATION_END).b
                        end = utils.next_non_white_space_char(view, end, white_space='\t ')
                        return sublime.Region(s.a, end)

                    elif view.line(s.b).empty():
                        return sublime.Region(s.a, s.b + 1)
            return s

        regions_transformer(self.view, f)


class _vi_w_post_every_motion(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        def f(view, s):
            state = VintageState(view)

            if state.mode == MODE_NORMAL:
                if s.b == view.size():
                    return sublime.Region(view.size() - 1, view.size() - 1)
                elif view.substr(s.b) == '\n':
                    if not view.line(s.b).empty():
                        r = sublime.Region(s.b + 1, s.b + 1)
                        pt = utils.next_non_white_space_char(view, r.b, white_space='\t ')
                        return sublime.Region(pt, pt)

            if state.mode == MODE_VISUAL:

                if not utils.is_region_reversed(view, s):
                    # FIXME: Moving from EMPTYLINE to NONEMPTYLINE should select FIRSTCHAR on NEXTLINE
                    # only, but it selects a WORD and the FIRSTCHAR of the following WORD too.

                    # When starting from an empty line, select only the FIRSTCHAR of the FIRSTWORD on
                    # NEXTLINE.
                    if view.size() == s.b:
                        return sublime.Region(s.a, s.b)

                    if ViExecutionState.select_word_begin_from_empty_line:
                        ViExecutionState.reset_word_state()
                        return sublime.Region(s.a, view.word(view.line(s.b).a).a + 1)

                    # If after the motion we're on an empty line, stay there.
                    if view.substr(s.b - 1) == '\n' and view.line(s.b - 1).empty():
                        return s

                    # Always select the FIRSTCHAR of NEXTWORD skipping any WHITESPACE.
                    # XXX: Possible infinite loop at EOF.
                    pt = s.b
                    while True:
                        pt = utils.next_non_white_space_char(view, pt, white_space='\t ')
                        # We're on an EMPTYLINE, so stay here.
                        if view.substr(pt) == '\n' and view.line(pt).empty():
                            break
                        # NEWLINECHAR after NONEMPTYLINE; keep going.
                        elif view.substr(pt) == '\n':
                            pt += 1
                            continue
                        # Any NONWHITESPACECHAR; stop here.
                        else:
                            break

                    s = sublime.Region(s.a, pt + 1)

                # Reversed selections...
                else:
                    # Skip over NEWLINECHAR at EOL if on NONEMPTYLINE.
                    if view.substr(s.b) == '\n' and not view.line(s.b).empty():
                        # FIXME: Don't swallow empty lines.
                        pt = utils.next_non_white_space_char(view, s.b, white_space='\t \n')
                        return sublime.Region(s.a, pt)

            if state.mode == _MODE_INTERNAL_NORMAL:
                if current_iteration == total_iterations:
                    if view.substr(s.b - 1) == '\n' and not view.line(s.b - 1).empty():
                        return sublime.Region(s.a, s.b - 1)

            return s

        regions_transformer(self.view, f)


class _vi_w_pre_every_motion(sublime_plugin.TextCommand):
    def run(self, edit, current_iteration=None, total_iterations=None):
        def f(view, s):
            state = VintageState(view)
            if state.mode == MODE_VISUAL:
                if not utils.is_region_reversed(view, s):

                    if (view.line(s.b - 1).empty() and
                        view.substr(s.b) not in (' \t') and
                        not view.line(s.b).empty()):
                            # When issuing *w* from an empty line in visual mode, Vim will select the FIRSTCHAR
                            # of the FIRSTWORD on the NEXTLINE. For that to happen, we need to signal here
                            # that were in such a context.
                            ViExecutionState.select_word_begin_from_empty_line = True

                    if view.substr(s.b - 1) != '\n':
                        # Ensures that we don't skip over WORDS of length 1.
                        return sublime.Region(s.a, s.b - 1)
                else:
                    return sublime.Region(s.a, s.b + 1)
            return s

        regions_transformer(self.view, f)


class _d_w_post_every_motion(sublime_plugin.TextCommand):
    """Assumes we are in _MODE_INTERNAL_NORMAL.

        Use only for *d* when deleting WORDS.

       This command is meant to be used as a post_every_motion hook.
    """
    def run(self, edit, current_iteration=None, total_iterations=None):
        is_last_iteration = (current_iteration == total_iterations - 1)
        def f(view, s):
            # If:
            #   * motion hasn't completed
            #   * we are at EOL
            #   * we are not on an empty line
            # ... skip the new line character. Othwerwise, S3 will count it as a WORD. Note that
            # empty lines do count as WORDs.
            if (not is_last_iteration and
                view.substr(s.b) == '\n' and
                not view.line(s.b).empty()):
                    return sublime.Region(s.a, s.b + 1)

            # On the last iteration, encompass the whole line if we're at EOL and .a and .b are
            # on different lines.
            if is_last_iteration:
                if (view.line(s.a) != view.line(s.b) and
                    view.substr(s.b) == '\n' and
                    not view.line(s.b - 1).empty()):
                        return sublime.Region(s.a, s.b + 1)

            # On the last iteration, if .a and .b are on different lines, we need to select
            # NEXTWORD and any following WHITESPACE too.
            if (is_last_iteration and
                view.line(s.a) != view.line(s.b) and
                # Is the leading text on this line white space? If so, delete that, the next WORD
                # and any WHITESPACE after it.
                view.substr(sublime.Region(view.line(s.b).a, s.b)).isspace()):
                    pt = utils.next_non_white_space_char(self.view, s.b)
                    pt = utils.next_non_white_space_char(self.view, view.word(pt).b)
                    return sublime.Region(s.a, pt)

            return s

        regions_transformer(self.view, f)


class _vi_e_post_every_motion(sublime_plugin.TextCommand):
    """Use only with ``vi_e``.

        Ensures that the caret ends up at a WORDEND and that it wraps around the new line
        character as needed.

        Works in ANYMODE (except VISUALLINE).
    """
    def run(self, edit, current_iteration=None, total_iterations=None, mode=None):
        def f(view, s):
            is_last_iteration = (current_iteration == total_iterations - 1)

            if mode == _MODE_INTERNAL_NORMAL:
                    # If we're at BOL one LINE down; move to NEXTWORD WORDEND inclusive.
                    if utils.is_at_bol(self.view, s):
                        next = utils.next_non_white_space_char(self.view, s.b, white_space='\t \n')
                        next = self.view.word(next)
                        return sublime.Region(s.a, next.b)
                    else:
                        return s

            elif mode == MODE_NORMAL:
                    # If we're at BOL one LINE down; move to NEXTWORD WORDEND exclusive.
                    if utils.is_at_bol(self.view, s):
                        next = utils.next_non_white_space_char(self.view, s.b, white_space='\t \n')
                        next = self.view.word(next)
                        return sublime.Region(next.b - 1, next.b - 1)
                    # Last motion; ensure caret ends up at a WORDEND exclusive. The native 'move'
                    # command will have left us on the next character.
                    elif is_last_iteration:
                        return sublime.Region(s.a - 1, s.b - 1)
                    else:
                        return s

            elif mode == MODE_VISUAL:
                # If we're at BOL one LINE down, move to NEXTWORD WORDEND inclusive.
                if utils.is_at_bol(self.view, s):
                    next = utils.next_non_white_space_char(self.view, s.b, white_space='\t \n')
                    next = self.view.word(next)
                    return sublime.Region(s.a, next.b)
                else:
                    return s

        regions_transformer(self.view, f)


class _vi_e_pre_motion(sublime_plugin.TextCommand):
    """Use only with ``vi_e``.

        Ensures that the caret moves to the next WORDEND instead on remaining on the current word.

        Works in ANYMODE (except VISUALLINE).
    """
    def run(self, edit, mode):
        def f(view, s):
            if mode == MODE_NORMAL:
                    # What to do if we are not on a white space character...
                    if view.substr(s.b) not in '\t ':
                        # Advance one so that the caret moves as expected instead of remaining on
                        # the same word when the motion executes.
                        if not utils._is_on_eol(view, s, mode):
                                return sublime.Region(s.a + 1, s.b + 1)
                        else:
                            return s
                    # We are on a white space char...
                    else:
                        return s

            else:
                return s

        regions_transformer(self.view, f)


class _vi_b_pre_motion(sublime_plugin.TextCommand):
    """Use only for vi_b.
    """
    # TODO: _MODE_INTERNAL_NORMAL is suspiciously mssing here.
    def run(self, edit, mode, current_iteration, total_iterations):
        def f(view, s):
            if mode == MODE_VISUAL:
                if s.size() == 1:
                    return sublime.Region(s.b, s.a)

            return s

        regions_transformer(self.view, f)


class _vi_b_post_every_motion(sublime_plugin.TextCommand):
    """Use only with for vi_b.
    """
    def run(self, edit, mode, current_iteration, total_iterations):
        def f(view, s):
            if mode == MODE_VISUAL:
                if s.size() == 0:
                    return sublime.Region(s.a, s.a + 1)

            return s

        regions_transformer(self.view, f)


class _vi_underscore_pre_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                line = view.line(s.b)
                return sublime.Region(line.a, line.a)
            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(view.line(s.b).a, view.full_line(s.b).b)
            elif mode == MODE_VISUAL:
                # TODO: This is sloppy. We're reorienting the caret here. We need to use the
                #       existing mechanism for that or imrpove it (using a normal hook as for
                #       other cases.)
                return sublime.Region(s.end(), s.begin())
            return s

        regions_transformer(self.view, f)


class _vi_underscore_post_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        state = VintageState(self.view)
        def f(view, s):
            if mode == MODE_NORMAL:
                pt = utils.next_non_white_space_char(view, s.b)
                return sublime.Region(pt, pt)
            elif mode == MODE_VISUAL:
                line = view.line(s.b)
                pt = utils.next_non_white_space_char(view, line.a)
                return sublime.Region(s.a, pt)
            elif mode == _MODE_INTERNAL_NORMAL:
                if not s.empty() and view.substr(s.b - 1) == '\n':
                    return s
                else:
                    return sublime.Region(s.a, view.full_line(s.b).b)

            return s

        regions_transformer(self.view, f)


class _vi_select_text_object(sublime_plugin.TextCommand):
    def run(self, edit, text_object=None, mode=None, count=1, extend=False, inclusive=False):
        def f(view, s):
            # TODO: Vim seems to swallow the delimiters if you give this command a count, which is
            #       a pretty weird behavior.
            if mode == _MODE_INTERNAL_NORMAL:

                return get_text_object_region(view, s, text_object,
                                              inclusive=inclusive,
                                              count=count)

            if mode == MODE_VISUAL:
                return get_text_object_region(view, s, text_object,
                                              inclusive=inclusive,
                                              count=count)

            return s

        regions_transformer(self.view, f)


class _vi_yy_pre_motion(sublime_plugin.TextCommand):
    # Assume NORMAL_MODE / _MODE_INTERNAL_NORMAL
    def run(self, edit, mode=None):
        def f(view, s):
            line = view.line(s.b)
            return sublime.Region(line.a, line.b + 1)

        regions_transformer(self.view, f)


class _vi_yy_post_motion(sublime_plugin.TextCommand):
    # Assume NORMAL_MODE / _MODE_INTERNAL_NORMAL
    def run(self, edit):
        def f(view, s):
            line = view.line(s.b - 1)
            return sublime.Region(s.a, line.b + 1)

        regions_transformer(self.view, f)


class _vi_move_caret_to_first_non_white_space_character(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == MODE_VISUAL:
                line = view.line(s.b - 1)
                pt = utils.next_non_white_space_char(view, line.a)
                return sublime.Region(s.a, pt + 1)
            elif mode != MODE_VISUAL_LINE:
                line = view.line(s.b)
                pt = utils.next_non_white_space_char(view, line.a)
                return sublime.Region(pt, pt)

            return s

        regions_transformer(self.view, f)


class _vi_x_post_every_motion(sublime_plugin.TextCommand):
    # Assume NORMAL_MODE / _MODE_INTERNAL_NORMAL
    def run(self, edit, mode=None, current_iteration=None, total_iterations=None):
        def f(view, s):
            if view.substr(s.b - 1) == '\n':
                # FIXME: Actually, we should go back to the first \n; we may have run over
                # multiple ones.
                return sublime.Region(s.a, s.b - 1)
            return s

        regions_transformer(self.view, f)


class _vi_big_x_post_every_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, current_iteration=None, total_iterations=None):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                if view.substr(s.b) == '\n':
                    return sublime.Region(s.b + 1, s.b + 1)

            return s

        regions_transformer(self.view, f)


class _vi_big_x_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == MODE_VISUAL:
                if s.a < s.b:
                    a = view.line(s.a).a
                    b = view.full_line(s.b - 1).b
                else:
                    a = view.full_line(s.a - 1).b
                    b = view.full_line(s.b).a
                return sublime.Region(a, b)
            return s

        regions_transformer(self.view, f)


class _vi_l(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                if view.line(s.b).empty():
                    return s

                x_limit = min(view.line(s.b).b - 1, s.b + count, view.size())
                return sublime.Region(x_limit, x_limit)

            if mode == _MODE_INTERNAL_NORMAL:
                x_limit = min(view.line(s.b).b, s.b + count)
                x_limit = max(0, x_limit)
                return sublime.Region(s.a, x_limit)

            if mode in (MODE_VISUAL, MODE_VISUAL_BLOCK):
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


class _vi_h(sublime_plugin.TextCommand):
    def run(self, edit, count=None, mode=None):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                x_limit = max(view.line(s.b).a, s.b - count)
                return sublime.Region(s.a, x_limit)

            # TODO: Split handling of the two modes for clarity.
            elif mode in (MODE_VISUAL, MODE_VISUAL_BLOCK):

                if s.a < s.b:
                    if mode == MODE_VISUAL_BLOCK and self.view.rowcol(s.b - 1)[1] == baseline:
                        return s

                    x_limit = max(view.line(s.b - 1).a + 1, s.b - count)
                    if view.line(s.a) == view.line(s.b - 1) and count >= s.size():
                        x_limit = max(view.line(s.b - 1).a, s.b - count - 1)
                        return sublime.Region(s.a + 1, x_limit)
                    return sublime.Region(s.a, x_limit)

                if s.a > s.b:
                    x_limit = max(view.line(s.b).a, s.b - count)
                    return sublime.Region(s.a, x_limit)

            elif mode == MODE_NORMAL:
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
        if mode == MODE_VISUAL_BLOCK:
            sel = self.view.sel()[0]
            if sel.a < sel.b:
                min_ = min(self.view.rowcol(r.b - 1)[1] for r in self.view.sel())
                if any(self.view.rowcol(r.b - 1)[1] != min_ for r in self.view.sel()):
                    baseline = min_

        regions_transformer(self.view, f)


class _vi_j(sublime_plugin.TextCommand):
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

    def run(self, edit, count=None, mode=None, xpos=0):
        def f(view, s):
            if mode == MODE_NORMAL:
                current_row = view.rowcol(s.b)[0]
                target_row = min(current_row + count, view.rowcol(view.size())[0])
                invisible_rows = self.folded_rows(view.line(s.b).b + 1)
                target_pt = view.text_point(target_row + invisible_rows, 0)
                target_pt = self.next_non_folded_pt(target_pt)

                if view.line(target_pt).empty():
                    return sublime.Region(target_pt, target_pt)

                target_pt = min(target_pt + xpos, view.line(target_pt).b - 1)
                return sublime.Region(target_pt, target_pt)

            if mode == _MODE_INTERNAL_NORMAL:
                current_row = view.rowcol(s.b)[0]
                target_row = min(current_row + count, view.rowcol(view.size())[0])
                target_pt = view.text_point(target_row, 0)
                return sublime.Region(view.line(s.a).a, view.full_line(target_pt).b)

            if mode == MODE_VISUAL:
                exact_position = s.b - 1 if (s.a < s.b) else s.b
                current_row = view.rowcol(exact_position)[0]
                target_row = min(current_row + count, view.rowcol(view.size())[0])
                target_pt = view.text_point(target_row, 0)
                is_long_enough = view.full_line(target_pt).size() > xpos

                # We're crossing over to the other side of .a; we need to modify .a.
                crosses_a = False
                if (s.a > s.b) and (view.rowcol(s.a)[0] < target_row):
                    crosses_a = True

                if view.line(s.begin()) == view.line(s.end() - 1):
                    if s.a > s.b:
                        if is_long_enough:
                            return sublime.Region(s.a - 1, view.text_point(target_row, xpos) + 1)
                        else:
                            return sublime.Region(s.a - 1, view.full_line(target_pt).b)

                # Returning to the same line...
                if not crosses_a and abs(view.rowcol(s.begin())[0] - view.rowcol(s.end())[0]) == 1:
                    if s.a > s.b:
                        if is_long_enough:
                            if view.rowcol(s.a - 1)[1] <= view.rowcol(s.b)[1]:
                                return sublime.Region(s.a - 1, view.text_point(target_row, xpos) + 1)

                if is_long_enough:
                    if s.a < s.b:
                        return sublime.Region(s.a, view.text_point(target_row, xpos) + 1)
                    elif s.a > s.b:
                        start = s.a if not crosses_a else s.a - 1
                        end = view.text_point(target_row, xpos)
                        end = end if (end < s.a) else end + 1
                        return sublime.Region(start, end)
                else:
                    if s.a < s.b:
                        return sublime.Region(s.a, view.full_line(target_pt).b)
                    elif s.a > s.b:
                        end = view.full_line(target_pt).b
                        end = end - 1 if not crosses_a else end
                        return sublime.Region(s.a, end)

            if mode == MODE_VISUAL_LINE:
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

        if mode == MODE_VISUAL_BLOCK:
            # Don't do anything if we have reversed selections.
            if any((r.b < r.a) for r in self.view.sel()):
                return
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
            self.view.sel().add(sublime.Region(start, start + max_size))
            return

        regions_transformer(self.view, f)


class _vi_k(sublime_plugin.TextCommand):
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

    def run(self, edit, count=None, mode=None, xpos=0):
        def f(view, s):
            if mode == MODE_NORMAL:
                current_row = view.rowcol(s.b)[0]
                target_row = min(current_row - count, view.rowcol(view.size())[0])
                target_pt = view.text_point(target_row, 0)
                target_pt = self.previous_non_folded_pt(target_pt)

                if view.line(target_pt).empty():
                    return sublime.Region(target_pt, target_pt)

                target_pt = min(target_pt + xpos, view.line(target_pt).b - 1)
                return sublime.Region(target_pt, target_pt)

            if mode == _MODE_INTERNAL_NORMAL:
                current_row = view.rowcol(s.b)[0]
                target_row = min(current_row - count, view.rowcol(view.size())[0])
                target_pt = view.text_point(target_row, 0)
                return sublime.Region(view.full_line(s.a).b, view.line(target_pt).a)

            if mode == MODE_VISUAL:
                exact_position = s.b - 1 if (s.a < s.b) else s.b
                current_row = view.rowcol(exact_position)[0]
                target_row = max(current_row - count, 0)
                target_pt = view.text_point(target_row, 0)
                is_long_enough = view.full_line(target_pt).size() > xpos

                # We're crossing over to the other side of .a; we need to modify .a.
                crosses_a = False
                if (s.a < s.b) and (view.rowcol(s.a)[0] > target_row):
                    crosses_a = True

                if view.line(s.begin()) == view.line(s.end() - 1):
                    if s.a < s.b:
                        if is_long_enough:
                            return sublime.Region(s.a + 1, view.text_point(target_row, xpos))
                        else:
                            return sublime.Region(s.a + 1, view.line(target_pt).b)

                # Returning to the same line...
                if not crosses_a and abs(view.rowcol(s.begin())[0] - view.rowcol(s.end() - 1)[0]) == 1:
                    if s.a < s.b:
                        if is_long_enough:
                            if view.rowcol(s.a)[1] <= view.rowcol(s.b - 1)[1]:
                                return sublime.Region(s.a, view.text_point(target_row, xpos) + 1)
                            else:
                                r = sublime.Region(s.a + 1, view.text_point(target_row, xpos))
                                return r

                if is_long_enough:
                    if s.a < s.b:
                        # FIXME: The following if-else could use some brains.
                        offset = 0
                        if xpos == 0 and not crosses_a:
                            offset = 1
                        elif crosses_a:
                            pass
                        else:
                            offset = 1
                        start = s.a if not crosses_a else s.a + 1
                        return sublime.Region(start, view.text_point(target_row, xpos + offset))
                    elif s.a > s.b:
                        return sublime.Region(s.a, view.text_point(target_row, xpos))
                else:
                    if s.a < s.b:
                        end = view.full_line(target_pt).b
                        end = end if not crosses_a else end - 1
                        return sublime.Region(s.a, end)
                    elif s.a > s.b:
                        return sublime.Region(s.a, view.line(target_pt).b)

            if mode == MODE_VISUAL_LINE:
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

        if mode == MODE_VISUAL_BLOCK:
            # Don't do anything if we have reversed selections.
            if any((r.b < r.a) for r in self.view.sel()):
                return

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
            self.view.sel().add(sublime.Region(rect_a_pt, rect_a_pt + rect_size))
            return

        regions_transformer(self.view, f)


class _vi_orient_selections_toward_begin(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            return sublime.Region(s.begin() + 1, s.begin())

        regions_transformer(self.view, f)


class _vi_adjust_carets(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                if  ((view.substr(s.b) == '\n' or s.b == view.size())
                     and not view.line(s.b).empty()):
                        return sublime.Region(s.b - 1, s.b - 1)
            return s

        regions_transformer(self.view, f)


class _vi_minimal_scroll(sublime_plugin.TextCommand):
    def run(self, edit, forward=True, next_command=None):
        self.view.show(self.view.sel()[0].b, False)


class _vi_big_b_post_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        def f(view, s):
            if mode == _MODE_INTERNAL_NORMAL:
                if view.substr(s.b) != '\n':
                    return sublime.Region(s.a, view.line(s.b).b)
            elif mode == MODE_VISUAL:
                if view.substr(s.b) != '\n':
                    return sublime.Region(s.a, view.line(s.b).b)

            return s

        regions_transformer(self.view, f)
