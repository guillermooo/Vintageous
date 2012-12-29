import sublime
import sublime_plugin

from Vintageous.vi.utils import (is_at_eol, is_at_hard_eol, is_at_bol,
                      back_one_char, forward_one_char, is_line_empty,
                      is_on_empty_line,)


class ClipEndToLine(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if not is_on_empty_line(self.view, s) and is_at_eol(self.view, s):
                new_sels.append(back_one_char(s))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class DontStayOnEolForward(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if is_at_eol(self.view, s):
                new_sels.append(forward_one_char(s))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class DontStayOnEolBackward(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if is_at_eol(self.view, s) and not self.view.line(s.b).empty():
                new_sels.append(back_one_char(s))
            else:
                new_sels.append(s)

        for s in new_sels:
            self.view.sel().add(s)


class DontOvershootLineRight(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if is_on_empty_line(self.view, s):
                new_sels.append(back_one_char(s))
            if is_at_eol(self.view, s):
                new_sels.append(back_one_char(s))
            elif is_at_bol(self.view, s):
                new_sels.append(back_one_char(s))
            else:
                new_sels.append(s)

        for s in new_sels:
            pass
            self.view.sel().add(s)


class DontOvershootLineLeft(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            if is_at_eol(self.view, s):
                new_sels.append(forward_one_char(s))
            else:
                new_sels.append(s)

        for s in new_sels:
            pass
            self.view.sel().add(s)
