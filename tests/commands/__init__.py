import sublime
import unittest

from Vintageous.test_runner import TestsState


class BufferTest(unittest.TestCase):
    def setUp(self):
        TestsState.reset_view_state()
        self.view = TestsState.view
        self.view.sel().clear()
        self.R = sublime.Region


def set_text(view, text):
    view.run_command('write_to_buffer', {'text': text, 'file_name': view.file_name()})


def add_selection(view, a=0, b=0):
    view.sel().add(sublime.Region(a, b))


def get_sel(view, num):
    return view.sel()[num]


def first_sel(view):
    return get_sel(view, 0)
