import sublime
import sublime_plugin

from Vintageous.state import VintageState
from Vintageous.vi.jump_list import JumpList


class ViAddToJumpList(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        jump_list = JumpList(state)

        file_name = self.view.file_name()
        # TODO: Unsaved files won't track jumps at the moment.
        if not file_name:
            return

        s = self.view.sel()[0]
        row = self.view.rowcol(s.b)[0]
        # TODO: We need to work on storing the shape of the selection, although I'm not sure
        # whether Vim does this either.
        length = 0

        jump_list.add([file_name, row, length])


class ViNextJump(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        jump_list = JumpList(state)

        file_name, row, length = jump_list.next

        for v in self.view.window().views():
            if v.file_name() == file_name:
                self.view.window().focus_view(v)

        pt = v.text_point(row, 0)

        v.sel().clear()
        self.view.sel().add(sublime.Region(pt, pt))


class ViLatestJump(sublime_plugin.TextCommand):
    def run(self, edit):
        state = VintageState(self.view)
        jump_list = JumpList(state)

        file_name, row, length = jump_list.latest

        found = None
        for v in self.view.window().views():
            if v.file_name() == file_name:
                found = v
                break

        if not found:
            return

        pt = v.text_point(row, 0)

        v.sel().clear()
        v.sel().add(sublime.Region(pt, pt))

        self.view.window().focus_view(v)
        v.show(pt)
