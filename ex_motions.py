import sublime
import sublime_plugin

class _vi_cmd_line_a(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(1))
