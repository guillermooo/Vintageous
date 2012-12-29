import sublime
import sublime_plugin

from Vintageous.vi.constants import regions_transformer
from Vintageous.vi.constants import MODE_VISUAL, MODE_NORMAL, _MODE_INTERNAL_VISUAL
from Vintageous.vintageous import VintageState


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


class ViFindInLineInclusive(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, character=None, _internal_mode=None):
        def f(view, s):
            line_text = view.substr(sublime.Region(s.b + 1, view.line(s.b).b))
            offset = s.b + 1 - view.line(s.b).a

            try:
                where = line_text.index(character)
            except ValueError:
                where = -1

            if where > -1:
                pt = view.line(s.b).a + where + offset

                state = VintageState(view)
                if state.mode == MODE_VISUAL or _internal_mode == _MODE_INTERNAL_VISUAL:
                    return sublime.Region(s.a, pt + 1)

                return sublime.Region(pt, pt)

            return s

        regions_transformer(self.view, f)


class ViFindInLineExclusive(sublime_plugin.TextCommand):
    """Contrary to *f*, *t* does not look past the caret's position, so if ``character`` is under
       the caret, nothing happens.
    """
    def run(self, edit, extend=False, character=None, _internal_mode=None):
        def f(view, s):
            line_text = view.substr(sublime.Region(s.b, view.line(s.b).b))
            offset = s.b - view.line(s.b).a

            try:
                where = line_text.index(character)
            except ValueError:
                where = -1

            if where > -1:
                pt = (view.line(s.b).a + where + offset)

                state = VintageState(view)
                # TODO: Handling modes via global state seems to be the right thing to do. Perhaps
                # _MODE_INTERNAL_VISUAL could become a first-class mode. We know anyway that it's
                # equivalent to MODE_NORMAL, so the necessary post processing can alway be done
                # to ensure that we end up in MODE_NORMAL after the command.
                if state.mode == MODE_VISUAL or _internal_mode == _MODE_INTERNAL_VISUAL:
                    return sublime.Region(s.a, pt)
                return sublime.Region(pt - 1, pt - 1)

            return s

        regions_transformer(self.view, f)
