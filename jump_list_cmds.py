"""Adds jump list functionality.

   Wraps Sublime Text's own jump list.
"""


import sublime
import sublime_plugin

from Default.history_list import get_jump_history

from Vintageous.state import VintageState
from Vintageous.vi.jump_list import JumpList



class ViAddToJumpList(sublime_plugin.WindowCommand):
    def run(self):
        get_jump_history(self.window.id()).push_selection(self.window.active_view())
