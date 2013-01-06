import sublime
import sublime_plugin

from Vintageous.vi.constants import regions_transformer
from Vintageous.vi.constants import MODE_VISUAL, MODE_NORMAL, _MODE_INTERNAL_VISUAL
from Vintageous.state import VintageState


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
    def run(self, edit, extend=False, character=None, _internal_mode=None, count=1):
        def f(view, s):
            offset = s.b + 1 - view.line(s.b).a
            a, eol = s.b + 1, view.line(s.b).b
            final_offset = -1

            try:
                for i in range(count):
                    line_text = view.substr(sublime.Region(a, eol))
                    match_in_line = line_text.index(character)

                    final_offset = offset + match_in_line

                    a = view.line(s.a).a + final_offset + 1
                    offset += match_in_line + 1
            except ValueError:
                pass

            if final_offset > -1:
                pt = view.line(s.b).a + final_offset

                state = VintageState(view)
                if state.mode == MODE_VISUAL or _internal_mode == _MODE_INTERNAL_VISUAL:
                    return sublime.Region(s.a, pt + 1)

                return sublime.Region(pt, pt)

            return s

        regions_transformer(self.view, f)


# FIXME: Only find exact char counts. Vim ignores the command when the count is larger than the
# number of instances of the sought character.
class ViReverseFindInLineInclusive(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, character=None, _internal_mode=None, count=1):
        def f(view, s):
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
                if state.mode == MODE_VISUAL or _internal_mode == _MODE_INTERNAL_VISUAL:
                    return sublime.Region(s.a, pt)

                return sublime.Region(pt, pt)

            return s

        regions_transformer(self.view, f)


class ViFindInLineExclusive(sublime_plugin.TextCommand):
    """Contrary to *f*, *t* does not look past the caret's position, so if ``character`` is under
       the caret, nothing happens.
    """
    def run(self, edit, extend=False, character=None, _internal_mode=None, count=1):
        def f(view, s):
            offset = s.b + 1 - view.line(s.b).a
            a, eol = s.b + 1, view.line(s.b).b
            final_offset = -1

            try:
                for i in range(count):
                    line_text = view.substr(sublime.Region(a, eol))
                    match_in_line = line_text.index(character)

                    final_offset = offset + match_in_line

                    a = view.line(s.a).a + final_offset + 1
                    offset += match_in_line + 1
            except ValueError:
                pass

            if final_offset > -1:
                pt = view.line(s.b).a + final_offset

                # TODO: Handling modes via global state seems to be the right thing to do. Perhaps
                # _MODE_INTERNAL_VISUAL could become a first-class mode. We know anyway that it's
                # equivalent to MODE_NORMAL, so the necessary post processing can alway be done
                # to ensure that we end up in MODE_NORMAL after the command.
                state = VintageState(view)
                if state.mode == MODE_VISUAL or _internal_mode == _MODE_INTERNAL_VISUAL:
                    return sublime.Region(s.a, pt)

                return sublime.Region(pt - 1, pt - 1)

            return s

        regions_transformer(self.view, f)


class ViReverseFindInLineExclusive(sublime_plugin.TextCommand):
    """Contrary to *F*, *T* does not look past the caret's position, so if ``character`` is right
       before the caret, nothing happens.
    """
    def run(self, edit, extend=False, character=None, _internal_mode=None, count=1):
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
                if state.mode == MODE_VISUAL or _internal_mode == _MODE_INTERNAL_VISUAL:
                    return sublime.Region(s.a, pt + 1)

                return sublime.Region(pt + 1, pt + 1)

            return s

        regions_transformer(self.view, f)


class ViGoToLine(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, line=None):
        line = line if line > 0 else 1
        dest = self.view.text_point(line - 1, 0)

        def f(view, s):
            if not extend:
                return sublime.Region(dest, dest)
            else:
                return sublime.Region(s.a, dest)

        regions_transformer(self.view, f)

        # FIXME: Bringing the selections into view will be undesirable in many cases. Maybe we
        # should have an optional .scroll_selections_into_view() step during command execution.
        self.view.show(self.view.sel()[0])


class ViPercent(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, percent=None):
        if percent == None:
            return

        row = self.view.rowcol(self.view.size())[0] * (percent / 100)

        def f(view, s):
            pt = view.text_point(row, 0)
            return sublime.Region(pt, pt)

        regions_transformer(self.view, f)

        # FIXME: Bringing the selections into view will be undesirable in many cases. Maybe we
        # should have an optional .scroll_selections_into_view() step during command execution.
        self.view.show(self.view.sel()[0])
