import sublime
import unittest

from Vintageous.test_runner import TestsState


class BufferTest(unittest.TestCase):
    def setUp(self):
        TestsState.reset_view_state()
        self.view = TestsState.view
        self.view.sel().clear()

    def R(self, a, b):
        return make_region(self.view, a, b)


def make_region_at_row(view, row=0, col=0, size=0):
    pt = view.text_point(row, col)
    return sublime.Region(pt, pt + size)


def make_region(view, a, b):
    try:
        pt_a = view.text_point(*a)
        pt_b = view.text_point(*b)
        return sublime.Region(pt_a, pt_b)
    except (TypeError, ValueError):
        pass

    if (isinstance(a, int) and isinstance(b, int)):
        return sublime.Region(a, b)
    raise ValueError("a and b parameters must be either ints or (row, col)")


def set_text(view, text):
    view.run_command('write_to_buffer', {'text': text, 'file_name': view.file_name()})


def add_selection(view, a=0, b=0):
    if isinstance(a, sublime.Region):
        view.sel().add(a)
        return
    view.sel().add(sublime.Region(a, b))


def get_sel(view, num):
    return view.sel()[num]


def first_sel(view):
    return get_sel(view, 0)
