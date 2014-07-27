import sublime
import unittest

from Vintageous.state import State


class ViewTest(unittest.TestCase):
    """
    New-style tests.
    """

    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.set_scratch(True)

    @property
    def state(self):
        return State(self.view)

    def clear_sel(self):
        self.view.sel().clear()

    def create(self, text=''):
        if text:
            set_text(self.view, text)

    def write(self, text):
        if not self.view:
            raise TypeError('no view available yet')
        set_text(self.view, text)

    def R(self, a, b=None):
        return make_region(self.view, a, b)

    def get_all_text(self):
        return self.view.substr(self.R(0, self.view.size()))

    def erase_all(self):
        self.view.run_command('__vi_tests_erase_buffer_content', {})

    def add_sel(self, a=0, b=0):
        if not self.view:
            raise TypeError('no view available yet')
        add_sel(self.view, a , b)

    def second_sel(self):
        return second_sel(self.view)

    def first_sel(self):
        return first_sel(self.view)

    def tearDown(self):
        if self.view:
            self.view.close()

    def assert_equal_regions(self, expected_region, actual_region, msg=''):
        """Tests that @expected_region and @actual_region cover the exact same
        region. Does not take region orientation into account.
        """
        if (expected_region.size() == 1) and (actual_region.size() == 1):
            expected_region = make_region(self.view, expected_region.begin(),
                                          expected_region.end())
            actual_region = make_region(self.view, actual_region.begin(),
                                        actual_region.end())
        self.assertEqual(expected_region, actual_region, msg)


def make_region(view, a, b=None):
    try:
        pt_a = view.text_point(*a)
        pt_b = view.text_point(*b)
        return sublime.Region(pt_a, pt_b)
    except (TypeError, ValueError):
        pass

    if isinstance(a, int) and b is None:
        pass
    elif not (isinstance(a, int) and isinstance(b, int)):
        raise ValueError("a and b parameters must be either ints or (row, col)")

    if b is not None:
        return sublime.Region(a, b)
    else:
        return sublime.Region(a)


def region2rowcols(view, reg):
    '''Takes a view and a region. Returns a pair of row-col tuples
    corresponding to the region's start and end points.'''
    points = (reg.begin(), reg.end())
    return list(map(view.rowcol, points))


def set_text(view, text):
    view.run_command('__vi_tests_write_buffer', {'text': text})


def add_sel(view, a=0, b=0):
    if isinstance(a, sublime.Region):
        view.sel().add(a)
        return
    view.sel().add(sublime.Region(a, b))


def get_sel(view, num):
    return view.sel()[num]


def first_sel(view):
    return get_sel(view, 0)


def second_sel(view):
    return get_sel(view, 1)


