import unittest

import sublime

from Vintageous.test_runner import TestsState
from Vintageous.vi import marks
from Vintageous.vi.settings import SettingsManager


class MarksTests(unittest.TestCase):
    def setUp(self):
        self.marks = marks.Marks()

    def testCanSetMark(self):
        self.marks.mark('a', TestsState.view)
        expected = (TestsState.view.window(), TestsState.view, (0, 0))
        self.assertEqual(self.marks['a'], expected)

    def testCanRetrieveEncodedMark(self):
        self.marks.mark('a', TestsState.view)
        expected = "{0}:{1}".format(TestsState.view.file_name(), "0:0")
        self.assertEqual(self.marks.mark_as_encoded_address('a'), expected)
