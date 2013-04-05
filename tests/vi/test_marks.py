import unittest

import sublime

from Vintageous.test_runner import TestsState
from Vintageous.vi import marks
from Vintageous.state import VintageState


# XXX: Use the mock module instead?
##################################################
class View(object):
    def __init__(self, id_, fname, buffer_id=0):
        self.view_id = id_
        self.fname = fname
        self._buffer_id = buffer_id

    def file_name(self):
        return self.fname

    def buffer_id(self):
        return self._buffer_id

class Window(object):
    pass
##################################################


class MarksTests(unittest.TestCase):
    def setUp(self):
        marks._MARKS = {}
        TestsState.view.sel().clear()
        TestsState.view.sel().add(sublime.Region(0, 0))
        self.marks = VintageState(TestsState.view).marks

    def testCanSetMark(self):
        self.marks.add('a', TestsState.view)
        expected_win, expected_view, expected_region = (TestsState.view.window(), TestsState.view, (0, 0))
        actual_win, actual_view, actual_region = marks._MARKS['a']
        self.assertEqual((actual_win.id(), actual_view.view_id, actual_region),
                         (expected_win.id(), expected_view.view_id, expected_region))

    def testCanRetrieveMarkInTheCurrentBufferAsTuple(self):
        self.marks.add('a', TestsState.view)
        # The caret's at the beginning of the buffer.
        self.assertEqual(self.marks.get_as_encoded_address('a'), sublime.Region(0, 0))

    def testCanRetrieveMarkInTheCurrentBufferAsTuple2(self):
        TestsState.view.sel().clear()
        TestsState.view.sel().add(sublime.Region(100, 100))
        self.marks.add('a', TestsState.view)
        self.assertEqual(self.marks.get_as_encoded_address('a'), sublime.Region(100, 100))

    def testCanRetrieveMarkInADifferentBufferAsEncodedMark(self):
        view = View(id_=TestsState.view.view_id + 1, fname=r'C:\foo.txt')

        marks._MARKS['a'] = (Window(), view, (0, 0))
        expected = "{0}:{1}".format(r'C:\foo.txt', "0:0")
        self.assertEqual(self.marks.get_as_encoded_address('a'), expected)

    def testCanRetrieveMarkInAnUntitledBufferAsEncodedMark(self):
        view = View(id_=TestsState.view.view_id + 1, fname='', buffer_id=999)

        marks._MARKS['a'] = (Window(), view, (0, 0))
        expected = "<untitled {0}>:{1}".format(999, "0:0")
        self.assertEqual(self.marks.get_as_encoded_address('a'), expected)

    def testCanRetrieveSingleQuoteMark(self):
        location = self.marks.get_as_encoded_address("'")
        self.assertEqual(location, '<command _vi_double_single_quote>')
