import unittest

import sublime

from Vintageous.tests import ViewTest
from Vintageous.vi import marks
from Vintageous.state import State
from Vintageous.tests import make_region
from Vintageous.tests import set_text
from Vintageous.tests import add_sel


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


class MarksTests(ViewTest):
    def setUp(self):
        super().setUp()
        marks._MARKS = {}
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, 0))
        self.marks = State(self.view).marks

    def testCanSetMark(self):
        self.marks.add('a', self.view)
        expected_win, expected_view, expected_region = (self.view.window(), self.view, (0, 0))
        actual_win, actual_view, actual_region = marks._MARKS['a']
        self.assertEqual((actual_win.id(), actual_view.view_id, actual_region),
                         (expected_win.id(), expected_view.view_id, expected_region))

    def testCanRetrieveMarkInTheCurrentBufferAsTuple(self):
        self.marks.add('a', self.view)
        # The caret's at the beginning of the buffer.
        self.assertEqual(self.marks.get_as_encoded_address('a'), sublime.Region(0, 0))

    def testCanRetrieveMarkInTheCurrentBufferAsTuple2(self):
        set_text(self.view, ''.join(('foo bar\n') * 10))
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(30, 30))
        self.marks.add('a', self.view)
        self.assertEqual(self.marks.get_as_encoded_address('a'), sublime.Region(24, 24))

    def testCanRetrieveMarkInADifferentBufferAsEncodedMark(self):
        view = View(id_=self.view.view_id + 1, fname=r'C:\foo.txt')

        marks._MARKS['a'] = (Window(), view, (0, 0))
        expected = "{0}:{1}".format(r'C:\foo.txt', "0:0")
        self.assertEqual(self.marks.get_as_encoded_address('a'), expected)

    def testCanRetrieveMarkInAnUntitledBufferAsEncodedMark(self):
        view = View(id_=self.view.view_id + 1, fname='', buffer_id=999)

        marks._MARKS['a'] = (Window(), view, (0, 0))
        expected = "<untitled {0}>:{1}".format(999, "0:0")
        self.assertEqual(self.marks.get_as_encoded_address('a'), expected)

    def testCanRetrieveSingleQuoteMark(self):
        location = self.marks.get_as_encoded_address("'")
        self.assertEqual(location, '<command _vi_double_single_quote>')
