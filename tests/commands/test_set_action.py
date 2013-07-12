import unittest

from Vintageous.test_runner import TestsState
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL

import sublime


def set_buffer_text(view, text):
    view.run_command('write_to_buffer', {'text': text, 'file_name': view.file_name()})


def pos(a=0, b=0):
    TestsState.view.sel().clear()
    TestsState.view.sel().add(sublime.Region(a, b))


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


class Test_vi_l(unittest.TestCase):
    def setUp(self):
        TestsState.reset_view_state()

    def testCanMoveInNormalMode(self):
        set_buffer_text(TestsState.view, 'abc')
        pos()

        TestsState.view.run_command('_vi_l_motion', {'mode': MODE_NORMAL, 'count': 1, 'extend': False})
        self.assertEqual(sublime.Region(1, 1), TestsState.view.sel()[0])

    def testCanMoveInNormalModeWithCount(self):
        set_buffer_text(TestsState.view, 'foo bar baz')
        pos()

        TestsState.view.run_command('_vi_l_motion', {'mode': MODE_NORMAL, 'count': 10, 'extend': False})
        self.assertEqual(sublime.Region(10, 10), TestsState.view.sel()[0])

    def testCanMoveInVisualMode(self):
        set_buffer_text(TestsState.view, 'abc')
        pos()

        # TODO: Encapsulate this.
        sel_start = TestsState.view.sel()[0].b + 1
        TestsState.view.sel().clear()
        TestsState.view.sel().add(sublime.Region(sel_start - 1, sel_start))

        TestsState.view.run_command('_vi_l_motion', {'mode': MODE_VISUAL, 'count': 1, 'extend': False})
        self.assertEqual(sublime.Region(sel_start - 1, sel_start + 1), TestsState.view.sel()[0])

    def testStopsAtRightEndInNormalMode(self):
        set_buffer_text(TestsState.view, 'abc')
        pos()
        end = TestsState.view.line(TestsState.view.sel()[0].b).b - 1
        expected = end

        TestsState.view.run_command('_vi_l_motion', {'mode': MODE_NORMAL, 'count': 10000, 'extend': False})
        self.assertEqual(TestsState.view.sel()[0], sublime.Region(2, 2))

    def testStopsAtRightEndInVisualMode(self):
        set_buffer_text(TestsState.view, 'abc\n')
        pos()
        end = TestsState.view.line(TestsState.view.sel()[0].b).b - 1
        expected = end

        # TODO: Encapsulate this.
        sel_start = TestsState.view.sel()[0].b + 1
        TestsState.view.sel().clear()
        TestsState.view.sel().add(sublime.Region(sel_start - 1, sel_start))

        TestsState.view.run_command('_vi_l_motion', {'mode': MODE_VISUAL, 'count': 10000, 'extend': False})
        self.assertEqual(TestsState.view.sel()[0], sublime.Region(0, 4))
