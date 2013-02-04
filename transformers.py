import sublime
import sublime_plugin

from Vintageous.vi.utils import (is_at_eol, is_at_hard_eol, is_at_bol,
                      back_one_char, forward_one_char, is_line_empty,
                      is_on_empty_line,)
from Vintageous.vi.constants import regions_transformer


class ClipEndToLine(sublime_plugin.TextCommand):
    def run(self, edit):
        def f(view, s):
            if not is_on_empty_line(self.view, s) and is_at_eol(self.view, s):
                return back_one_char(s)
            else:
                return s

        regions_transformer(self.view, f)


class DontStayOnEolForward(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        def f(view, s):
            if is_at_eol(self.view, s):
                return forward_one_char(s)
            else:
                return s

        regions_transformer(self.view, f)


class DontStayOnEolBackward(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        def f(view, s):
            if is_at_eol(self.view, s) and not self.view.line(s.b).empty():
                return back_one_char(s)
            else:
                return s

        regions_transformer(self.view, f)


class DontOvershootLineLeft(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        def f(view, s):
            if view.size() > 0 and is_at_eol(self.view, s):
                return forward_one_char(s)
            else:
                return s

        regions_transformer(self.view, f)