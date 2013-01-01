import sublime
import sublime_plugin

from Vintageous.state import VintageState
from Vintageous.vi import utils
from Vintageous.vi.constants import MODE_NORMAL, MODE_VISUAL_LINE, MODE_VISUAL, _MODE_INTERNAL_VISUAL
from Vintageous.run import ViExecutionState


# XXX: This is a very bad name. Better: ConvertSelectionsToVisualMode
class ExtendToMinimalWidth(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if s.empty():
                new_sels.append(sublime.Region(s.a, s.b + 1))
            else:
                if s.a < s.b:
                    if utils.is_at_hard_eol(self.view, s):
                        new_sels.append(sublime.Region(s.a, s.b - 1))
                    else:
                        new_sels.append(s)
                else:
                    new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class CollapseToDirection(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if not s.empty():
                if s.a < s.b:
                    new_sels.append(sublime.Region(s.b - 1, s.b - 1))
                else:
                    new_sels.append(sublime.Region(s.b, s.b))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class CollapseToBegin(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if not s.empty():
                new_sels.append(sublime.Region(s.a, s.a))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class ReorientCaret(sublime_plugin.TextCommand):
    def run(self, edit, forward=True, mode=None, _internal_mode=None):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if mode != MODE_VISUAL_LINE:
                if s.end() - s.begin() == 1:
                    if forward:
                        if s.b < s.a:
                            new_sels.append(sublime.Region(s.b, s.a))
                        else:
                            new_sels.append(s)
                    else:
                        if s.b > s.a:
                            new_sels.append(sublime.Region(s.b, s.a))
                        else:
                            new_sels.append(s)
                else:
                    new_sels.append(s)

            else:
                if forward:
                    if self.view.full_line(s.b).a == s.b and self.view.full_line(s.b).b == s.a:
                        new_sels.append(sublime.Region(s.b, s.a))
                    else:
                        new_sels.append(s)
                elif self.view.full_line(s.b - 1).a == s.a and self.view.full_line(s.b - 1).b == s.b:
                    r = sublime.Region(self.view.full_line(s.a).b, s.a)
                    new_sels.append(r)
                else:
                    new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class VisualClipEndToEol(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if s.a < s.b:
                # going forward
                if utils.is_at_hard_eol(self.view, s) and \
                   not utils.visual_is_on_empty_line_forward(self.view, s):
                        new_sels.append(utils.back_end_one_char(s))
                else:
                    new_sels.append(s)
            else:
                # Moving down by lines.
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class VisualClipEndToBol(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []

        for s in sels:
            if utils.is_at_eol(self.view, s):
                w_sels.append(utils.forward_end_one_char(s))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class VisualDontOvershootLineRight(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []

        for s in sels:
            if (not utils.is_region_reversed(self.view, s) and
                (utils.visual_is_end_at_bol(self.view, s) or
                 utils.visual_is_on_empty_line_forward(self.view, s)) and

                 not s.b == self.view.size()):
                    new_sels.append(utils.back_end_one_char(s))
            # Reversed selection. We are at BOL one LINE down, so
            # go back one CHARACTER.
            # FIXME: We need ST to compare regions or improve this.
            elif (utils.is_region_reversed(self.view, s) and
                  not utils.is_same_line(self.view, s.b - 1, s.b)):
                        new_sels.append(utils.back_end_one_char(s))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class VisualDontOvershootLineLeft(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []

        for s in sels:
            if (s.a > s.b and
                utils.is_at_eol(self.view, s) and
                not s.b == 0):
                    new_sels.append(utils.forward_end_one_char(s))
            elif (s.a < s.b and
                  utils.is_at_hard_eol(self.view, s)):
                    new_sels.append(sublime.Region(s.a, s.b + 1))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class VisualShrinkEndOneChar(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []

        for s in sels:
            if (s.a < s.b and not utils.visual_is_on_empty_line_forward(self.view, s) and
               not (utils.visual_is_end_at_bol(self.view, s))):
                    new_sels.append(utils.back_end_one_char(s))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class VisualExtendToFullLine(sublime_plugin.TextCommand):
    def run(self, edit, _internal_mode=None):
        def f(view, s):
            if _internal_mode == _MODE_INTERNAL_VISUAL:
                if s.a <= s.b:
                    if view.line(s.b).a != s.b:
                        return sublime.Region(self.view.full_line(s.b - 1).b,
                                              self.view.line(s.a).a)
                    else:
                        return sublime.Region(self.view.full_line(s.b).b,
                                              self.view.line(s.a).a)
                else:
                    return sublime.Region(self.view.full_line(s.a - 1).b,
                                          self.view.line(s.b).a)
            else:
                return self.view.full_line(s)

        regions_transformer(self.view, f)


class _vi_dd_pre_motion(sublime_plugin.TextCommand):
    def run(self, edit, _internal_mode=None):
        def f(view, s):
            if _internal_mode == _MODE_INTERNAL_VISUAL:
                current_line = view.line(s.b)
                return sublime.Region(current_line.a, current_line.a)
            return s

        regions_transformer(self.view, f)


class _vi_dd_post_motion(sublime_plugin.TextCommand):
    def run(self, edit, _internal_mode=None):
        def f(view, s):
            if view.substr(s.b - 1) != '\n':
                return sublime.Region(s.a, view.full_line(s.b).b)
            return s

        regions_transformer(self.view, f)


class VisualExtendToLine(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []

        for s in sels:
            new_sels.append(self.view.line(s))

        for s in new_sels:
            self.view.sel().add(s)


class ViReorientCaret(sublime_plugin.TextCommand):
    # XXX: Dead code.
    def run(self, edit, mode=None, _internal_mode=None):
        if mode != MODE_VISUAL_LINE:
            return

        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []

        for s in sels:
            if s.a <= s.b:
                new_sels.append(self.view.full_line(s))
            else:
                new_sels.append(self.view.full_line(s))

        for s in new_sels:
            self.view.sel().add(s)


class VisualExtendToBol(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        if mode != MODE_VISUAL_LINE:
            return

        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []

        for s in sels:
            if s.a < s.b and (self.view.line(s.a) == self.view.line(s.b)):
                r = sublime.Region(self.view.full_line(s.b).b, s.a)
                new_sels.append(r)
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class VisualExtendEndToHardEnd(sublime_plugin.TextCommand):
    def run(self, edit, mode=None):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []

        for s in sels:
            if s.a < s.b:
                # TODO: Wait until regions can compare themselves neatly.
                if (self.view.line(s.b).a == self.view.line(s.b -1).a and
                    self.view.line(s.b).b == self.view.line(s.b -1).b):
                    new_sels.append(sublime.Region(s.a, self.view.full_line(s.b).b))
                else:
                    new_sels.append(s)
            else:
                if self.view.line(s.b).a != s.b:
                    r = sublime.Region(s.a, self.view.full_line(s.b).a)
                    new_sels.append(r)
                else:
                    new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class _vi_w_post_every_motion(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        def f(view, s):
            state = VintageState(view)

            if state.mode == MODE_NORMAL:
                if view.substr(s.b) == '\n':
                    if not view.line(s.b).empty():
                        r = sublime.Region(s.b + 1, s.b + 1)
                        pt = utils.next_non_white_space_char(view, r.b, white_space='\t ')
                        return sublime.Region(pt, pt)

            if state.mode == MODE_VISUAL:
                # FIXME: Moving from EMPTYLINE to NONEMPTYLINE should select FIRSTCHAR on NEXTLINE
                # only, but it selects a WORD and the FIRSTCHAR of the following WORD too.

                # When starting from an empty line, select only the FIRSTCHAR of the FIRSTWORD on
                # NEXTLINE.
                if view.line(s.a) != view.line(s.b):
                    if s.b == view.word(view.line(s.b).a).b + 1 and not ViExecutionState.dont_shrink_word:
                        return sublime.Region(s.a, view.line(s.b).a + 1)
                    else:
                        # Next *w* won't be a special case again.
                        ViExecutionState.reset_word_state()

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

            return s

        regions_transformer(self.view, f)


class _vi_w_pre_motion(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            state = VintageState(view)
            if state.mode == MODE_VISUAL:
                # When issuing *w* from an empty line in visual mode, Vim will select the FIRSTCHAR
                # of the FIRSTWORD on the NEXTLINE. Make sure here that, if that has been the case
                # before this command, the post_every_motion hook won't get confused and fail to
                # advance one word.
                if view.line(s.b).a + 1 == s.b:
                    if view.substr(s.b) not in ('\t '):
                        ViExecutionState.dont_shrink_word = True
            return s

        regions_transformer(self.view, f)


class _vi_w_pre_every_motion(sublime_plugin.TextCommand):
    def run(self, edit, current_iteration=None, total_iterations=None):
        def f(view, s):
            state = VintageState(view)
            if state.mode == MODE_VISUAL:
                if view.substr(s.b - 1) != '\n':
                    # Ensures that we don't skip over WORDS of length 1.
                    return sublime.Region(s.a, s.b - 1)
            return s

        regions_transformer(self.view, f)


class _d_w_post_every_motion(sublime_plugin.TextCommand):
    """Assumes we are in _MODE_INTERNAL_VISUAL.

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


class _back_one_if_on_hard_eol(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if (s.a < s.b and
                self.view.full_line(s.b - 1).b == s.b):
                    new_sels.append(sublime.Region(s.a, s.b - 1))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class _extend_b_to_hard_eol(sublime_plugin.TextCommand):
    """Ensures that all selections encompass the following new line character.

       Use only for CHARACTERWISE VISUAL MODE or equivalent.
    """
    def run(self, edit, **kwargs):
        def f(view, s):
            # Consider 2d$. This command should delete two lines and this class helps with that.
            # In some cases, though, we can't possibly know whether .b is at SOMELINE HARDEOL
            # or at SOMELINE HARDBOL. For example, if .b is at CURRENTLINE HARDEOL and NEXTLINE is
            # shorter, 2d$ may cause the caret to land at NEXTLINE HARDEOL, which is the same
            # point as HARDBOL two lines down. In such case, we don't need to extend .b to
            # HARDEOL, but with the available data to this function, we can't know that.
            #
            # For now, we'll consider the example above as an exception and let Vintageous do the
            # wrong thing. It's more important that the command mentioned above works well when
            # the caret is in the middle of a line or at HARDBOL.
            state = VintageState(view)

            if state.mode == MODE_VISUAL:
                if s.a < s.b and not view.line(s.b - 1).empty():
                    hard_eol = self.view.full_line(s.b - 1).b
                    return sublime.Region(s.a, hard_eol)

            elif state.mode == MODE_NORMAL:
                pass

            return s

        regions_transformer(self.view, f)


class _pre_every_dollar(sublime_plugin.TextCommand):
    def run(self, edit, current_iteration, total_iterations):
        def f(view, s):
            state = VintageState(view)

            if state.mode == MODE_NORMAL:
                pass
            return s

        regions_transformer(self.view, f)


class _extend_a_to_bol_if_leading_white_space(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if (s.a <= s.b and
                self.view.substr(sublime.Region(self.view.line(s.a).a, s.a)).isspace()):
                    bol = self.view.line(s.a).a
                    new_sels.append(sublime.Region(bol, s.b))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class _vi_e_post_every_motion(sublime_plugin.TextCommand):
    """Use only with ``vi_e``.

        Ensures that the caret ends up at a WORDEND and that it wraps around the new line
        character as needed.

        Works in ANYMODE (except VISUALLINE).
    """
    def run(self, edit, current_iteration=None, total_iterations=None,
            mode=None, _internal_mode=None):
        def f(view, s):
            is_last_iteration = (current_iteration == total_iterations - 1)

            if _internal_mode == _MODE_INTERNAL_VISUAL:
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


# TODO: Move this to somewhere where it's easy to import from and use it for transformers.
def regions_transformer(view, f):
    """Applies ``f`` to every selection region in ``view`` and replaces the existing selections.
    """
    sels = list(view.sel())
    view.sel().clear()

    new_sels = []
    for s in sels:
        new_sels.append(f(view, s))

    for s in new_sels:
        view.sel().add(s)


class _vi_e_pre_motion(sublime_plugin.TextCommand):
    """Use only with ``vi_e``.

        Ensures that the caret moves to the next WORDEND instead on remaining on the current word.

        Works in ANYMODE (except VISUALLINE).
    """
    def run(self, edit, mode, _internal_mode):
        def f(view, s):
            if mode == MODE_NORMAL:
                    # What to do if we are not on a white space character...
                    if view.substr(s.b) not in '\t ':
                        # Advance one so that the caret moves as expected instead of remaining on
                        # the same word when the motion executes.
                        if not utils._is_on_eol(view, s, mode, _internal_mode):
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
    def run(self, edit, mode, _internal_mode, current_iteration, total_iterations):
        def f(view, s):
            delta = 1
            if mode == MODE_VISUAL:
                delta = 1 if utils.is_region_reversed(view, s) else 2

            text_before_caret = view.substr(sublime.Region(view.line(s.b).a, s.b - delta))
            first_char_is_space = view.substr(s.b - delta).isspace() if (view.line(s.b).a == s.b - delta) else False

            if mode == MODE_NORMAL:
                if text_before_caret.isspace() or first_char_is_space:
                    pt = utils.previous_non_white_space_char(self.view, s.b - 1, white_space='\t ')
                    if view.line(pt).empty():
                        return sublime.Region(s.a , pt + 1)
                    elif view.word(pt).size() == 1:
                        return sublime.Region(pt + 1, pt + 1)

                    return sublime.Region(pt, pt)

                # At BOL.
                # XXX: Use a general function instead of spelling out the computation.
                elif view.line(s.b).a == s.b and not view.line(s.b - 1).empty():
                    return sublime.Region(s.b - 1, s.b - 1)

            elif mode == MODE_VISUAL:
                if utils.is_region_reversed(view, s):

                    if text_before_caret.isspace() or first_char_is_space:
                        pt = utils.previous_non_white_space_char(self.view, s.b - delta, white_space='\t ')
                        # PREVIOUSLINE empty; don't go past it.
                        if view.line(pt).empty():
                            return sublime.Region(s.a , pt + 1)
                        return sublime.Region(s.a, pt)

                    elif utils.is_at_bol(view, s) and not view.line(s.b - 1).empty():
                        # Single-character words are a special case; we don't want to skip over
                        # them.
                        if view.word(s.b - 1).size() > 1:
                            return sublime.Region(s.a, s.b - 1)

                else:
                    # Non-reversed region. Note that .b here is at NEXTCHAR, not CURRENTCHAR.
                    if text_before_caret.isspace() or first_char_is_space:
                        pt = utils.previous_non_white_space_char(self.view, s.b - delta, white_space='\t ')
                        if view.line(pt).empty():
                            return sublime.Region(s.a , pt + 1)
                        # XXX: I don't think this branch is necessary.
                        # On new WORD; make sure motion doesn't skip it.
                        elif view.substr(pt) not in ('\t \n'):
                            return sublime.Region(s.a, pt + 1)

                        return sublime.Region(s.a, pt)

                    # At WORDBEGIN or at any non-ALPHANUMERICCHAR.
                    elif (view.word(s.b - 1).a == s.b - 1) or not view.substr(s.b - 1).isalnum():
                        return sublime.Region(s.a, s.b - 1)

            return s

        regions_transformer(self.view, f)


class _vi_b_post_every_motion(sublime_plugin.TextCommand):
    """Use only with for vi_b.
    """
    def run(self, edit, mode, _internal_mode, current_iteration, total_iterations):
        def f(view, s):
            if mode == MODE_VISUAL:
                # Vim selects the FIRSTCHAR of NEXTWORD when moving backward in VISUAL mode.
                if not utils.is_region_reversed(self.view, s):
                    return sublime.Region(s.a, s.b + 1)

            return s

        regions_transformer(self.view, f)


class _vi_underscore_pre_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, _internal_mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                line = view.line(s.b)
                return sublime.Region(line.a, line.a)
            return s

        regions_transformer(self.view, f)


class _vi_underscore_post_motion(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, _internal_mode=None, extend=False):
        def f(view, s):
            if mode == MODE_NORMAL:
                pt = utils.next_non_white_space_char(view, s.b)
                return sublime.Region(pt, pt)
            elif mode == MODE_VISUAL:
                line = view.line(s.b - 1)
                pt = utils.next_non_white_space_char(view, line.a)
                return sublime.Region(s.a, pt + 1)
            return s

        regions_transformer(self.view, f)


class _vi_j_pre_motion(sublime_plugin.TextCommand):
    # Assume NORMAL_MODE / _MODE_INTERNAL_VISUAL
    # This code is probably duplicated.
    def run(self, edit):
        def run(view, s):
            line = view.line(s.b)
            return sublime.Region(line.a, line.a)

        regions_transformer(self.view, f)
