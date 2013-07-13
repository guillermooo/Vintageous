import unittest

from Vintageous.test_runner import TestsState
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL

import sublime


def set_text(view, text):
    view.run_command('write_to_buffer', {'text': text, 'file_name': view.file_name()})


def add_selection(view, a=0, b=0):
    view.sel().add(sublime.Region(a, b))


def get_sel(view, num):
    return view.sel()[num]


def first_sel(view):
    return get_sel(view, 0)


class TestSetAction(unittest.TestCase):
    def setUp(self):
        TestsState.reset_view_state()

    def testCanSetAction(self):
        TestsState.view.run_command('set_action', {'action': 'vi_d'})
        actual = TestsState.view.settings().get('vintage')['action']
        self.assertEqual('vi_d', actual)


class TestSetMotion(unittest.TestCase):
    def setUp(self):
        TestsState.reset_view_state()

    @unittest.skip("Can't set motion because will be run straight away.")
    # TODO: Mock .eval() so it does not reset the state.
    def testCanSetMotion(self):
        TestsState.view.run_command('set_motion', {'motion': 'vi_l'})
        actual = TestsState.view.settings().get('vintage')['motion']
        self.assertEqual('vi_l', actual)


class BufferTest(unittest.TestCase):
    def setUp(self):
        TestsState.reset_view_state()
        self.view = TestsState.view
        self.view.sel().clear()
        self.R = sublime.Region


class Test_vi_l(BufferTest):
    def testCanMoveInNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l_motion', {'mode': MODE_NORMAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(1, 1), first_sel(self.view))

    def testCanMoveInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l_motion', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(0, 1), self.view.sel()[0])

    def testCanMoveInNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l_motion', {'mode': MODE_NORMAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(10, 10), self.view.sel()[0])

    def testCanMoveInInternalNormalModeWithCount(self):
        set_text(self.view, 'foo bar baz')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l_motion', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(0, 10), self.view.sel()[0])

    def testCanMoveInVisualMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=1)

        self.view.run_command('_vi_l_motion', {'mode': MODE_VISUAL, 'count': 1, 'extend': False})
        self.assertEqual(self.R(0, 2), first_sel(self.view))

    def testCanMoveInVisualModeWithCount(self):
        set_text(self.view, 'foo bar fuzz buzz')
        add_selection(self.view, a=0, b=1)

        self.view.run_command('_vi_l_motion', {'mode': MODE_VISUAL, 'count': 10, 'extend': False})
        self.assertEqual(self.R(0, 11), first_sel(self.view))

    def testStopsAtRightEndInNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l_motion', {'mode': MODE_NORMAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(2, 2), first_sel(self.view))

    def testStopsAtRightEndInVisualMode(self):
        set_text(self.view, 'abc\n')
        add_selection(self.view, a=0, b=1)

        self.view.run_command('_vi_l_motion', {'mode': MODE_VISUAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(0, 4), first_sel(self.view))

    def testStopsAtRightEndInInternalNormalMode(self):
        set_text(self.view, 'abc')
        add_selection(self.view, a=0, b=0)

        self.view.run_command('_vi_l_motion', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10000, 'extend': False})
        self.assertEqual(self.R(0, 3), first_sel(self.view))
